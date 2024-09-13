import base64
import streamlit as st
from PIL import Image
import io
from langchain.chains.conversation.base import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from utils.Session  import *





init_session()


class BasicChat():
    def __init__(self, context="Vous êtes un assistant technique."):
        self.llm = ChooseLLM()
        self.history = []
        self.context = context
        self.setContext(self.context)
        
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
        mots = text.split()
        for mot in mots:
            yield mot + " "
            
            
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
                    response = st.write_stream(self.stream(e))
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









class ImageChatter ():
    def __init__(self, image_path):
        # Initialiser la session et choisir le modèle de vision
        
        self.llm = ChooseLLM()
        self.history = []
        self.context = "Vous êtes un assistant technique."
        
        self.llm = ChooseVisionLLM()
        self.image_base64 = image_base64
        self.image = self.decode_image()
        

    def decode_image(self):
        # Convertir l'image base64 en un objet PIL Image
        image_data = base64.b64decode(self.image_base64)
        image = Image.open(io.BytesIO(image_data))
        return image

