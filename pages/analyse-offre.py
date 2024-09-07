import json
from typing import List
import streamlit as st
import tempfile
from crewai import Agent, Task, Crew, Process
from crewai_tools import PDFSearchTool
from docx import Document
from docx.shared import RGBColor
from datetime import datetime
from dotenv import load_dotenv

from utils.Agents import Commercial
from utils.Functions import toast, extraire_tableau_json


load_dotenv()



# --- Global Word Document ---
docAnalyse = Document()
docAnalyse.add_heading('Résultat de l\'Analyse', 0)

def writeDocument(text, heading_level=None, color=RGBColor(0, 0, 0)): # Noir par défaut
    """
    Ajoute du texte au document global avec une mise en forme spécifique.

    Args:
        text (str): Le texte à ajouter au document.
        heading_level (int, optional): Le niveau de titre (1 à 9). Par défaut, un titre de niveau 1.
        color (RGBColor, optional): La couleur du texte. Par défaut, rouge vif.
    """
    global docAnalyse

    if heading_level is None:
        paragraph = docAnalyse.add_paragraph(text)
        paragraph.style.font.color.rgb = color
    elif heading_level == 0:
        docAnalyse.add_heading(text, 0)
    elif 1 <= heading_level <= 3:
        heading = docAnalyse.add_heading(text, heading_level)
        heading.style.font.color.rgb = color
    else:
        paragraph = docAnalyse.add_paragraph(text)
        paragraph.style.font.color.rgb = color

# Exemple d'utilisation
# writeDocument("Ceci est un titre important", heading_level=1)
# writeDocument("Et voici un paragraphe en rouge vif.")


def saveDocument():
    global docAnalyse  # Indique que vous utilisez la variable globale à l'intérieur de la fonction
    # Save the Word document
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"result_{timestamp}.docx"
    docAnalyse.save(filename) 



#tableau dans lequel on va stocker les fichiers offres

agents_commerciaux: List[Commercial] = []
#tableau dans lequel on va stocker les Agents commerciaux
commerciaux = []

# --- Streamlit Interface and sidebar ---
st.title("Analyseur d'offres")


tab1, tab2, tab3 = st.tabs(["CCTP", "Offres", "Result"])

