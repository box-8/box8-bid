import streamlit as st
import base64
from utils.BasicChat import BasicChat
from openai import OpenAI



class AppVision(BasicChat):
  
    def __init__(self) -> None:
        # Initialisation de la classe de base et de l'API locale
        super()._init("Vision", "👀")
        
        self.context = "Vous êtes un ingénieur en construction qui analyse des photos de chantier."
        self.setOpenaAI()
        self.llm_model_name = st.sidebar.radio(
            "Choose Vision LLM",
            ["gpt-4o-mini", "local-model"],
            captions=[
                "Opena IA Vision model, via system variable OPENAI_API_KEY",
                "Local Phi 3-5 on port 1552. No API key",
            ],
        )

        if self.llm_model_name == "gpt-4o-mini":
            self.setOpenaAI()
        else:
            self.base_url = "http://localhost:1552/v1"  # Base URL pour le LLM local
            self.llm = OpenAI(base_url=self.base_url, api_key="not-needed") # Point to the local server
        st.write(f"You selected ({self.llm_model_name}) model.")
            
    def setOpenaAI(self):
        self.base_url = "https://api.openai.com/v1/chat/completions"  # Base URL pour le LLM local
        # Point to opena AI server
        # assuming  opean ai is reading from local variables
        self.llm = OpenAI()
    
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

    
    
if __name__ == "__main__":
    app = AppVision()
    app.main()