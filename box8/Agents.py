from crewai import Agent, Task, Crew, Process
from crewai_tools import PDFSearchTool
from box8.Session import *
from box8.Functions import DocumentWriter, extraire_tableau_json
import fitz

init_session()




def normalize_crew_result(result):
    
    # Normaliser le résultat sous forme de chaîne de caractères
    if isinstance(result, tuple):
        # Si le résultat est un tuple, on le rejoint avec des sauts de ligne
        result = "\n".join(map(str, result))
    elif isinstance(result, list):
        # Si c'est une liste, on la convertit également en chaîne
        result = "\n".join(result)
    elif isinstance(result, dict):
        # Si c'est un dictionnaire, formater chaque paire clé-valeur
        result = "\n".join(f"{key}: {value}" for key, value in result.items())
    else:
        # Assurer que le résultat est bien une chaîne
        result = str(result)
    return result










###############################################################################################
###############################################################################################
# --- Classe RagPdf ---
###############################################################################################
###############################################################################################
class Rag():
    def __init__(self, tool: PDFSearchTool = None):
        self.tool = tool
        self.answer = ""
        self.research_agent = Agent(
            role="Assistant de recherche",
            goal="Trouver les éléments pertinents à une question en recherchant dans un document",
            allow_delegation=False,
            verbose=True,
            backstory=(
                """
                L'agent de recherche est compétent pour rechercher et extraire des données d'un document.
                Si aucun information n'est pertinente, il le précise en majuscules
                """
            ),
            tools=[self.tool],
            llm = ChooseLLM()
        )
    
    def set_doc(self, path):
        self.tool = PDFSearchTool(path=path)
        self.__init__(tool = self.tool)
         
    
    def ask(self,question):
        # --- Tasks ---
        self.task = Task(
            description=(
                """
                Répondez à la question ci-dessous en vous basant uniquement sur les informations présentes dans le document :
                {customer_question}
                """
            ),
            expected_output="""
                Une réponses claire et concise à la question basées strictement sur le texte à analyser.
                Répondez dans la langue de la question
                """,
            tools=[self.tool],
            agent=self.research_agent,
        )
        # --- Crew ---
        self.crew = Crew(
                agents=[self.research_agent],
                tasks=[self.task],
                process=Process.sequential,
            )
        try : 
            result = self.crew.kickoff(inputs={"customer_question": question})
            self.answer = normalize_crew_result(result)
            return self.answer
        except Exception as e:
            print(f"Erreur lors de l'appel à Rag : {e}")
            # st.write(result)
            return e 

    
    
    
    

###############################################################################################
###############################################################################################
# --- Classe RagPdf ---
###############################################################################################
###############################################################################################
class RagPdf(Rag):
    def __init__(self, path):
        tool = PDFSearchTool(pdf=path)
        super().__init__(tool)







###############################################################################################
###############################################################################################
# --- Classe RagAgent ---
###############################################################################################
###############################################################################################
class RagAgent() :
    def __init__(self, tool: PDFSearchTool = None):
        self.tool = tool
        
        self.research_agent = Agent(
            role="Agent de Recherche",
            goal="Rechercher dans le PDF pour trouver des réponses pertinentes",
            allow_delegation=False,
            verbose=True,
            backstory=(
                """
                L'agent de recherche est compétent pour rechercher et 
                extraire des données des documents, garantissant des réponses précises sur des éléments pertinents.
                """
            ),
            tools=[self.tool],
            llm = ChooseLLM()
        )

            
        self.professional_writer_agent = Agent(
            role="Rédacteur Professionnel",
            goal="Rédiger des réponses professionnelles basés sur les résultats de l'agent de recherche",
            allow_delegation=False,
            verbose=True,
            backstory=(
                """
                L'agent rédacteur professionnel possède d'excellentes capacités rédactionnelles.
                Il rédige des réponses claires et concises uniquement basées sur les informations fournies.
                Si une information n'est pas disponible dans le texte fourni, 
                l'Agent rédacteur professionnel le précise clairement dans un paragraphe et en lettres majuscules.
                """
            ),
            tools=[],
            llm = ChooseLLM()
        )
        
        self.crewresult = ""

    def answer(self,question): 
        global docAnalyse
        # --- Tasks ---
        self.answer_customer_question_task = Task(
            description=(
                """
                Répondez à la question ci-dessous en vous basant uniquement sur les informations présentes.
                Si aucune indication n'existe sur la question posée, précisez-le. 
                Voici la question (répondez dans la langue de la question) :
                {customer_question}
                """
            ),
            expected_output="""
                Fournir des réponses claires et concises aux questions basées strictement sur le texte à analyser.
                """,
            tools=[self.tool],
            agent=self.research_agent,
        )

        self.write_email_task = Task(
            description=(
                """
                Reprendre les conclusions de l'agent de recherche et en rédiger la synthèse.
                """
            ),
            expected_output="""
                Rédiger un texte clair concis.
                """,
            tools=[],
            agent=self.professional_writer_agent,
        )

        # --- Crew ---
        self.crew = Crew(
                agents=[self.research_agent, self.professional_writer_agent],
                tasks=[self.answer_customer_question_task, self.write_email_task],
                process=Process.sequential,
            )
        try : 
            result = self.crew.kickoff(inputs={"customer_question": question})
            result = normalize_crew_result(result)
            return result
        except Exception as e:
            print(f"Erreur lors de l'appel à RagAgent : {e}")
            return e 











