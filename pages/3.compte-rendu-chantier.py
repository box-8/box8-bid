import os
import tempfile
import streamlit as st 
from utils.Session import *
from utils.Agents import RagAgent
from crewai_tools import PDFSearchTool

st.set_page_config(page_title="Compte Rendu de Chantier", page_icon="🎙️", layout="wide") 

init_session()
ui_options_llmModel()


st.header("Compte rendu de chantier (" + st.session_state.llm_model+")")

file_uploaded = st.file_uploader("Télécharger le CCTP", type="pdf")
crc_tool = None
question = st.chat_input("Poser votre question")
try :
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as crc_pdf:
        crc_pdf.write(file_uploaded.read())
        crc_pdf_path = crc_pdf.name
    crc_tool = PDFSearchTool(pdf=crc_pdf_path)
    if crc_tool:
        if st.button("Voir le fichier"):
            os.startfile(crc_pdf_path)

    gaelJaunin = RagAgent(name=file_uploaded.name, tool=crc_tool)

    if question:
        st.warning(question)
        result = gaelJaunin.answer(question)
        st.success(result)

except Exception as e:
    print(f"Une erreur s'est produite  : {str(e)}")

