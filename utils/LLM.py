from crewai_tools import PDFSearchTool
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun


class LLMFactory:
    def Groq(self, model="mixtral-8x7b-32768"):
        GROQ_API_KEY = load_dotenv("GROQ_API_KEY")
        llm =  ChatGroq(
            temperature=0.7, 
            groq_api_key=GROQ_API_KEY, 
            model_name=model
            )
        return llm
    
    def LMStudio(self):    
        llm = ChatOpenAI(
            temperature=0.7,
            openai_api_base="http://localhost:1234/v1",
            openai_api_key="",
            model_name="mistral"
        )
        return llm
    
    def OpenAI(self):
        API_KEY = load_dotenv("OPENAI_API_KEY")
        llm = ChatOpenAI(
            temperature=0.7,
            openai_api_base="https://api.openai.com/v1",  # Le point de terminaison de l'API OpenAI
            openai_api_key=API_KEY,  # Remplace par ta clé API OpenAI
            model_name="gpt-4",  # Utilise GPT-4 par exemple, ou un autre modèle supporté
        )
        return llm

    











# class PDFSearchToolFactory:
#     def __init__(self, llm_provider="openai", model="gpt-3.5-turbo", base_url=None, api_key=None):
#         """
#         Initialise la classe avec les configurations par défaut pour OpenAI.
#         :param llm_provider: Le fournisseur du LLM. Peut être "openai" (par défaut), "local", ou "groq".
#         :param model: Le modèle à utiliser (par exemple, "gpt-3.5-turbo" pour OpenAI, "mistral" pour Groq).
#         :param base_url: L'URL de base pour un modèle LLM local.
#         :param api_key: La clé API si nécessaire (pour OpenAI par exemple).
#         """
#         self.llm_provider = llm_provider
#         self.model = model
#         self.base_url = base_url
#         self.api_key = api_key

#     def create_pdf_search_tool(self):
#         if self.llm_provider == "local":
#             return self._create_local_pdf_search_tool()
#         elif self.llm_provider == "groq":
#             return self._create_groq_pdf_search_tool()
#         else:
#             return self._create_openai_pdf_search_tool()

#     def _create_openai_pdf_search_tool(self):
#         """Crée un objet PDFSearchTool utilisant OpenAI par défaut."""
#         return PDFSearchTool(
#             config=dict(
#                 llm=dict(
#                     provider="openai",
#                     config=dict(
#                         model=self.model,
#                         api_key=self.api_key,
#                         # temperature=0.5, 
#                         # top_p=1, 
#                         # stream=true,
#                     ),
#                 ),
#                 embedder=dict(
#                     provider="openai",
#                     config=dict(
#                         model="text-embedding-ada-002",
#                         task_type="retrieval_document",
#                     ),
#                 ),
#             )
#         )

#     def _create_local_pdf_search_tool(self):
#         """Crée un objet PDFSearchTool utilisant un LLM local."""
#         return PDFSearchTool(
#             config=dict(
#                 llm=dict(
#                     provider="custom",
#                     config=dict(
#                         base_url=self.base_url or "http://localhost:1552/v1",
#                         api_key=self.api_key or "no_key",
#                         model=self.model,
#                     ),
#                 ),
#                 embedder=dict(
#                     provider="local",
#                     config=dict(
#                         model="local-embedding-model",
#                         task_type="retrieval_document",
#                     ),
#                 ),
#             )
#         )

#     def _create_groq_pdf_search_tool(self):
#         """Crée un objet PDFSearchTool utilisant l'API Groq pour Mistral."""
#         chat_groq = ChatGroq(model=self.model)  # Utilisation de langchain_groq
#         return PDFSearchTool(
#             config=dict(
#                 llm=dict(
#                     provider="groq",
#                     config=dict(
#                         model=self.model,
#                         instance=chat_groq,
#                     ),
#                 ),
#                 embedder=dict(
#                     provider="groq",
#                     config=dict(
#                         model="groq-embedding-model",
#                         task_type="retrieval_document",
#                     ),
#                 ),
#             )
#         )

# # Exemple d'utilisation
# factory = PDFSearchToolFactory(llm_provider="local", model="mistral", base_url="http://localhost:1552/v1")
# pdf_search_tool = factory.create_pdf_search_tool()
