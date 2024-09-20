import os
import tempfile
import streamlit as st
from box8.Session import APP_PATH, init_session
from box8.Chats import BasicChat, BasicPdfRag
from box8.Agents import SummarizePdf

st.set_page_config(page_title="Chat Document", page_icon="🔖", layout="wide") 
st.title("Chat avec un document 🔖")

init_session()

# -- Store chat in session

def setCHAT():
    if "chatter" not in st.session_state:
        chatter = BasicChat()
        st.session_state.chatter = chatter
    else:
        chatter = st.session_state.chatter
        chatter.setSessionLlm()
    return chatter


def setRAG():
    
    if "ragger" not in st.session_state:
        ragger = BasicPdfRag()
        st.session_state.ragger = ragger        
    else:
        ragger = st.session_state.ragger    
        ragger.setSessionLlm()
    return ragger

header_container = st.container()

container = st.sidebar.container()
file_upload = container.file_uploader("Télécharger un document", type="pdf")

def header(header_container, chat):
    col1, col2 = st.columns(2)
    with col1:
        if header_container.button("Options"):
            chat.options()
    with col2:
        if header_container.button("Reset chat"):
            chat.reset_history()


def getTempsUploadedFile(file_upload):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
        temp.write(file_upload.read())
    return temp
    
# chat avec le LLM dans le contexte du document
if file_upload:
    tempFile = getTempsUploadedFile(file_upload)
    if st.button("Résumer le document"):
        summarizer = SummarizePdf() 
        summarizer.initiate(tempFile.name)
        summarizer.summarize()
        doc = summarizer.save()
        if st.button("ouvrir le document"):
            st.write(doc.path)
            os.startfile(doc.path)
    else:
        
        try :
            
            chat = setRAG()
            header(header_container, chat)
                
            chat.setfileByPath(path=tempFile.name)
            chat.chat()  
            
            if tempFile.name:
                if container.button("Voir le fichier", type="primary"):
                    os.startfile(tempFile.name)
                
        except Exception as e:
            st.error(e)    
# chat avec le LLM sans contexte de document
else:
    chat = setCHAT()
    chat.chat()
    header(header_container, chat)