with tab1:
    # --- Streamlit Interface main page ---
    cctp_uploaded = st.file_uploader("Télécharger le CCTP", type="pdf")
    cctp_pdf_search_tool = None
    if cctp_uploaded is None:
        toast("Charger le CCTP")
    else :
        # Save uploaded PDF to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as cctp_temp_pdf:
            cctp_temp_pdf.write(cctp_uploaded.read())
            cctp_temp_pdf_path = cctp_temp_pdf.name
        cctp_pdf_search_tool = PDFSearchTool(pdf=cctp_temp_pdf_path)


    with tab2:
        offre_uploaded_1 = st.file_uploader("Télécharger l'offre 1 ", type="pdf")
        offre_pdf_search_tool_1 = None

        if offre_uploaded_1 is None:
            toast("Charger l'offre 1")
        else:
            # Save uploaded PDF to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as offre_temp_pdf_1:
                offre_temp_pdf_1.write(offre_uploaded_1.read())
                offre_temp_pdf_path_1 = offre_temp_pdf_1.name
            cctp_pdf_search_tool_1 = PDFSearchTool(pdf=offre_temp_pdf_path_1)
            agents_commerciaux.append(Commercial(cctp_pdf_search_tool_1))

        

        offre_uploaded_2 = st.file_uploader("Télécharger l'offre 2 ", type="pdf")
        offre_pdf_search_tool_2 = None
        if offre_uploaded_2 is None:
            toast("Charger l'offre 2")
        else:
            # Save uploaded PDF to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as offre_temp_pdf_2:
                offre_temp_pdf_2.write(offre_uploaded_2.read())
                offre_temp_pdf_path_2 = offre_temp_pdf_2.name
            offre_pdf_search_tool_2 = PDFSearchTool(pdf=offre_temp_pdf_path_2)
            agents_commerciaux.append(Commercial(offre_pdf_search_tool_2))


        offre_uploaded_3 = st.file_uploader("Télécharger l'offre 3 ", type="pdf")
        offre_pdf_search_tool_3 = None
        if offre_uploaded_3 is None:
            toast("Charger l'offre 3")
        else:
            # Save uploaded PDF to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as offre_temp_pdf_3:
                offre_temp_pdf_3.write(offre_uploaded_3.read())
                offre_temp_pdf_path_3 = offre_temp_pdf_3.name
            offre_pdf_search_tool_3 = PDFSearchTool(pdf=offre_temp_pdf_path_3)
            agents_commerciaux.append(Commercial(offre_pdf_search_tool_3))

        can_start = True
        if len(agents_commerciaux) <1  :
            can_start = False 
            st.warning("Charger au moins une offre (3 maxi)")


    with tab3:
        
        if cctp_pdf_search_tool is None:
            st.warning("Charger le CCTP et au moins 1 offre (3 maxi)")
            st.markdown("""
                    L'analyse d'offre à partir d'un cahier des charges est un processus important dans le cadre d'un appel d'offres. Elle consiste à examiner attentivement les propositions des différents soumissionnaires afin de déterminer celle qui répond le mieux aux exigences et aux besoins spécifiés dans le cahier des charges.
                    
                    Concrètement, cette analyse implique une évaluation rigoureuse de chaque offre en fonction des critères prédéfinis, tels que le prix, la qualité, les délais, l'expérience du soumissionnaire, etc. Le but est de comparer objectivement les différentes propositions et de sélectionner celle qui présente le meilleur rapport qualité-prix, tout en s'assurant de sa conformité aux spécifications techniques et aux exigences légales.
                    
                    L'analyse d'offre est donc une étape clé pour garantir la réussite d'un projet, en permettant de choisir le prestataire le plus adapté pour répondre aux attentes et mener à bien la mission confiée. Elle requiert une grande rigueur et une parfaite connaissance du cahier des charges afin de prendre une décision éclairée et objective. 
                        """)
        else:
            if not st.button("Commencer l'analyse du CCTP", key="analisys_cctp") :
                st.warning("Charger le CCTP et les offres des soumissionnaires (3 maxi)")
            else:

                # --- Main analisys procedure ---
                can_start = False
                if len(agents_commerciaux) <=2  :
                    can_start = True 
                    
                if not cctp_pdf_search_tool is None and can_start :
                    
                    ingenieur_generaliste = Agent(
                        role="Ingénieur généraliste",
                        goal="Poser des questions pertinente pertinentes, diriger le projet",
                        allow_delegation=False,
                        verbose=True,
                        backstory=(
                            """
                            Véritable chef d'orchestre l'ingénieur généraliste est compétent pour rechercher et 
                            extraire des points d'attention dans les documents fournis.
                            Il garanti qu'aucun manquement ne soit présent  la porte à des non confromités dans le projet qui lui est confié.
                            """
                        ),
                        tools=[cctp_pdf_search_tool],
                    )
                    
                    
                    expected_output_json="""
                        En retour, générer uniquement une chaine de charactères représentant un tableau json contenant les enjeux du cahier des charges (CCTP) 
                        listés sous la forme de questions selon la structure suivante : 

                        [
                            \{ 
                                "enjeu" : "titre de l'enjeu du CCTP",
                                "question" : "question à poser à l'offre du soumissionnaire pour vérifier que l'enjeux est traité plus ou moins correctement"
                            \}, 
                        ]

                        """
                    
                    task_list_keypoints = Task(
                        description=(""" 
                            A partir du contexte du projet décrit dans le cahier des charges (CCTP);
                            extraire des points d'attention de manière à vérifier ultérieurement dans les offres des entreprises que 
                            les enjeux sont bien pris en compte. 
                            """),
                        expected_output=expected_output_json,
                        tools=[cctp_pdf_search_tool],
                        agent=ingenieur_generaliste,                
                    )
                    
                        
                    
                    crew = Crew(
                        agents=[ingenieur_generaliste],
                        tasks=[task_list_keypoints],
                        process=Process.sequential,
                        full_output=True,
                        verbose=True,
                        )
                    
                    GlobalText = ""
                    crew_output = crew.kickoff()
                    st.write(crew_output)
                    questionnements = []
                    RAW = crew_output.raw
                    
                    questionnements = extraire_tableau_json(RAW)
                    writeDocument("ANALYSE OFFRES", heading_level=0)
                    for i, commercial in enumerate(agents_commerciaux):
                        Offre = f"Offre Commerciale n°{i+1}"
                        st.markdown(f"# {Offre}")
                        writeDocument(Offre, heading_level=1)
                        
                        for k, entry in enumerate(questionnements) :
                            enjeu =  entry["enjeu"]
                            question = entry["question"]
                            responseCommercial = commercial.ask(question)
                            
                            st.write(f"{enjeu} : {question}")
                            
                            writeDocument(f"{enjeu}", heading_level=2)
                            writeDocument(f"{question}", heading_level=3)
                            writeDocument(responseCommercial)
                    
                    saveDocument()
        
toast(None)