import streamlit as st
import fitz
import time
from crewai import Agent, Task, Crew, Process
from box8.Session import *


# input Et soit le chemin du fichier soit un file upload en streamlit
class SummarizePdf():
    def __init__(self, input=None):
        if input:
            self.initiate(input)
    def initiate(self, input):
        
        # les tableaux de texte 
        self.initial_text = []
        self.final_text = []
        self.final_text.append("")
        self.ok = False
        
        if isinstance(input, str):
            self.ok = True
            self.path = input
            self.document = fitz.open(self.path)
            self.total_pages = self.document.page_count
            self.final_text.append(self.path)
        elif input is not None:
            # en st on a importé un fichier
            try:
                self.ok = True
                self.document = fitz.open(stream=input.read(), filetype="pdf")
                self.total_pages = self.document.page_count
                self.final_text.append(input.name)
            except Exception as e:
                self.usage = "error"
                self.document = None
                self.total_pages = 0
        else:
            self.usage = "error"
            self.document = None
            self.total_pages = 0 
        
        if self.ok:
            self.agent_summarizer = Agent(
                role="résumer du texte",
                goal="résumer le contenu d'un document page à page",
                allow_delegation=False,
                verbose=True,
                backstory=(
                    """
                    L'agent est compétent extraire des données d'un document et produire un résumé condensé fidèle à l'idée originale du texte.
                    """
                ),
                tools=[self.tool],
                llm = ChooseLLM()
            )
            self.store()
            self.summarize()
        
        
    def store(self):
        for page_number in range(self.total_pages):
            page = self.document.load_page(page_number)
            self.initial_text.append(page.get_text())
    
    def summarize(self):
        textbefore = None  # Initialisation pour le premier texte
        for i, text in enumerate(self.initial_text):  # i sera incrémenté automatiquement
            self.sumupPage(text, textbefore, self.final_text[i])  # Passez i à la fonction si nécessaire
            textbefore = text
    
    
    
    def sumupPage(self,text,textbefore):
        # --- Tasks ---
        self.task_summarize = Task(
            description=(
                """
                Résumer en deux paragraphes maximum le texte de la page suivante :
                {initial_text}
                """
            ),
            expected_output="""
                Un résumé clair et concis basées strictement sur le texte à fourni.
                Répondez dans la langue du texte fourni
                """,
            tools=[self.tool],
            agent=self.research_agent,
        )
        # --- Crew ---
        self.crew = Crew(
                agents=[self.agent_summarizer],
                tasks=[self.task_summarize],
                process=Process.sequential,
            )
        try : 
            result = self.crew.kickoff(inputs={"initial_text": text})
            self.final_text.append(result)
        except Exception as e:
            print(f"Erreur lors de l'appel à Rag : {e}")
            # st.write(result)
            return e 
        
    
    def show(self):
        result = "" 
        for sumup in self.final_text:
            result = result + " " +sumup 
        return result
        
        
summarizer = SummarizePdf() 

if True:
    summarizer.initiate("cctp_plomberie.pdf")
    print(summarizer.show())
else:
    # Interface Streamlit
    st.title("Affichage séquentiel du texte d'un PDF")
    uploaded_file = st.file_uploader("Téléverser un fichier PDF", type="pdf")

    if uploaded_file :
        summarizer.initiate(uploaded_file)