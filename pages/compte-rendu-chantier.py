from typing import List
import streamlit as st
import tempfile
from crewai_tools import PDFSearchTool
from docx import Document
from dotenv import load_dotenv

from utils.Agents import Commercial, Consultant
from utils.Functions import toast, extraire_tableau_json, DocumentWriter

load_dotenv()

#tableau dans lequel on va stocker les Agents commerciaux
agents_commerciaux: List[Commercial] = []

# --- Streamlit Interface and sidebar ---
st.title(f"Assistant Compte Rendu de Chantier (CRC)")

with st.expander("Explications" , expanded=True):
    st.markdown("""
    Lors d'une réunion de chantier, les différents acteurs du projet, tels que le maître d'ouvrage, le maître d'œuvre, les entreprises, et parfois les bureaux d'études, se réunissent pour 
    * faire un point l'avancement des études et travaux.
    * discuter des éventuels problèmes rencontrés, 
    * prendre et acter des décisions pour assurer le bon déroulement du chantier.
    
    Chaque réunion permet de suivre l'évolution du planning, vérifier la conformité des travaux réalisés, 
    et ajuster les interventions futures si nécessaire. 
    
    À l'issue de cette réunion, un compte rendu est rédigé pour consigner les décisions prises, 
    les actions à entreprendre, ainsi que les responsabilités de chacun. 
    
    
    Cet outil est essentiel pour garder une trace officielle des échanges en garantissant une bonne coordination des acteurs. 
    
    Le présent logiciel de gestion de chantier permet de faciliter la rédaction de ces comptes rendus en structurant les informations, en automatisant certaines tâches, et en assurant une meilleure traçabilité des actions.
            """)
# --- Le CCTP ---
st.header("CRC")
crc_uploaded = st.file_uploader("Télécharger le compte rendu précédent", type="pdf")
crc_pdf_search_tool = None
