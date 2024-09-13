import tempfile
import streamlit as st
from utils.Session import *
from utils.Chats import BasicChat, BasicPdfRag


st.set_page_config(page_title="Analyse d'Offres", page_icon="💵", layout="wide") 

init_session()


container = st.sidebar.container()
file_upload = container.file_uploader("Télécharger un document", type="pdf")
    
# -- Store chat in session
if "chat" not in st.session_state:
    st.session_state.chat = BasicChat()
chat = st.session_state.chat


header_container = st.container()

col1, col2, col3 = header_container.columns(3)

    
# chat avec le LLM dans le contexte du document
if file_upload:     
    try :
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            temp.write(file_upload.read())
        
        if "chatrag" not in st.session_state:
            st.session_state.chatrag = BasicPdfRag(path=temp.name)        
        rag = st.session_state.chatrag
        rag.chat()  
        if temp.name:
            if container.button("Voir le fichier", type="primary"):
                os.startfile(temp.name)
            
    except Exception as e:
        st.error(e)    
# chat avec le LLM sans contewte de document
else: 
    chat.chat()



with col1:
    if st.button("Options"):
        chat.options()
    
with col2:
    if st.button("Reset chat"):
        if file_upload:
            chat.reset_history()     
        else:
            rag.reset_history()
    
with col3:
    if st.button("Save to doc"):
        if file_upload:
            chat.saveToDoc()
        else:
            rag.saveToDoc()
        
    