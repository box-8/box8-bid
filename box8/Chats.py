import base64
import streamlit as st
from PIL import Image
import io
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
    # tofo implementer l'usage d'une question non inscrite dans l'historique de conversation
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


# TODO
class BasicImageChatter(BasicChat):
  
    def __init__(self, context="Vous êtes un ingénieur en construction qui analyse des photos de chantier."):
        self.history = []
        self.context = context
        self.setContext(self.context)
        self.llm = ChooseVisionLLM() # Initialisation du LLM Cision

        
    def main(self):
        # Interface utilisateur pour télécharger une image
        
        self.uploaded_doc = st.file_uploader("Télécharger une image", type=["jpg", "png", "bmp", "jpeg"])
        if self.uploaded_doc is not None:
            # Si un fichier est uploadé, passer à la discussion
            st.sidebar.image(self.uploaded_doc, caption="uploaded file")
            self.chat()

    
    
    def ask(self, query):
        if self.uploaded_doc is not None:
            try:
                # Encodage de l'image en base64
                image = self.uploaded_doc.read()
                self.base64_image = base64.b64encode(image).decode("utf-8")
                # Envoyer la requête au modèle avec l'image et la question
                return self.get_response(query)
            except Exception as e:
                return f"Erreur lors de la lecture de l'image: {e}"
        else:
            return "Veuillez télécharger une image avant de poser une question."

    
    def completion(self, query=""):
        
        messages = [
                {
                "role": "system",
                "content": self.context,
                },
                {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"{query}"},
                    {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{self.base64_image}"
                    },
                    },
                ],
                }
            ]
        print(messages)
        return self.llm.chat.completions.create(
            model=self.llm_model_name, # not used
            messages=messages,
            max_tokens=1000,
            stream=True,
            )
        
    def get_response(self, query=""):
        # Génération de la requête avec le modèle
        if query =="":
            return ""
        try:
            # Création du payload pour l'API LLM local
                        
            completion = self.completion()
            
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk
        except Exception as e:
            return f"Erreur lors de l'envoi de la requête: {e}"

    



# class ImageChatter ():
#     def __init__(self, image_path):
#         # Initialiser la session et choisir le modèle de vision
        
#         self.llm = ChooseLLM()
#         self.history = []
#         self.context = "Vous êtes un assistant technique."
        
#         self.llm = ChooseVisionLLM()
#         self.image_base64 = image_base64
#         self.image = self.decode_image()
        

#     def decode_image(self):
#         # Convertir l'image base64 en un objet PIL Image
#         image_data = base64.b64decode(self.image_base64)
#         image = Image.open(io.BytesIO(image_data))
#         return image

