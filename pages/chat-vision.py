import json
import os
import streamlit as st
from box8.Chats import Imagevisionbot
from box8.Functions import extraire_tableau_json

st.set_page_config(page_title="Analyse d'image", page_icon="👀", layout="wide") 
st.title("Box 8 : analyse d'image 👀")

# Instancier le visionbot
if "visionbot" not in st.session_state:
    st.session_state.visionbot = Imagevisionbot(os.getenv("OPENAI_API_KEY"))
visionbot = st.session_state.visionbot

checkboxContainer = st.container()





def makePrompt(question):
    prompt = f"""
        Vous allez analyser l'image suivante et répondre à la question associée.
        Question : {question}
        Veuillez formater la réponse sous la forme d'un JSON structuré :
        {{
            "response": "réponse à la question",
            "objects_detected": [{{
                "objet": "nom de l'objet",
                "score": "Score de confiance"
                }}
            
        }}
        Retournez uniquement du JSON et aucune autre explication.
        """
    return prompt


def doOption(visionbot, prompts):
    if prompts =="sécurité":
        question = f"""
        Quelles non conformités de chantier voyez vous sur cette image ?
        Veuillez formater la réponse sous la forme d'une liste JSON structurée :
        [
            {{
                "non_compliance": "description de chaque conformité de sécurité",
                "gravity": "Score de gravité de la non conformité sur une échelle de 1 (oubli) à 5 (grave manquement)"
            }},
            ...
        ]
        Retournez uniquement du JSON et aucune autre explication.
        """
        response = visionbot.ask(question)
        content = response["choices"][0]["message"]["content"]
        non_compliances = extraire_tableau_json(content)
        
        for item in non_compliances:
            st.checkbox(f"{item['non_compliance']} (Gravité : {str(item['gravity'])})")

    # if prompts =="avancement":
        



prompts = st.sidebar.radio("Prompts prédéfinis",
            ["aucun","sécurité","qualité", "avancement"],

            key="vision_prompt"
        )

def main():


    # Télécharger une image via Streamlit
    uploaded_file = st.file_uploader("Choisissez une image", type=["jpg", "jpeg", "png"])

    # Champ de texte pour la question
    question = st.chat_input("Posez une question concernant l'image:")
    # Afficher l'historique de la conversation
    
                    
    if uploaded_file is not None:
        # Afficher l'image téléchargée
        st.image(uploaded_file, caption="Image téléchargée", use_column_width=True)

        # Encoder l'image en base64
        visionbot.encode_image(uploaded_file)

        # Envoyer la question avec l'image et afficher les échanges précédents
        if question:
            response = visionbot.ask(question)
            # st.write(response)
            if visionbot.conversation:
                st.write("Historique de la conversation :")
                for message in visionbot.conversation:
                    if message['role'] == "user":
                        with st.chat_message("user"):
                            st.write(message['content'])
                    else:
                        with st.chat_message("AI"):
                            st.write(message['content'])
        
        if st.sidebar.button("Go"):
            doOption(visionbot, prompts)
        
        
        
        
        
                
if __name__ == "__main__":
    main()
