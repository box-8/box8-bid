import base64
import requests
import streamlit as st
from langchain.chains.conversation.base import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate

from crewai_tools import PDFSearchTool

from box8.Agents import Rag
from box8.Functions import DocumentWriter
from box8.Session  import *


init_session()


class BasicChat():
    def __init__(self):
        self.initiate()
        
    def initiate(self):
        self.history = []
        self.context = "Vous êtes un assistant qui répond aux questions."
        self.setContext(self.context)
        self.setSessionLlm()
        
    def setSessionLlm(self):
        self.llm = ChooseLLM()
        
    def reset_history(self):
        self.history = []
        self.setContext(self.context)
        
    def setContext(self, context):
        newcontext = SystemMessage(content=context)
        if len(self.history) == 0:# If the history is empty, append the context
            self.history.append(newcontext)
        else:
            self.history[0] = newcontext# If the history has at least one element, replace the first one
        return newcontext

    def options(self,container=None):
        llm_options(self)
    
    def stream(self, text=""):
        st.write(text)
        mots = text.split()
        for mot in mots:
            yield mot + " "
            
    def saveToDoc(self):
        doc = DocumentWriter("Chat")
        doc.Chapter("context")
        doc.writeBlack(self.context)
        doc.Chapter("content")
        for i, message in enumerate(self.history):
            st.error(message.content)
            if i % 2 == 0:
                doc.writeBlue(message.content)
            else:
                doc.writeBlack(message.content)
        doc.saveDocument("Chat")
    
    # affichage de l'onglet chat simple
    def chat(self):
        # conversation
        for message in self.history:
            if isinstance(message, AIMessage):
                with st.chat_message("AI"):
                    st.write(message.content)
            elif isinstance(message, HumanMessage):
                with st.chat_message("Human"):
                    st.write(message.content)

        # user input
        user_query = st.chat_input("Type your message here...")
        if user_query is not None and user_query != "":
            self.history.append(HumanMessage(content=user_query))
            with st.chat_message("Human"):
                st.markdown(user_query)
            with st.chat_message("AI"):
                try:
                    response = st.write_stream(self.ask(user_query))
                except Exception as e:
                    response = f"({st.session_state.llm_model}) " + st.write_stream(self.stream(e))
            self.history.append(AIMessage(content=response))

    # fonction générique pour poser une question au LLM actif 
    def ask(self, query) :
        return self.get_response(query)
        
    # fonction générique pour recevoir la réponse du  LLM actif 
    # todo implementer l'usage d'une question non inscrite dans l'historique de conversation
    def get_response(self, query):
        chatactual = self.history
        prompt = ChatPromptTemplate.from_messages(chatactual)
        chain = prompt | self.llm | StrOutputParser()
        return chain.stream({})






# class to chat with a document
class BasicPdfRag(BasicChat):
    def __init__(self, path: str = None):
        self.initiate()
        self.setfileByPath(path)
        # self.tool= PDFSearchTool(pdf=path)
        # self.rag = Rag(self.tool)
    
    def setfileByPath(self, path: str):
        self.tool= PDFSearchTool(pdf=path)
        self.rag = Rag(self.tool)
        
    def ask(self, query) :
        mots = self.rag.ask(query)
        for mot in mots:
            yield mot














#############################################################################################
# VISION
#############################################################################################


class Imagevisionbot:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        self.image_base64 = "data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="
        self.conversation = []  # Stockage de l'historique des messages

    def encode_image(self, image_file):
        """Encode l'image en base64."""
        self.image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        return self.image_base64

    
    def ask(self, question, append=True):
        """Ajoute la question à la conversation et envoie à l'API OpenAI."""
        # Ajouter la question de l'utilisateur au contexte de conversation
        
        if append:
            self.conversation.append({
                "role": "user",
                "content": question
            })
        
        # Préparer la charge utile avec l'historique des messages
        payload = {
            "model": "gpt-4o-mini",  # Ajustez le modèle si nécessaire
            "messages": self.conversation + [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{self.image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }

        # Faire l'appel à l'API OpenAI
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=self.headers, json=payload)

        if response.status_code == 200:
            response_json = response.json()

            # Ajouter la réponse du modèle au contexte de la conversation
            self.conversation.append({
                "role": "assistant",
                "content": response_json['choices'][0]['message']['content']
            })

            return response_json
        else:
            return {"error": "Failed to process the request", "details": response.text}

















# # class to chat with a picture
# # Classe pour discuter avec une image
# class BasicImageChatter(BasicChat):
#     def __init__(self, image_uploaded):
#         # Appel au constructeur de la classe parente BasicChat pour initialiser `history` et les autres attributs
#         super().__init__()
        
#         # Redéfinition du contexte spécifique pour la classe BasicImageChatter
#         self.context = "Vous êtes un ingénieur en construction qui analyse des photos de chantier."
#         self.setContext(self.context)
        
#         # Initialisation du LLM spécifique pour la vision
#         self.llm = ChooseVisionLLM()  # Placeholder, à remplacer par le bon modèle de vision
#         self.uploaded_doc = image_uploaded  # Stockage de l'image téléchargée
        
#         # Lecture du fichier sans le sauvegarder localement
#         image_data = image_uploaded.getvalue()
#         # Encodage de l'image en base64
#         self.base64_image = base64.b64encode(image_data).decode("utf-8")
        
        
#     def ask(self, query):
#         if self.uploaded_doc is not None:
#             try:
#                 return self.get_response(query)
#             except Exception as e:
#                 yield f"Erreur lors de la lecture de l'image: {e}"
#         else:
#             yield "Veuillez télécharger une image avant de poser une question."

    
#     def get_response(self, query):
        
#         completion = self.llm.chat.completions.create(
#         model="local-model", # not used
#         messages=[
#             {
#             "role": "system",
#             "content": f"{self.context}",
#             },
#             {
#             "role": "user",
#             "content": [
#                 {"type": "text", "text": f"{query} "},
#                 {
#                 "type": "image_url",
#                 "image_url": {
#                     "url": f"data:image/jpeg;base64,{self.base64_image}"
#                 },
#                 },
#             ],
#             }
#         ],
#         max_tokens=1000,
#         stream=True
#         )

#         for chunk in completion:
#             if chunk.choices[0].delta.content:
#                 yield chunk.choices[0].delta.content
    
#     def get_responsess(self, query=""):
#         if query == "":
#             yield f"Popo: {query}"

#         try:
#             # Création de la complétion via la chaîne
#             completion = self.completion(query)
#             response = ''.join(completion)
#             # Retourner la complétion sous forme de générateur pour st.write_stream
#             for chunk in completion:
#                 yield chunk  # Le stream est renvoyé ici directement pour l'affichage
            
#             # Une fois la réponse complète obtenue, ajouter au contexte
            
#         except Exception as e:
#             yield f"Erreur lors de l'envoi de la requête: {e}"  
#     def completion(self, query=""):
#         # Ajout de la question dans l'historique
#         st.warning(self.base64_image)
#         # Création de la liste de messages pour le contexte du chat
#         chatactual = [
#             {"role": "system", "content": self.context},
#             {"role": "user", "content": f"{query}"},
#             {"role": "user", "content": f"![Image](data:image/jpeg;base64,{self.base64_image})"}
#         ]
        
#         # Création du prompt avec le contexte et la requête
#         prompt = ChatPromptTemplate.from_messages(chatactual)
        
#         # Utilisation de la syntaxe avec pipe (|)
#         chain = prompt | self.llm | StrOutputParser()

#         # Retour de la chaîne
#         return chain.stream({})
     
