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


def makeTeck(specialité = "électricité"):
 return Agent(
            role=f"Technicien {specialité}",
            goal=f"Rédaction des procédures de mise en service {specialité}",
            allow_delegation=False,
            verbose=True,
            backstory=(
                f"""
                Le technicien intervient dans le cadre de la mise en service l'installation
                Pour cela il rédige les documents et les spécifications fonctionnelles visant à mettre en service
                tous les équipements du groupes fonctionnels {specialité}.
                """
            ),
            tools=[],
            llm = ChooseLLM()
        )
 
 
def do(uploaded_file):
    
        # Read the file and prepare the data for PDFSearchTool
        # PDF Search Tool setup
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
            f.write(uploaded_file.read())
        uploaded_file_path = f.name
        pdf_tool = PDFSearchTool(pdf=uploaded_file_path)
        
        Commissioneur = Agent(
                role="Responsable mise en service",
                goal="Établir la procédure de mise en service de systèmes complexes",
                allow_delegation=False,
                verbose=True,
                backstory=(
                    """
                    Le responsable de mise en service intervient dans le cadre de la construction d'un équipement technique  
                    au moment de la mise en service l'installation.
                    Pour cela : 
                    Sur la base de la spécification technique 
                    Il définit tous les groupes fonctionnels nécessaires au fonctionnement de l'unité.
                    Il coordonne le savoir faire des techniciens spécialisés dédiés la rédaction des sous tâches de la mise en service.
                    """
                ),
                tools=[pdf_tool],
                llm = ChooseLLM()
            )
        
        
        rédigerProcédure = Task(
                description=(""" 
                    À partir du cahier des charges rédiger la procédure de mise en service. 
                    """),
                expected_output="""
                Retourner un tableau JSON des tâches a accomplir pour mettre en service l'installation.
                ["
                    \{ 
                        "task" : "description de la tâche à accomplir",
                        "techniciens":[{{
                            "technicien électricité" : "que doit faire le technicien spécialisé",
                            "technicien thermique" : "que doit faire le technicien spécialisé",
                            ...
                        }}]
                    \},
                    ... 
                ]

                """,
                tools=[pdf_tool],
                agent=Commissioneur,                
            )

        elecTechnicien = makeTeck(specialité = "électricité")
        thermiqueTechnicien = makeTeck(specialité = "thermique")
        # Form a crew and kick off the process
        crew = Crew(
            agents=[Commissioneur],
            tasks=[rédigerProcédure],
            process=Process.sequential
        )

        # Run the agent and display results in Streamlit
        result = crew.kickoff()
        
        st.write(result)
        
        try :
            RAW = result.raw
            questionnements = extraire_tableau_json(RAW)
            st.write(questionnements)
        except Exception as e:
            print(f"Erreur lors de l'appel de Consultant.analyse_cctp : {e}")
            return e 

        
