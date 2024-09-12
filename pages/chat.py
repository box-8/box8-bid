import tempfile
import streamlit as st
from utils.Session import *
from utils.Chats import BasicChat
from utils.Agents import Rag


st.set_page_config(page_title="Analyse d'Offres", page_icon="💵", layout="wide") 

init_session()


chat = BasicChat()

if st.button("Options"):
    chat.options()

file_upload = st.file_uploader("Télécharger le CCTP", type="pdf")
chat.chat()


if file_upload:

    try :
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            temp.write(file_upload.read())
        rag = Rag()
        rag.set_doc(path=temp.name)
        input = st.text_input("entrer votre question")
        if input:
            rag.answer(input)
            
    except Exception as e:
        st.error(e)    
        
