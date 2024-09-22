import os
import streamlit as st
import base64
import requests

class ImageChatBot:
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

    def ask(self, question):
        """Ajoute la question à la conversation et envoie à l'API OpenAI."""
        # Ajouter la question de l'utilisateur au contexte de conversation
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


api_key = os.getenv("OPENAI_API_KEY")
# Instancier le chatbot
    
if "chatbot" not in st.session_state:
    st.session_state.chatbot = ImageChatBot(api_key)

chatbot = st.session_state.chatbot 

def main():

    # Télécharger une image via Streamlit
    uploaded_file = st.file_uploader("Choisissez une image", type=["jpg", "jpeg", "png"])

    # Champ de texte pour la question
    question = st.chat_input("Posez une question concernant l'image:")

    if uploaded_file is not None:
        # Afficher l'image téléchargée
        st.image(uploaded_file, caption="Image téléchargée", use_column_width=True)

        # Encoder l'image en base64
        chatbot.encode_image(uploaded_file)

        # Envoyer la question avec l'image et afficher les échanges précédents
        if question:
            response = chatbot.ask(question)
            
        # Afficher l'historique de la conversation
        if chatbot.conversation:
            st.write("Historique de la conversation :")
            for message in chatbot.conversation:
                if message['role'] == "user":
                    with st.chat_message("user"):
                        st.write(message['content'])
                     
                else:
                     with st.chat_message("AI"):
                        st.write(message['content'])
                
if __name__ == "__main__":
    main()
