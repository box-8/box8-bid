import base64
import streamlit as st
from PIL import Image
import io
from langchain import OpenAI, ConversationChain
from langchain.chains.conversation.memory import ConversationBufferMemory
from utils.Session  import init_session_llm_vision, ChooseVisionLLM

class ImageChatter:
    def __init__(self, image_base64):
        # Initialiser la session et choisir le modèle de vision
        init_session_llm_vision()
        self.model = ChooseVisionLLM()
        self.image_base64 = image_base64
        self.image = self.decode_image()
        
        # Initialiser la mémoire de la conversation pour gérer le fil de discussion
        self.memory = ConversationBufferMemory(return_messages=True)
        self.conversation = ConversationChain(
            llm=self.model,
            memory=self.memory
        )

    def decode_image(self):
        # Convertir l'image base64 en un objet PIL Image
        image_data = base64.b64decode(self.image_base64)
        image = Image.open(io.BytesIO(image_data))
        return image

    def display_image(self):
        # Afficher l'image dans Streamlit
        st.image(self.image, caption="Image chargée", use_column_width=True)

    def chat_with_image(self, prompt):
        # Intégrer le prompt de l'utilisateur dans la chaîne de conversation
        response = self.conversation.run(f"Image analysée: {prompt}")
        return response

    def get_conversation_history(self):
        # Récupérer l'historique de la conversation
        return self.memory.load_memory_variables({})["history"]
