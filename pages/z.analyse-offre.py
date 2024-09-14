import os
from typing import List
from crewai import Agent, Crew, Task
import streamlit as st 
import tempfile
from crewai_tools import PDFSearchTool
from box8.Session import *
from box8.Agents import Commercial, Consultant, RagAgent
from box8.Functions import toast, extraire_tableau_json, DocumentWriter



st.set_page_config(page_title="Analyse d'Offres", page_icon="💵", layout="wide") 

init_session()

if st.sidebar.button("Options"):
    llm_options()


#tableau dans lequel on va stocker les Agents commerciaux
agents_commerciaux: List[Commercial] = []

# --- Streamlit Interface and sidebar ---

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
    if offre_uploaded_1 is None:
        return None
    try :
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as offre_temp_pdf_1:
            offre_temp_pdf_1.write(offre_uploaded_1.read())
            offre_temp_pdf_path_1 = offre_temp_pdf_1.name
        cctp_pdf_search_tool_1 = PDFSearchTool(pdf=offre_temp_pdf_path_1)
        return Commercial(offre=cctp_pdf_search_tool_1)
    except Exception as e:
        print(f"Une erreur s'est produite create_Commercial : {str(e)}")
        return None

llmname  = st.session_state.llm_model 
        
if st.button(f"Commencer l'analyse du CCTP ({llmname})", key="analisys_cctp") :
    
    if cctp_uploaded is None : 
        st.warning("Fournir un CCTP est obligatoire")
    else:
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as cctp_temp_pdf:
            cctp_temp_pdf.write(cctp_uploaded.read())
            cctp_temp_pdf_path = cctp_temp_pdf.name
        cctp_pdf_search_tool = PDFSearchTool(pdf=cctp_temp_pdf_path)    
        gaelJaunin = Consultant(cctp =cctp_pdf_search_tool)
        
        questionsGaelJaunin = gaelJaunin.analyse_cctp()
        
        agents_commerciaux.append(create_Commercial(offre_uploaded_1))
        agents_commerciaux.append(create_Commercial(offre_uploaded_2))
        agents_commerciaux.append(create_Commercial(offre_uploaded_3))
        # on nettoie le tableau d'offres Nulles
        # print(agents_commerciaux)
        agents_commerciaux = [offre for offre in agents_commerciaux if offre is not None]
        # print(agents_commerciaux)
        
        
        
        if len(agents_commerciaux) ==0  :
            st.error("Fournir au moins une offre à analyser vis à vis du CCTP")
            st.header("Les enjeux du CDC sont : ")
            for entry in questionsGaelJaunin:
                enjeu = entry["enjeu"]
                st.markdown(f"- {enjeu}")
            st.header("Les questions à poser sont : ")
            for entry in questionsGaelJaunin:
                question = entry["question"]
                st.markdown(f"- {question}")
        else:
            # on Créé un document word
            rapportGaelJAUNIN = DocumentWriter("Rapport d'analyse d'offres")
            
            # Initialiser la liste pour stocker les questions et réponses
            questions_reponses = []

            # Première boucle pour capturer les réponses de chaque commercial
            for i, commercial in enumerate(agents_commerciaux):
                Chapter = f"Commercial {i+1} : {commercial.name} "
                rapportGaelJAUNIN.Chapter(Chapter)
                st.markdown(f"## {Chapter}")

                for entry in questionsGaelJaunin:
                    enjeu = entry["enjeu"]
                    question = entry["question"]

                    rapportGaelJAUNIN.SubChapter(f"{enjeu}")
                    rapportGaelJAUNIN.writeBlue(f"{question}")

                    # Obtenir la réponse du commercial
                    answer = commercial.answer(question)

                    # Écrire la réponse dans le rapport
                    rapportGaelJAUNIN.writeBlack(answer)
                    st.subheader(f"{question}")
                    st.markdown(f"{answer}")

                    # Stocker la question, le commercial et sa réponse
                    questions_reponses.append({
                        "question": question,
                        "commercial": commercial.name,
                        "response": answer,
                        "enjeu": enjeu,
                    })

            # Sauvegarder le rapport
            docPath = rapportGaelJAUNIN.saveDocument()
            button = st.button(f"Ouvrir le rapport", key="wordfinished")
            if button: 
                os.startfile(docPath)
            
            
            
            # Étape 2 : Créer un tableau comparatif des réponses
            tableau_comparatif = {}

            # Boucle pour chaque question afin d'analyser et comparer les réponses
            for question_entry in questionsGaelJaunin:
                question = question_entry["question"]

                # Extraire les réponses pour cette question spécifique
                reponses_pour_question = [entry for entry in questions_reponses if entry["question"] == question]

                # Créer une entrée dans le tableau comparatif pour cette question
                tableau_comparatif[question] = {}

                for entry in reponses_pour_question:
                    commercial = entry["commercial"]
                    response = entry["response"]

                    # Ajouter la réponse du commercial à la question
                    tableau_comparatif[question][commercial] = response

            # Afficher le tableau comparatif (ou le stocker)
            #st.write("Tableau comparatif des réponses :")
            ## st.write(tableau_comparatif)
            
            # Etape 3 Générere une question pour créer le tableau comparatif 
            for question, reponses in tableau_comparatif.items():
                Question = ""
                print(f"Question : {question}")
                Question += f"""
                A la question : {question}
                
                """
                # Boucle pour chaque entreprise et sa réponse
                for entreprise, reponse in reponses.items():
                    # print(f"  Entreprise : {entreprise}")
                    # print(f"  Réponse : {reponse}")
                    Question += f"""
                    l'offre de l'entreprise "{entreprise}" indique : "{reponse}"
                    """
            
            st.write(Question)
            # Etape 43 Comparer les offres que les questions poszes 
            goal = """
                 Evaluer la qualité de la réponse de chaque entreprise dans un tableau json avec le format suivant : 
                 [
                     {"question":"résumé de la question",
                     [
                         {"entreprise":"évaluation de la réponse à la question posée sur une échelle de 1 à 10 "},
                         ... entreprises suivantes
                     },
                     
                 ]
                """
            agent = Agent(
                role="fournir un classement des offres",
                goal=goal,
                allow_delegation=False,
                verbose=True,
                backstory=(
                    """
                    On souhaite comparer entre eux le contenu technique de plusieures offres 
                    """
                ),
                llm = ChooseLLM()
            )
            task = Task(
                description=(
                    """
                    retoruner l'analyse de l'agent dans un tableau json
                    """
                ),
                expected_output="""
                    json avec le format suivant demandè
                    
                    """,
                tools=[],
                agent=agent,
            )
            crew = Crew(
                agents=[agent],
                tasks=[task]
            )
            
            st.write(crew.kickoff())