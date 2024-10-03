from io import BytesIO
import os
from typing import List
from crewai import Agent, Crew, Process, Task
import streamlit as st 
import tempfile
from crewai_tools import PDFSearchTool
from box8.Session import *
from box8.Agents import Commercial, Consultant, RagAgent
from box8.Functions import toast, extraire_tableau_json, DocumentWriter

 
def do(uploaded_file):
    
        # Read the file and prepare the data for PDFSearchTool
        # PDF Search Tool setup
        doc = DocumentWriter()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
            f.write(uploaded_file.read())
        uploaded_file_path = f.name
        pdf_tool = PDFSearchTool(pdf=uploaded_file_path)
        
        # Création des agents
        agent_tech_genlecture = Agent(
            role="Expert Technique Ingéniérie",
            goal="""
            Synthétiser la fiche technique de l'équipement.""",
            verbose=True,
            memory=True,
            backstory="""
            Ingénieur en génie électromécanique et génie des procédés, vous avez une grande expertise dans l'analyse de 
            systèmes techniques complexes et faites appel à vos compétences de synthèse technique.
            """,
            max_iter=5,
            tools=[pdf_tool],
            llm = ChooseLLM()
        )
        agent_tech_genlecturetask = Task(
            description="Lire la documentation technique et synthétiser son contenu.",
            expected_output="""
            Un descriptif synthétique de la fiche d'équipements.""",
            agent=agent_tech_genlecture,
        )
        
        # Création des agents
        agent_tech_lecture = Agent(
            role="Expert Technique Ingéniérie",
            goal="""
            Identifier les composants techniques qui devront être inclus dans le processus de mise en service (commissionning) 
            d'aprés la fiche technique.
            Si la fiche technique n'indique pas de sous-équipements faites appel à vos connaissances 
            pour déterminer une décomposition en sous équipements.""",
            verbose=True,
            memory=True,
            backstory="""
            Ingénieur en génie électromécanique et génie des procédés, vous avez une grande expertise dans l'analyse de 
            systèmes techniques complexes et faites appel à vos connaissances pour déterminer 
            la composition d'un équipement en vue de sa mise en service (électricité, 
            instrumentation de mesure, instrumentation de régulation, organes mécaniques ...).
            """,
            max_iter=5,
            tools=[pdf_tool],
            llm = ChooseLLM()
        )
        agent_tech_lecturetask = Task(
            description="Lire la documentation technique et déterminer la composition de l'équipement.",
            expected_output="""
            Une liste avec l'intitulé du type d'équipement décrivant les composants et groupes 
            fonctionnels, organisée dans l'ordre de leur mise en service.""",
            agent=agent_tech_lecture,
        )
        
        
        crew = Crew(
            agents=[agent_tech_genlecture,agent_tech_lecture],
            tasks=[agent_tech_genlecturetask, agent_tech_lecturetask],
            process=Process.sequential  # Exécution séquentielle des tâches
        )
        
        part1 = "Groupes fonctionnels / équipements"
        st.subheader(part1)
        result = crew.kickoff()
        st.write(result.raw)
        
        doc.Chapter(part1)
        doc.writeBlack(result.raw)
        
        
        commissionning_agent = Agent(
            role="Ingénieur Mise en Service Commissionning",
            goal=f"""
            Rédiger une procédure de mise en service détaillée de l'équipement sachant qu'il comporte les éléments suivants :
            {result.raw} 
            Détailler des essais de contrôle de mise en service et de performance pour chacun d'eux
            """,
            verbose=True,
            memory=True,
            backstory="""
            Vous avez une grande expérience dans la mise en service de systèmes 
            industriels (chaleur, pétrochimie, pompage, énergie, transport, industrie manufacturière).
            """,
            max_iter=5,
            llm = ChooseLLM()
        )
        
        commissionning_agenttask = Task(
            description="Pour chaque composant de la liste décrire les tâches et actions à réaliser pour sa mise en service.",
            expected_output="""
            Une procédure de mise en service avec des instructions précises pour la mise en service. 
            """,
            agent=commissionning_agent,
            async_execution=False,  # S'exécute séquentiellement
        )
        crew = Crew(
            agents=[commissionning_agent],
            tasks=[commissionning_agenttask],
            process=Process.sequential  # Exécution séquentielle des tâches
        )
        
        part2 = "Mise en service / équipements"
        st.subheader(part2)
        result = crew.kickoff()
        st.write(result.raw)
        
        doc.Chapter(part2)
        doc.writeBlack(result.raw)
        
        
        redactor_agent = Agent(
            role="Technicien de Mise en Service",
            goal=f"""
            A partir de la liste ci aprés, décrire tâche par tâche le détail de la procédure de mise en service.
            Proposer des essais de performance pour chacun d'eux :
            {result.raw} 
            
            """,
            verbose=True,
            memory=True,
            backstory="""
            Vous avez une grande expérience dans la mise en service de systèmes 
            industriels (chaleur, pétrochimie, pompage, énergie, transport, industrie manufacturière).
            Vous entrez dans le détail des procédures de mise en service
            """,
            max_iter=5,
            llm = ChooseLLM()
        )
        
        redactor_agenttask = Task(
            description="""
            Pour chaque composant de la liste décrire les tâches et actions à réaliser 
            pour sa mise en service du point de vue technique, de la sécurité, de la qualité et des objectifs de performance.
            """,
            expected_output="""
            Une procédure technique de mise en service avec des instructions précises étape par étape. 
            """,
            agent=commissionning_agent,
            async_execution=False,  # S'exécute séquentiellement
        )
        # crew = Crew(
        #     agents=[agent_tech_lecture,redactor_agenttask],
        #     tasks=[agent_tech_lecturetask, redactor_agenttask],
        #     process=Process.sequential  # Exécution séquentielle des tâches
        # )
        crew = Crew(
            agents=[redactor_agent],
            tasks=[redactor_agenttask],
            process=Process.sequential  
        )
        part3 = "Détail de Mise en service"
        st.subheader(part3)
        result = crew.kickoff()
        st.write(result.raw)
        
        doc.Chapter(part3)
        doc.writeBlack(result.raw)
        
        
        if False:
            agent_verificateur = Agent(
                role="Vérificateur Qualité",
                goal=f"""
                S'assurer que la procédure est complète et conforme aux normes de rédaction technique : 
                {result.raw}
                """,
                verbose=True,
                memory=True,
                backstory="Spécialiste dans la validation de procédures techniques.",
                tools=[pdf_tool],
                llm = ChooseLLM()
                
            )
            agent_verificateurtask = Task(
                description="Vérifier la qualité de la procédure rédigée.",
                expected_output="Procédure de mise en service complète avec rapport de validation de conformité ou rapport de corrections.",
                agent=agent_verificateur,
            )
            
            crew = Crew(
                agents=[agent_verificateur],
                tasks=[agent_verificateurtask],
                process=Process.sequential  # Exécution séquentielle des tâches
            )
            
            part4 = "Vérification"
            st.subheader(part4)
            result = crew.kickoff()
            st.write(result.raw)
            doc.Chapter(part4)
            doc.writeBlack(result.raw)
        # doc.saveDocument(os.path.join("uploads","analyse-fiche-technique.docx"))
        return doc




st.set_page_config(page_title="Analyse de fiche technique", page_icon="🤖", layout="wide") 
init_session()
st.header("Mise en service")
uploaded_file_mes = st.file_uploader("Upload technical document", type="pdf")
if st.button("Analyse de la fiche technique"):
    
    # Streamlit file uploader for PDF
    
    if uploaded_file_mes :
        
        doc = do(uploaded_file_mes)
        doc.saveDocument(os.path.join("uploads","analyse-fiche-technique.docx"))
    
