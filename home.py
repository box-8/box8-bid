import streamlit as st


# ---  init session ---
if 'llm_model' not in st.session_state:
    st.session_state.llm_model = 'openai'  # ou tout autre modèle par défaut  st.session_state.llm_model = "openai"


st.set_page_config(page_title="Analyse d'Offres et d'URL", page_icon="🔍") 
st.title("Box 8 : la boite à outils du consultant augmenté")
st.subheader(st.session_state.llm_model)
    

tab1, tab2 = st.tabs(["Home","Options"])


with tab2:
    st.subheader("Options")
    model = st.sidebar.radio(
            "Choose LLM",
            ["openai", "groq", "local"],
            captions=[
                "OpenIA via system variable",
                "Groq via system variable",
                "Ollama local instance of Mistral 7b",
            ],
        )
    st.session_state.llm_model = model
        # if llm_model_name == "":
        #     st.session_state.llm_model = "gpt-4o-mini"
        
        # elif : 
        #     # self.base_url= "groq"
        #     # self.api_key=st.secrets["GROQ_API_KEY"]
        #     # self.llm = ChatGroq(temperature=0, groq_api_key=self.api_key, model_name="mixtral-8x7b-32768")
        # else:
        # #     self.base_url = "http://localhost:1552/v1"  # Base URL pour le LLM local
        # #     self.llm = OpenAI(base_url=self.base_url, api_key="not-needed") # Point to the local server
        # # st.write(f"You selected ({self.llm_model_name}) model.")
        
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
        st.page_link("pages/analyse-medicale.py")
