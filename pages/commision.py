from box8.Session import *
from box8.Agents import Commercial, Consultant, RagAgent
from box8.Functions import toast, extraire_tableau_json, DocumentWriter
from scripts.mes import *


uploaded_file_mes = st.file_uploader("Upload technical document", type="pdf")
if st.button("MISE EN SERVICE"):
    
    # Streamlit file uploader for PDF
    
    if uploaded_file_mes :
        
        do(uploaded_file_mes)
    
    
