from crewai import Agent, Task, Crew, Process
from crewai_tools import PDFSearchTool


# --- Classe Commercial ---
class Commercial() :
    def __init__(self, offre : PDFSearchTool):
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
        )
        
        self.crewresult = ""

    def ask(self, enjeu, question): 
        global docAnalyse
        # --- Tasks ---
        self.answer_customer_question_task = Task(
            description=(
                """
                Répondez aux questions du  basées sur le PDF de l'offre.
                L'agent de recherche cherchera dans le PDF pour trouver les réponses pertinentes.
                Votre réponse finale DOIT être claire et précise, basée sur le contenu du PDF de l'offre.
                Si l'offre ne répond pas à la question posée, il faut le préciser et proposer d'ajuster l'offre au moyen d'une question adaptée
                Sur l'enjeu {enjeu}, voici la question du client :
                {customer_question}
                """
            ),
            expected_output="""
                Fournir des réponses claires et précises aux questions du client strictement basées sur le contenu du PDF de l'offre.
                """,
            tools=[self.offre],
            agent=self.research_agent,
        )

        self.write_email_task = Task(
            description=(
                """
                Rédiger une analyse fine du contenu de l'offre comparativement à la demande du cahier des charges :  
                - basé sur les résultats de l'agent de recherche.
                - L'analyse doit indiquer clairement les solutions mise en oeuvre dans le devis pour cadrer avec l'enjeu.
                - Argumenter d'après les de manière à répondre aux questions soulevées dans par l'enjeu
                - Si le devis ne cadre pas avec les enjeiux du cahier des charges, il faut le préciser en indiquant que l'offre doit être corrigée
                """
            ),
            expected_output="""
                Rédiger un texte clair et concis en réponse au client pour justifier la prestation.
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
    
        result = self.crew.kickoff(inputs={"customer_question": question, "enjeu":enjeu})

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


