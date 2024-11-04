from neo4j import GraphDatabase
from transformers import AutoTokenizer, AutoModel
from langchain.embeddings import EmbeddingFunction
from langchain.chains import RetrievalQA
from langchain.vectorstores import Neo4jVectorStore
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
import torch
import os

# Conexão com o Neo4j
uri = "neo4j://localhost:7687"
username = "neo4j"
password = "test"  # Altere para a senha do Neo4j no ambiente de produção

driver = GraphDatabase.driver(uri, auth=(username, password))

# Função de embeddings com BERT
model_name = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def get_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    outputs = model(**inputs)
    embeddings = outputs.last_hidden_state[:, 0, :].detach()
    return embeddings

# Configuração do LangChain e GPT
class BERTEmbeddingFunction(EmbeddingFunction):
    def __call__(self, text):
        return get_embedding(text).numpy().flatten()

embedding_function = BERTEmbeddingFunction()
vectorstore = Neo4jVectorStore(driver, embedding_function)
llm = OpenAI(model_name="text-davinci-003")
qa_chain = RetrievalQA(
    retriever=vectorstore.as_retriever(),
    llm=llm,
    prompt=PromptTemplate("Responda com base nos dados financeiros: {question}")
)

# Função para perguntas e respostas
def ask_question(question):
    response = qa_chain({"question": question})
    return response["result"]

# Exemplo de uso
if __name__ == "__main__":
    question = "Qual foi o saldo da conta no último trimestre?"
    print("Resposta:", ask_question(question))
