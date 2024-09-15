import streamlit as st
from crewai import Agent, Task, Crew, Process
from box8.Agents import SummarizePdf
from box8.Session import *

st.set_page_config(page_title="Résumer document", page_icon="🐻", layout="wide") 
init_session()


summarizer = SummarizePdf() 
ui_options_llmModel(sidebar=True)
 
if False:
    summarizer.initiate("uploads/devis/CCTP_VRD.pdf")
    summarizer.save()
else:
    # Interface Streamlit
    st.title("Résumé de texte")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("images/logo.png", width=150)
    with col2:
        uploaded_file = st.file_uploader("Téléverser un fichier PDF", type="pdf")

    if uploaded_file :
        summarizer.initiate(uploaded_file)
        summarizer.summarize()
        summarizer.save()