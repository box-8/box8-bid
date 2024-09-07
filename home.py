import streamlit as st

st.set_page_config(page_title="Analyse d'Offres et d'URL", page_icon="🔍") 

st.title("Décryptez vos Offres et Explorez le Web")
st.subheader("Analyse approfondie d'offres commerciales et d'URL")

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
    st.page_link("pages/analyse-medicale.py")