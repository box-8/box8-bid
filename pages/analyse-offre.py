
from box8.Session import *
from box8.Agents import Commercial, Consultant, RagAgent
from box8.Functions import toast, extraire_tableau_json, DocumentWriter
from scripts.rao import rao


st.set_page_config(page_title="Analyse d'Offres", page_icon="💵", layout="wide") 
init_session()

if st.sidebar.button("Options"):
    llm_options()



if st.button("ANALYSE D'OFFRE"):
    rao()


