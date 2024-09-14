import streamlit as st
import fitz  
# fitz est le module principal de PyMuPDF

# Fonction pour afficher une page PDF
def display_pdf_page(doc, page_number):
    page = doc.load_page(page_number)  # Charge la page spécifiée
    pix = page.get_pixmap()  # Obtient une image de la page
    st.image(pix.tobytes(), output_format='PNG')  # Affiche l'image dans Streamlit

# Interface Streamlit
st.title("Visionneuse PDF avec PyMuPDF")

uploaded_file = st.file_uploader("Téléverser un fichier PDF", type="pdf")

if uploaded_file is not None:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")  # Ouvre le PDF depuis le flux de données
    total_pages = doc.page_count

    selected_page = st.selectbox("Sélectionner une page", range(total_pages))
    display_pdf_page(doc, selected_page)