import streamlit as st
from utils.Session import *


st.set_page_config(page_title="Analyse d'Offres et d'URL", page_icon="🤖", layout="wide") 

init_session()


st.title("Box 8 : boite à outils")
    
    
    
tab1, tab2 = st.tabs(["Home","Models"])

with tab2:
    
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Models de langage")
        ui_options_llmModel(sidebar=False)
    with col2:
        st.subheader("Models de vision")
        ui_options_visionModel(sidebar=False)
    
with tab1:
    st.subheader("Analyse approfondie d'offres commerciales et d'URL")
    st.image("images/logo.png", width=150)
    st.markdown("""
    Cette application vous permet de :

    * **Gere des projets de construction ** : Téléchargez un document d'offre (PDF, Word, etc.) et obtenez un résumé des points clés, des clauses importantes et des informations financières.
    * **Discuter avec vos documnents ** : Collez une URL et obtenez un aperçu du contenu de la page, des mots-clés pertinents et des informations sur le site web.
    **Commencez dès maintenant !** 
    """)

    # col1, col2 = st.columns(2)

    # with col1:
    #     st.page_link("pages/analyse-offre.py") 
        
        
    # with col2:
    #     st.page_link("pages/compte-rendu-chantier.py")
