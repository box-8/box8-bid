import streamlit as st 
import os
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI, OpenAI
from entities.Affaires import Affaire

# --- PATH de la base de données sqlite

APP_PATH = "C:\\_prod\\box8-bid\\"

SQL_LITE_AFFAIRES_PATH = 'sqlite:///C:/_prod/box8-bid/affaires.db'



def string_to_float(value):
    try:
        # Suppression des symboles non numériques comme l'euro (€) et des espaces
        cleaned_value = value.replace('€', '').replace(' ', '').replace(',', '.')
        # Conversion en float
        return float(cleaned_value)
    except ValueError:
        # Gestion des erreurs si la conversion échoue
        return 0.0  # Vous pouvez décider d'une valeur par défaut ou d'une autre gestion d'erreur



def app_upload_file(file):
    devis_directory = "uploads/devis"
    if not os.path.exists(devis_directory):
        os.makedirs(devis_directory)
        # Chemin complet où le fichier sera stocké
    devis_path = os.path.join(devis_directory, file.name)
    with open(devis_path, "wb") as f:
        f.write(file.getbuffer())
    return devis_path

   
def trouver_index(valeur, tableau):
    try:
        index = tableau.index(valeur)
        return index
    except ValueError:
        return 0

# initie les variables de session
def init_session():
    init_session_llm()
    init_session_llm_vision()
    init_session_affaire()
    
def init_session_affaire():
    if "affaire" not in st.session_state:
        st.session_state.affaire = Affaire(nom="") 



def init_session_llm():
    # -- modeles de langage
    if "llm_allowed" not in st.session_state:
        st.session_state.llm_allowed = ["openai", "groq", "groq-llama", "local", "gpt-3.5"]
    
    if "llm_allowed_def" not in st.session_state:
        st.session_state.llm_allowed_def = [
            "Modèle Open AI GPT-4 (Defaut)", 
            "Moteur d'inférence rapide avec le modèle Mixtral-8x7b", 
            "Moteur d'inférence rapide avec le modèle Llama-3.1-70b-versatile", 
            "Moteur LM Studio ou ollama en local sur le port 1552", 
            "Modèle Open AI GPT-3-turbo"]
        
    if "llm_model" not in st.session_state:
        st.session_state.llm_model = 'openai'  


# génère le composant de choix du modèle de langage
def ui_options_llmModel(sidebar=True):
    idx = trouver_index(st.session_state.llm_model, st.session_state.llm_allowed)
    if sidebar :
        selected_llm = st.sidebar.radio("Modèle de langage",
            st.session_state.llm_allowed,
            captions=st.session_state.llm_allowed_def,
            key="selected_llm_options",
            index=idx
        )
    else:
        selected_llm = st.radio("Modèle de langage",
            st.session_state.llm_allowed,
            captions=st.session_state.llm_allowed_def,
            key="selected_llm_options",
            index=idx
        )
    if selected_llm :
        st.session_state.llm_model = selected_llm

# renvoie le llm à utiliser. par defaut, 
# argument vide on renvoie le llm de session
# 
def ChooseLLM(model_name=""):
    
    if not model_name =="":
        name = model_name
    else: 
        name = st.session_state.llm_model

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
    
    st.toast("Model for Agent is :  "  + selected_llm.model_name)
    return selected_llm



def init_session_llm_vision():
    # -- modeles de vision
    if "llm_allowed_vision" not in st.session_state:
        st.session_state.llm_allowed_vision = ["gpt-4o-mini", "local-vision"]
    
    if "llm_allowed_vision_def" not in st.session_state:
        st.session_state.llm_allowed_vision_def = [
            "Modèle OpenAI Dall-E (Defaut)", 
            "Moteur LM Studio ou ollama en local sur le port 1553"]
        
    if "llm_model_vision" not in st.session_state:
        st.session_state.llm_model_vision = 'gpt-4'


# génère le composant de choix du modèle de vision
def ui_options_visionModel(sidebar=True):
    idx = trouver_index(st.session_state.llm_model_vision, st.session_state.llm_allowed_vision)
    if sidebar :
        selected_llm = st.sidebar.radio(
            "Modèle de Vision",
            st.session_state.llm_allowed_vision,
            captions=st.session_state.llm_allowed_vision_def,
        )
    else:
        selected_llm = st.radio(
            "Modèle de Vision",
            st.session_state.llm_allowed_vision,
            captions=st.session_state.llm_allowed_vision_def,
        )
    if selected_llm :
        st.session_state.llm_model_vision = selected_llm

# renvoie le llm à utiliser. par defaut, 
# argument vide on renvoie le llm de session
# "gpt-4o-mini", "local-vision"
def ChooseVisionLLM(model_name=""):
    
    if not model_name =="":
        name = model_name
    else: 
        name = st.session_state.llm_model_vision

    if name=="local-vision":
        base_url = "http://localhost:1553/v1"  
        API_KEY="not-needed"
        selected_llm = OpenAI(base_url=base_url, api_key=API_KEY) 
    elif name=="supervision-model":
        base_url = "https://api.openai.com/v1/chat/completions"
        API_KEY = os.getenv("OPENAI_API_KEY")
        selected_llm = OpenAI(api_key=API_KEY, model="gpt-4")
    else:
        st.toast("vision model name : " + st.session_state.llm_model_vision)
        base_url = "https://api.openai.com/v1/chat/completions"
        API_KEY = os.getenv("OPENAI_API_KEY")
        selected_llm = OpenAI(api_key=API_KEY, model="gpt-4o-mini")
    
    return selected_llm


@st.dialog("Modèles et Options")
def llm_options(chat=None):
    col1, col2 = st.columns(2)
    with col1:
        ui_options_llmModel(sidebar=False)
    with col2:
        ui_options_visionModel(sidebar=False)
      
    if chat is not None:
        modify_context = st.text_area("Context",chat.context)
        if modify_context:
            chat.setContext(modify_context)





if "confirm" not in st.session_state:
    st.session_state.confirm = False

@st.dialog("Confirmation requise")
def confirmbox():
    st.write("Confirmer !")
    if st.button("Oui",type="secondary"):
        st.session_state.confirm = True
        st.rerun()
    if st.button("Non"):
        st.session_state.confirm = False
        st.rerun()
if "llm_model_vision" not in st.session_state:
    st.session_state.confirm = False
