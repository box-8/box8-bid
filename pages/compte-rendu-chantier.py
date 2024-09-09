import os
from typing import List
from crewai import Agent, Crew, Process, Task
from langchain_openai import ChatOpenAI
import streamlit as st
import tempfile
from crewai_tools import PDFSearchTool
from docx import Document
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from utils.Functions import DocumentWriter

load_dotenv()

# --- Streamlit Interface and sidebar ---
st.title(f"Assistant Compte Rendu de Chantier (CRC)")

with st.expander("Explications" , expanded=False):
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

st.toast(st.session_state.llm_model)

st.header("CRC")
crc_uploaded = st.file_uploader("Télécharger le compte rendu", type="pdf")
crc_pdf_search_tool = None

if crc_uploaded is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as crc_temp_pdf:
        crc_temp_pdf.write(crc_uploaded.read())
        crc_temp_pdf_path = crc_temp_pdf.name
    crc_pdf_search_tool = PDFSearchTool(pdf=crc_temp_pdf_path) 
    
    button = st.button(f"voir le pdf",key="file_rename")
    if button: 
        os.startfile(crc_temp_pdf_path)

question = st.text_input("Saisissez votre question :")

if question and st.button("Lancer analyse") :
    rapportGaelJAUNIN = DocumentWriter("Rapport d'analyse d'offres")
    # Define general agent
    general_agent = Agent(role='Ingénieur Chef de projet',
        goal="""Etablir une liste des enjeux du projet.""",
        backstory="""
        Vous êtes un expert en construction.
        Vous fournissez des retours de haute qualité, approfondis, perspicaces et exploitables via une liste détaillée de modifications et de tâches concrètes. 
        """,
        allow_delegation=False, 
        verbose=True,
        tools=[crc_pdf_search_tool],
        llm = ChooseLLM()
    )


    # Define Tasks Using Crew Tools
    syntax_review_task = Task(
        description=f"""
        Analyser la situation du chantier d'aprés le document fourni en répondant à la question suivante : 
        {question}
        """,
        expected_output="Rapport d'analyse détaillée sur la situation du chantier.",
        agent=general_agent
    )
    
    crew =  Crew(
                agents=[general_agent],
                tasks=[syntax_review_task],
                process=Process.sequential,
            )
    try : 
        response = crew.kickoff()
        
        rapportGaelJAUNIN.writeBlack(response)
        rapportGaelJAUNIN.saveDocument()
    except Exception as e:
        print(f"Une erreur s'est produite: {str(e)}")
        response = str(e)
    st.write(response)
        
else:
    st.warning("Veuillez entrer une question avant de lancer l'analyse.")







