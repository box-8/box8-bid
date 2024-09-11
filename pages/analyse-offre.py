import os
from typing import List
import streamlit as st 
import tempfile
from crewai_tools import PDFSearchTool
from docx import Document
from dotenv import load_dotenv
from utils.Session import ChooseLLM, trouver_index, init_session
from utils.Agents import Commercial, Consultant
from utils.Functions import toast, extraire_tableau_json, DocumentWriter

st.set_page_config(page_title="Analyse d'Offres", page_icon="💵", layout="wide") 

init_session()


idx = trouver_index(st.session_state.llm_model, st.session_state.llm_allowed)
selected_llm = st.sidebar.radio("Choose LLM",
        st.session_state.llm_allowed,
        captions=st.session_state.llm_allowed_def,
        key="selected_llm_options",
        index=idx
    )
if selected_llm :
    st.session_state.llm_model = selected_llm

#tableau dans lequel on va stocker les Agents commerciaux
agents_commerciaux: List[Commercial] = []

# --- Streamlit Interface and sidebar ---


# selected_llm = st.sidebar.radio(
#         "Choose LLM",
#         st.session_state.llm_allowed,
#         captions=st.session_state.llm_allowed_def,
#         key="selected_llm_options"
#     )
# if selected_llm :
#     st.session_state.llm_model = selected_llm
    
    
st.toast(st.session_state.llm_model)

st.title(f"Analyseur d'offres ({st.session_state.llm_model})")

with st.expander("Explications" , expanded=False):
    st.markdown("""
    L'analyse d'offre à partir d'un cahier des charges est un processus important dans le cadre d'un appel d'offres. Elle consiste à examiner attentivement les propositions des différents soumissionnaires afin de déterminer celle qui répond le mieux aux exigences et aux besoins spécifiés dans le cahier des charges.
    
    Concrètement, cette analyse implique une évaluation rigoureuse de chaque offre en fonction des critères prédéfinis, tels que :
    * le prix, 
    * la qualité, 
    * les délais, 
    * l'expérience du soumissionnaire, etc. 

    Le but est de comparer objectivement les différentes propositions et de sélectionner celle qui présente le meilleur rapport qualité-prix, tout en s'assurant de sa conformité aux spécifications techniques et aux exigences légales.

    L'analyse d'offre est donc une étape clé pour garantir la réussite d'un projet, en permettant de choisir le prestataire le plus adapté pour répondre aux attentes et mener à bien la mission confiée.
    Elle requiert une grande rigueur et une parfaite connaissance du cahier des charges afin de prendre une décision éclairée et objective. 
            """)
# --- Le CCTP ---
st.header("CCTP")
cctp_uploaded = st.file_uploader("Télécharger le CCTP", type="pdf")
cctp_pdf_search_tool = None


st.header("Offres")

offre_uploaded_1 = st.file_uploader("Télécharger l'offre 1 ", type="pdf")
offre_pdf_search_tool_1 = None

offre_uploaded_2 = st.file_uploader("Télécharger l'offre 2 ", type="pdf")
offre_pdf_search_tool_2 = None
        
offre_uploaded_3 = st.file_uploader("Télécharger l'offre 3 ", type="pdf")
offre_pdf_search_tool_3 = None      


def create_Commercial(offre_uploaded_1):
    try :
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as offre_temp_pdf_1:
            offre_temp_pdf_1.write(offre_uploaded_1.read())
            offre_temp_pdf_path_1 = offre_temp_pdf_1.name
        cctp_pdf_search_tool_1 = PDFSearchTool(pdf=offre_temp_pdf_path_1)
        return Commercial(name=offre_uploaded_1.name, offre=cctp_pdf_search_tool_1)
    except Exception as e:
        print(f"Une erreur s'est produite create_Commercial : {str(e)}")
        return None
        
if st.button("Commencer l'analyse du CCTP", key="analisys_cctp") :
    
    if cctp_uploaded is None : 
        st.warning("Fournir un CCTP est obligatoire")
    else:
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as cctp_temp_pdf:
            cctp_temp_pdf.write(cctp_uploaded.read())
            cctp_temp_pdf_path = cctp_temp_pdf.name
        cctp_pdf_search_tool = PDFSearchTool(pdf=cctp_temp_pdf_path)    
        gaelJaunin = Consultant(cctp_pdf_search_tool)
        questionsGaelJaunin = gaelJaunin.analyse_cctp()
        st.write(questionsGaelJaunin)
        agents_commerciaux.append(create_Commercial(offre_uploaded_1))
        agents_commerciaux.append(create_Commercial(offre_uploaded_2))
        agents_commerciaux.append(create_Commercial(offre_uploaded_3))
        # on nettoie le tableau d'offres Nulles
        print(agents_commerciaux)
        agents_commerciaux = [offre for offre in agents_commerciaux if offre is not None]
        print(agents_commerciaux)
        if len(agents_commerciaux) <=1  :
            st.error("Fournir au moins une offre à analyser vis à vis du CCTP")
        else:
            # on Créé un document word
            rapportGaelJAUNIN = DocumentWriter("Rapport d'analyse d'offres")
            
            for i, commercial in enumerate(agents_commerciaux):
                Chapter = f"Commercial {i+1} : {commercial.name} "
                rapportGaelJAUNIN.Chapter(Chapter)
                st.markdown(f"## {Chapter}")
                for entry in questionsGaelJaunin:
                    enjeu = entry["enjeu"]
                    question = entry["question"]
                    rapportGaelJAUNIN.SubChapter(f"{enjeu}")
                    rapportGaelJAUNIN.writeBlue(f"{question}")
                    answer = commercial.answer(question)
                    rapportGaelJAUNIN.writeBlack(answer)
                    st.subheader(f"{question}")
                    st.markdown(f"{answer}")
            docPath = rapportGaelJAUNIN.saveDocument()
            button = st.button(f"Ouvrir le rapport",key="wordfinished")
            if button: 
                os.startfile(docPath)
            
