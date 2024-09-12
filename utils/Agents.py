from crewai import Agent, Task, Crew, Process
from crewai_tools import PDFSearchTool
from utils.Session import *
from utils.Functions import extraire_tableau_json

init_session()



class RagAgent() :
    def __init__(self, name: str = "", tool: PDFSearchTool = None):
        self.name = name
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
        except Exception as e:
            print(f"Erreur lors de l'appel à RagAgent : {e}")
            return e 



# --- Classe Commercial ---
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
        except Exception as e:
            print(f"Erreur lors de l'appel de Commercial.answer : {e}")
            return e 





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