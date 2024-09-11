import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader
import time

from dotenv import load_dotenv
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

st.title("Chatbot with Groq")

llm = ChatGroq(groq_api_key = groq_api_key,
               model_name = "llama3-8b-8192")

prompt = ChatPromptTemplate.from_template(
'''
Answer the following question based on the provided context.
Please provide the most accurate response based on the question
<context>
{context}
</context>
Question: {input}
'''
)

def vector_embeddings():
    if "vectors" not in st.session_state:
        st.session_state.embeddings = OllamaEmbeddings(model="llama2")
        st.session_state.loader = TextLoader("merged_text_file.txt")
        st.session_state.docs = st.session_state.loader.load()
        st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 200)
        st.session_state.final_documents = st.session_state.text_splitter.split_documents(st.session_state.docs)
        st.session_state.vectors = FAISS.from_documents(st.session_state.final_documents[:10],st.session_state.embeddings)



prompt1 = st.text_input("Enter your Query!")

if st.button("Documents Embeddings"):
    vector_embeddings()
    st.write("Vector Store DB is ready!")



if prompt1:
    document_chain = create_stuff_documents_chain(llm,prompt)
    retriever = st.session_state.vectors.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever,document_chain)
    start=time.process_time()
    response = retrieval_chain.invoke({"input":prompt1})
    print("Response_time :", time.process_time()-start)
    st.write(response['answer'])

    with st.expander("Document Similarity Search"):
        for i,doc in enumerate(response['context']):
            st.write(doc.page_content)
            st.write("--------------------------------")