###############################################################################################
###############################################################################################

# résumé de pdfs
# input Et soit le chemin du fichier soit un file upload en streamlit
# ###############################################################################################
###############################################################################################
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
            self.usage = "os"
            self.path = input
            self.document = fitz.open(self.path)
            self.documentName = os.path.basename(self.path)
            self.total_pages = self.document.page_count
            self.final_text.append(self.path)
        elif input is not None:
            # en st on a importé un fichier
            try:
                self.usage = "st"
                self.ok = True
                self.document = fitz.open(stream=input.read(), filetype="pdf")
                self.documentName = input.name
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
                role="Summarize text",
                goal="Summarize each page of a document ",
                allow_delegation=False,
                verbose=True,
                backstory=(
                    """
                    We want to have a reader digested summary of a big document
                    """
                ),
                llm = ChooseLLM()
            )
            self.store()
            #self.summarize()
        
        
    def store(self):
        for page_number in range(self.total_pages):
            page = self.document.load_page(page_number)
            self.initial_text.append(page.get_text())
    
    def summarize(self):
        textbefore = None  # Initialisation pour le premier texte
        for i, text in enumerate(self.initial_text):  
            self.sumupPage(i, text, textbefore)
            textbefore = text
    
    
    def sumupPage(self,actual_page, text,textbefore):
        # --- Tasks ---
        # print(text)
        self.task_summarize = Task(
            description=(
                """
                Summarize in two paragraphs MAXIMUM and in the same language the following text  :
                 "{initial_text} 
                 Page {actual_page}"
                """
            ),
            expected_output="""
                A strict, clear and concise summary strictly based on the text provided.
                Answer in the language of the provided text.
                """,
            agent=self.agent_summarizer,
        )
        st.toast(f"Analysis page {actual_page} by : " + st.session_state.llm_model)
        # --- Crew ---
        self.crew = Crew(
                agents=[self.agent_summarizer],
                tasks=[self.task_summarize],
                process=Process.sequential,
            )
        try : 
            result = self.crew.kickoff(inputs={"initial_text": text,"actual_page": actual_page})
            result = normalize_crew_result(result)
            self.final_text.append(result)
            if self.usage == "st":
                st.subheader(f"page {actual_page}")
                st.write(result)
            return result
            
        except Exception as e:
            print(f"Erreur lors de l'appel à Rag : {e}")
            # st.write(result)
            return e 
        
    def save(self, name = None):
        doc = DocumentWriter(self.documentName + " nombre de pages " + str(self.total_pages) )
        
        for sumup in self.final_text:
            doc.writeBlack(sumup)
        if name :
            doc.saveDocument( os.path.join("uploads",self.documentName) )
        else:
            doc.saveDocument( os.path.join("uploads",self.documentName) )
        
        return doc
    
    def show(self):
        result = "" 
        for sumup in self.final_text:
            result = result + " " +sumup 
        return result
        
        












###############################################################################################
###############################################################################################
# --- Classe Commercial ---

