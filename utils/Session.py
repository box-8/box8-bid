import streamlit as st 
import os
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

def init_session():
    if "llm_model" not in st.session_state:
        st.session_state.llm_model = 'openai'  

    if "llm_allowed" not in st.session_state:
        st.session_state.llm_allowed = ["openai", "groq", "groq-llama", "local", "gpt-3-turbo"]
        
    if "llm_allowed_def" not in st.session_state:
        st.session_state.llm_allowed_def = [
            "Modèle Open AI GPT-4 (Defaut)", 
            "Moteur d'inférence rapide avec le modèle Mixtral-8x7b", 
            "Moteur d'inférence rapide avec le modèle Llama-3.1-70b-versatile", 
            "Moteur LM Studio ou ollama en local sur le port 1552", 
            "Modèle Open AI GPT-3-turbo"]

    if "current_affaire" not in st.session_state:
        st.session_state.current_affaire = None  
init_session()



def ChooseLLM(name=""):
    
    if not name == "" :
        name = st.session_state.llm_model
    else:
        st.session_state.llm_model = name

    if name not in st.session_state.llm_allowed:
        name = "opeanai"

    if name=="local":
        selected_llm = ChatOpenAI(
            model="mistral-7b-local",
            base_url="http://localhost:1552/v1"
        )
    elif name=="groq":
        API_KEY = os.getenv("GROQ_API_KEY")
        selected_llm = ChatGroq(temperature=0, groq_api_key=API_KEY, model_name="mixtral-8x7b-32768")
        
    elif name=="groq-llama":
        API_KEY = os.getenv("GROQ_API_KEY")
        selected_llm = ChatGroq(temperature=0, groq_api_key=API_KEY, model_name="llama-3.1-70b-versatile")
    
    elif name=="openai":
        API_KEY = os.getenv("OPENAI_API_KEY")
        selected_llm = ChatOpenAI(
            temperature=0.7,
            openai_api_base="https://api.openai.com/v1",  # Le point de terminaison de l'API OpenAI
            openai_api_key=API_KEY ,  # Remplace par ta clé API OpenAI
            model_name="gpt-4",  # Utilise GPT-4 par exemple, ou un autre modèle supporté
        )
    else:
        API_KEY = os.getenv("OPENAI_API_KEY")
        selected_llm = ChatOpenAI(
            temperature=0.7,
            openai_api_base="https://api.openai.com/v1",  # Le point de terminaison de l'API OpenAI
            openai_api_key=API_KEY ,  # Remplace par ta clé API OpenAI
        )
    return selected_llm



# --- PATH de la base de données sqlite

SQL_LITE_AFFAIRES_PATH = 'sqlite:///C:/_prod/box8-bid/affaires.db'