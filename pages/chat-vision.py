import streamlit as st
from box8.Session import APP_PATH, init_session, init_session_llm_vision
from box8.Chats import BasicImageChatter
from PIL import Image
import base64
import io


st.set_page_config(page_title="Analyse d'Image", page_icon="👀", layout="wide") 
init_session()



# Fonction pour convertir une image uploadée en base64
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Interface Streamlit
st.title("Chat avec une image 👀")

# Composant uploader d'image
uploaded_file = st.sidebar.file_uploader("Choisissez une image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Afficher l'option de choix du modèle de vision
    

    # Convertir l'image uploadée en base64
    image = Image.open(uploaded_file)
    image_base64 = image_to_base64(image)

    # Instancier la classe ImageChatter avec l'image en base64
    image_chatter = BasicImageChatter(uploaded_file)

    # Afficher l'image
    st.image(uploaded_file, caption="uploaded file")

    # Récupérer la réponse du modèle
    response = image_chatter.chat()
