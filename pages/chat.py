import tempfile
import streamlit as st
from utils.Session import *
from utils.Chats import BasicChat
from utils.Agents import Rag


st.set_page_config(page_title="Analyse d'Offres", page_icon="💵", layout="wide") 

init_session()

# -- Store chat in session
if "chat" not in st.session_state:
    st.session_state.chat = BasicChat()  
chat = st.session_state.chat

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Options"):
        chat.options()
with col2:
    if st.button("Reset chat"):
        chat.reset_history()
with col3:
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
        