###############################################################################################
###############################################################################################
class Commercial() :
    def __init__(self, name: str = "", offre: PDFSearchTool = None):
        self.name = name
        self.offre = offre
        
        self.research_agent = Agent(
            role="Agent de Recherche",
            goal="Rechercher dans le PDF pour trouver des réponses pertinentes",
            allow_delegation=False,
            verbose=True,
            backstory=(
                """
                L'agent de recherche est compétent pour rechercher et 
                extraire des données des documents, garantissant des réponses précises et rapides.
                """
            ),
            tools=[self.offre],
            llm = ChooseLLM()
        )

            
        self.professional_writer_agent = Agent(
            role="Rédacteur Professionnel",
            goal="Rédiger des réponses professionnelles basés sur les résultats de l'agent de recherche",
            allow_delegation=False,
            verbose=True,
            backstory=(
                """
                L'agent rédacteur professionnel possède d'excellentes compétences en rédaction 
                et est capable de rédiger des réponses claires et concises en fonction des informations fournies.
                Si une information n'est pas disponible dans le texte fourni, 
                l'Agent rédacteur professionnel le précise clairement en posant une question adaptée au contexte.
                """
            ),
            tools=[],
            llm = ChooseLLM()
        )
        
        self.crewresult = ""

    def answer(self,question): 
        global docAnalyse
        # --- Tasks ---
        self.answer_customer_question_task = Task(
            description=(
                """
                Répondez à la question ci-dessous en vous basant uniquement sur l'offre fournie.
                Si L'offre ne donne aucune indication sur la question posée, précisez-le et proposez des améliorations 
                en suggérant une question adaptée. 
                Voici la question :
                {customer_question}
                """
            ),
            expected_output="""
                Fournir des réponses claires et concises aux questions strictement basées sur le contenu de l'offre à analyser.
                """,
            tools=[self.offre],
            agent=self.research_agent,
        )

        self.write_email_task = Task(
            description=(
                """
                Analysez l'offre en la comparant au cahier des charges à partir des éléments fournis : 
                1- Si L'offre ne donne aucune indication sur la question posée, précisez-le en majuscule
                2- Sinon, résumer les solutions proposées pour répondre à l'enjeu. 
                et Indiquer les manquements qui ne correspondent pas aux exigences en précisant les corrections nécessaires.
                """
            ),
            expected_output="""
                Rédiger un texte clair concis décrivant la prestation.
                """,
            tools=[],
            agent=self.professional_writer_agent,
        )

        # --- Crew ---
        self.crew = Crew(
                agents=[self.research_agent, self.professional_writer_agent],
                tasks=[self.answer_customer_question_task, self.write_email_task],
                process=Process.sequential,
            )
        try : 
            result = self.crew.kickoff(inputs={"customer_question": question})
            result = normalize_crew_result(result)
            return result
        except Exception as e:
            print(f"Erreur lors de l'appel de Commercial.answer : {e}")
            return e 










###############################################################################################
###############################################################################################
# --- Classe Consultant ---
###############################################################################################
###############################################################################################
# cctp_pdf_search_tool est de type PDFSearchTool
class Consultant():
    def __init__(self, cctp : PDFSearchTool):
        self.cctp_pdf_search_tool = cctp
        
        self.ingenieur_generaliste = Agent(
            role="Chef de projet",
            goal="Ingénieur généraliste le chef de projet pose les questions pertinentes permettant de comparer des offres",
            allow_delegation=False,
            verbose=True,
            backstory=(
                """
                Chef de projet, l'ingénieur généraliste est garant de la qualité, du  délai et du budget de réalisation.
                """
            ),
            tools=[self.cctp_pdf_search_tool],
            llm=ChooseLLM()
        )
    
    def analyse_cctp(self):
        self.expected_output_json="""
            Générer une chaîne de caractères représentant un tableau JSON des enjeux du CCTP sous forme de questions, avec la structure suivante : 
            [
                \{ 
                    "enjeu" : "titre de l'enjeu du CCTP",
                    "question" : "question à poser à l'offre du soumissionnaire pour vérifier que l'enjeux est traité plus ou moins correctement"
                \}, 
            ]

            """
        
        task_list_keypoints = Task(
            description=(""" 
                À partir du cahier des charges (CCTP), identifiez les points clés à vérifier dans les offres pour s'assurer que les enjeux sont bien pris en compte. 
                """),
            expected_output=self.expected_output_json,
            tools=[self.cctp_pdf_search_tool],
            agent=self.ingenieur_generaliste,                
        )
        
        self.crew = Crew(
            agents=[self.ingenieur_generaliste],
            tasks=[task_list_keypoints],
            process=Process.sequential,
            full_output=True,
            verbose=True,
            )
        
        try :
            self.crew_output = self.crew.kickoff()
            self.questionnements = []
            RAW = self.crew_output.raw
            self.questionnements = extraire_tableau_json(RAW)
            return self.questionnements
        except Exception as e:
            print(f"Erreur lors de l'appel de Consultant.analyse_cctp : {e}")
            return e 