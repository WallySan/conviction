# Conviction

A solução cria um subconsciente infinito para a IA, ampliando seu contexto limitado e funcionando como uma memória profunda e ilimitada além da consciência imediata.

---

# Subconsciente Artificial – Contexto Expandido

🔍 A solução expande a IA ao incorporar um **Contexto Infinitamente Maior**, atuando como um **subconsciente artificial**.  
“Infinito” porque é limitado apenas pela capacidade de armazenamento do hardware. Ele não raciocina diretamente, mas **gera intuições** e **influencia escolhas e "sentimentos"** da IA.

🧠 Enquanto a IA tradicional opera com um **contexto limitado** (memória consciente), o subconsciente é uma **camada paralela e expansível de conhecimento**, fundamentada em convicções.

🌐 Proporciona acesso a informações **amplas e interconectadas**, indo além do que está presente no contexto imediato.

📚 Oferece uma base contínua de dados e aprendizados, permitindo **decisões mais coerentes**, **memória de longo prazo** e **conexões profundas** entre ideias.



![image](https://github.com/user-attachments/assets/713efea4-0325-4096-8e8b-13b3a52d4762)


---

# Treinamento do Subconsciente

![Treinamento do Subconsciente](https://github.com/user-attachments/assets/d60c561a-28d2-4a7e-b6b5-a5b3c3216e18)

---

# Detalhes de uma Região de Convicção

![Detalhes de uma Região de Convicção](https://github.com/user-attachments/assets/74e06fc5-9e48-45ef-ac1c-c58c6fd89447)

---

# Visualização do Mapa Mental

![Visualização do Mapa Mental](https://github.com/user-attachments/assets/0e7b7e0a-bdf6-495b-9589-655bcf8f2cde)

---

# Exemplo de Node

![Exemplo de Node](https://github.com/user-attachments/assets/72e94bc4-b44b-4457-97fb-c984c1a9de31)

---

# Exemplo de Relação

![Exemplo de Relação](https://github.com/user-attachments/assets/e49b3c42-c3bd-4e0b-98ef-02bf0d6bf14c)

---

# Prompt Incrementado com o Contexto de Convicções

![Prompt Incrementado](https://github.com/user-attachments/assets/a1e3088a-f39b-4d90-954a-6f7afe3f1f8f)

---

# Alimentando o Subconsciente com Informações

![Alimentando o Subconsciente](https://github.com/user-attachments/assets/48983a74-0085-4353-91a5-daa83693ef3d)

# Ao fazer a pergunta sobre horário que estudo, os grafos já recuperam o contexto, e sugerem o prompt:

![image](https://github.com/user-attachments/assets/c847336b-9fdc-492a-b852-d370d1030add)


---

# Realizando um Novo Prompt com Influência do Subconsciente

![Prompt com Influência do Subconsciente](https://github.com/user-attachments/assets/19fd5efe-6ec4-4e45-9e1f-831bab912a89)

---
---
---
# Instalação

Instalar as bibliotecas utilizadas pelo código via pip install

Instalar o Neo4J via Docker não esquecendo de ajustar sua senha para a mesma da conexão do arquivo .py

> sudo docker run \
>  --name neo4j-container \
>   -p 7474:7474 -p 7687:7687 \
>   -d \
>   -e NEO4J_AUTH=neo4j/S3nh@Segura2024 \
>   neo4j:latest


Realizar treinamento com afirmações simples separadas por ; 

> curl -X POST http://localhost:9875/processar \
>   -H "Content-Type: application/json" \
>   -d '{"texto": "A cultura é a base da identidade humana; A arte tem o poder de transformar a sociedade; A tradição deve ser respeitada, mas também atualizada; A > diversidade cultural é o maior patrimônio que temos; O folclore inspira nossa criatividade; As festas populares são momentos de verdadeira união; A língua materna é um tesouro que precisa ser preservado; A modernidade desafia os costumes, mas traz progresso; O artesanato reflete a alma de uma comunidade; O cinema é uma janela para diferentes realidades"}'

Via Web consegue interagir facilmente com os grafos:

> http://localhost:7474/browser/

Subir serviço de convicções:

> uvicorn app:app --host 0.0.0.0 --port 9875 --reload


