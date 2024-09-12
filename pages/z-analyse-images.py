import streamlit as st
from utils.Chats import ImageChatter
from PIL import Image
import base64
import io

# Fonction pour convertir une image uploadée en base64
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Interface Streamlit
st.title("Chat avec une image et fil de discussion")

# Composant uploader d'image
uploaded_file = st.file_uploader("Choisissez une image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Afficher l'option de choix du modèle de vision
    

    # Convertir l'image uploadée en base64
    image = Image.open(uploaded_file)
    image_base64 = image_to_base64(image)

    # Instancier la classe ImageChatter avec l'image en base64
    image_chatter = ImageChatter(image_base64)

    # Afficher l'image
    image_chatter.display_image()

    # Créer un champ de texte pour chatter avec l'image
    user_input = st.text_input("Posez une question à propos de l'image:")

    if user_input:
        # Récupérer la réponse du modèle
        response = image_chatter.chat_with_image(user_input)
        st.write(f"Réponse du modèle : {response}")

        # Afficher l'historique de la conversation
        st.write("Historique de la conversation :")
        conversation_history = image_chatter.get_conversation_history()
        st.write(conversation_history)
