import streamlit as st
from utils.Session import init_session
init_session()
st.set_page_config(page_title="Analyse d'Offres et d'URL", page_icon="🤖", layout="wide") 

st.title("Box 8 : boite à outils")



selected_llm = st.sidebar.radio(
        "Choose LLM",
        st.session_state.llm_allowed,
        captions=st.session_state.llm_allowed_def,
        key="selected_llm_options"
    )
if selected_llm :
    st.session_state.llm_model = selected_llm
    
    
    
tab1, tab2 = st.tabs(["Home","Options"])

with tab2:
    st.subheader("Options")
    


st.toast(st.session_state.llm_model)

with tab1:
    st.subheader("Analyse approfondie d'offres commerciales et d'URL")
    st.image("images/logo.png", width=150)
    st.markdown("""
    Cette application vous permet de :

    * **Analyser des offres** : Téléchargez un document d'offre (PDF, Word, etc.) et obtenez un résumé des points clés, des clauses importantes et des informations financières.
    * **Explorer des URL** : Collez une URL et obtenez un aperçu du contenu de la page, des mots-clés pertinents et des informations sur le site web.
    **Commencez dès maintenant !** 
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.page_link("pages/analyse-offre.py") 
        
        
    with col2:
        st.page_link("pages/compte-rendu-chantier.py")
