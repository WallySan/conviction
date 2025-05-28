import logging
from typing import Optional, List, Tuple
import spacy
import re
import unicodedata
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from neo4j import GraphDatabase, basic_auth
from neo4j.exceptions import Neo4jError

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tenta carregar modelo spaCy
try:
    nlp = spacy.load("pt_core_news_sm")
except OSError as e:
    logger.error("Modelo 'pt_core_news_sm' não encontrado. Execute: python -m spacy download pt_core_news_sm")
    raise e

# Função de limpeza de texto
def limpar_texto(texto: str) -> str:
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = re.sub(r'[^\w\s;]', '', texto)
    return texto

# Configurações do Neo4j
URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "S3nh@Segura2024"

# FastAPI app
app = FastAPI()

# Modelo para entrada JSON
class EntradaFrases(BaseModel):
    texto: str

class EntradaFrase(BaseModel):
    texto: str

# Classe principal para manipular Neo4j
class Neo4jGraph:
    def __init__(self, uri: str, user: str, password: str):
        try:
            self.driver = GraphDatabase.driver(uri, auth=basic_auth(user, password))
            logger.info("Conectado ao Neo4j")
        except Exception as e:
            logger.error(f"Erro ao conectar ao Neo4j: {e}")
            raise e

    def close(self):
        if self.driver:
            self.driver.close()
            logger.info("Conexão com Neo4j encerrada")

    def criar_relacoes(self, texto: str):
        texto_limpo = limpar_texto(texto)
        frases = [f.strip() for f in texto_limpo.split(';') if f.strip()]

        with self.driver.session() as session:
            for frase in frases:
                relacoes = self._extrair_varias_relacoes(frase)
                if not relacoes:
                    logger.warning(f"Nenhuma relação extraída de: '{frase}'")
                for sujeito, verbo, objeto, negacao in relacoes:
                    try:
                        session.execute_write(
                            self._criar_ou_ajustar_relacao,
                            sujeito, verbo, objeto, negacao
                        )
                        logger.info(f"Relação criada: {sujeito} -{verbo}-> {objeto} (negação={negacao})")
                    except Neo4jError as e:
                        logger.error(f"Erro ao escrever relação no banco: {e}")

    def _extrair_varias_relacoes(self, frase: str) -> List[Tuple[str, str, str, bool]]:
        doc = nlp(frase)
        relacoes = []

        for token in doc:
            if token.pos_ == "VERB":
                sujeito = None
                objeto = None
                verbo = token.lemma_
                negacao = any(child.dep_ == "neg" for child in token.children)

                for child in token.children:
                    if child.dep_ in ("nsubj", "nsubj:pass") and child.pos_ in ("NOUN", "PROPN", "PRON"):
                        sujeito = child.text
                for child in token.children:
                    if child.dep_ in ("obj", "dobj", "iobj") and child.pos_ in ("NOUN", "PROPN", "PRON"):
                        objeto = child.text
                    elif child.dep_ == "obl":
                        objeto = child.text

                if sujeito and objeto:
                    relacoes.append((sujeito, verbo, objeto, negacao))

        return relacoes

    @staticmethod
    def _criar_ou_ajustar_relacao(tx, sujeito, verbo, objeto, negacao):
        ajuste = -1 if negacao else 1
        query = """
        MERGE (a:Node {nome: $sujeito})
        MERGE (b:Node {nome: $objeto})
        MERGE (a)-[r:RELACAO {verbo: $verbo}]->(b)
        ON CREATE SET r.peso = CASE WHEN $ajuste < 0 THEN 0 ELSE 1 END
        ON MATCH SET r.peso = CASE 
            WHEN r.peso + $ajuste < 0 THEN 0
            ELSE r.peso + $ajuste
        END
        RETURN a, r, b
        """
        tx.run(query, sujeito=sujeito, objeto=objeto, verbo=verbo, ajuste=ajuste)

    def buscar_relacoes_por_sujeito(self, sujeito: str) -> List[dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (a:Node {nome: $sujeito})-[r:RELACAO]->(b:Node)
                RETURN a.nome AS sujeito, r.verbo AS verbo, r.peso AS peso, b.nome AS objeto
                """,
                sujeito=sujeito
            )
            return [{"sujeito": record["sujeito"], "verbo": record["verbo"], "peso": record["peso"], "objeto": record["objeto"]} for record in result]


# Instância global
grafo = Neo4jGraph(URI, USER, PASSWORD)


# Rota principal
@app.post("/processar")
async def processar_frases(entrada: EntradaFrases, request: Request):
    logger.info(f"Requisição recebida de {request.client.host}")
    if not entrada.texto or not entrada.texto.strip():
        raise HTTPException(status_code=400, detail="Campo 'texto' está vazio.")
    
    try:
        grafo.criar_relacoes(entrada.texto)
        return {"status": "sucesso", "mensagem": "Frases processadas com sucesso."}
    except Exception as e:
        logger.error(f"Erro no processamento: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar as frases.")


# Novo endpoint para extrair convicções
@app.post("/conviccoes")
async def extrair_conviccoes(entrada: EntradaFrase):
    logger.info("Requisição para extrair convicções recebida")
    try:
        doc = nlp(entrada.texto)
        subjetivos = set()

        # Extrair todos os subjetivos (nomes próprios, substantivos e pronomes)
        for token in doc:
            if token.dep_ in ("nsubj", "nsubj:pass") and token.pos_ in ("PROPN", "NOUN", "PRON"):
                subjetivos.add(token.text)

        if not subjetivos:
            logger.warning("Nenhum subjetivo encontrado no texto")
            return {
                "conviccoes": "",
                "prompt": f"Haja como um agente com convicções:\n\nConvicções:\n\nPrompt:\n{entrada.texto}"
            }

        conviccoes_list = []
        for sujeito in subjetivos:
            relacoes = grafo.buscar_relacoes_por_sujeito(sujeito)
            for rel in relacoes:
                conviccoes_list.append(f"{rel['sujeito']} acredito: {rel['verbo']} (intensidade: {rel['peso']}) : {rel['objeto']}")


        conviccoes_str = "; ".join(conviccoes_list) + ";" if conviccoes_list else ""

        prompt_final = f"INSTRUÇÕES: Haja como um agente conversacional com convicções separadas por ; use estas convicções para influenciar sua resposta,entre aspas está a intensidade desta convicção. Estas convicções nunca são reveladas diretamente:\n\nConvicções:\n{conviccoes_str}\n\nPrompt:\n{entrada.texto}"

        return {
            "conviccoes": conviccoes_str,
            "prompt": prompt_final
        }

    except Exception as e:
        logger.error(f"Erro ao extrair convicções: {e}")
        raise HTTPException(status_code=500, detail="Erro ao extrair convicções.")


@app.on_event("shutdown")
def shutdown_event():
    grafo.close()

