import os
import tempfile
import streamlit as st
from box8.Session import APP_PATH, init_session
from box8.Chats import BasicChat, BasicPdfRag
from box8.Agents import SummarizePdf

st.set_page_config(page_title="Analyse d'Offres", page_icon="💵", layout="wide") 

init_session()

# -- Store chat in session
if "basicChat" not in st.session_state:
    st.session_state.basicChat = BasicChat()

if "basicPdfRag" not in st.session_state:
    st.session_state.basicPdfRag = BasicPdfRag()        


container = st.sidebar.container()
file_upload = container.file_uploader("Télécharger un document", type="pdf")


chat = st.session_state.basicChat
rag = st.session_state.basicPdfRag

header_container = st.container()

col1, col2, col3, col4 = header_container.columns(4)

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
    pass

        
            
with col4:
    if st.button("Sauvegarder la conversation"):
        if file_upload:
            chat.saveToDoc()
        else:
            rag.saveToDoc()
        
    
# chat avec le LLM dans le contexte du document
if file_upload:     

    if st.button("Résumer le document"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            temp.write(file_upload.read())
        st.write(temp.name)
        summarizer = SummarizePdf() 
        summarizer.initiate(temp.name)
        summarizer.summarize()
        doc = summarizer.save()
        if st.button("ouvrir le document"):
            
            st.write(doc.path)
            os.startfile(doc.path)
            
    else:
        try :
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
                temp.write(file_upload.read())
            rag.setfileByPath(path=temp.name)
            rag.chat()  
            if temp.name:
                if container.button("Voir le fichier", type="primary"):
                    os.startfile(temp.name)
                
        except Exception as e:
            st.error(e)    
# chat avec le LLM sans contexte de document
else: 
    chat.chat()


