# Use uma imagem base com Python
FROM python:3.10-slim

# Instalar dependências do sistema
RUN apt-get update && \
    apt-get install -y curl gnupg && \
    curl -fsSL https://debian.neo4j.com/neotechnology.gpg.key | gpg --dearmor -o /usr/share/keyrings/neo4j-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/neo4j-archive-keyring.gpg] https://debian.neo4j.com stable 4.4" | tee /etc/apt/sources.list.d/neo4j.list && \
    apt-get update && \
    apt-get install -y neo4j

# Definir variáveis de ambiente para Neo4j
ENV NEO4J_HOME="/var/lib/neo4j"
ENV PATH="${PATH}:${NEO4J_HOME}/bin"

# Instalar dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código do chatbot para dentro do contêiner
COPY app.py /app/app.py

# Expor as portas necessárias (7687 é a porta padrão do Neo4j)
EXPOSE 7687 5000

# Iniciar o Neo4j e o app Python
CMD neo4j start && python /app/app.py
