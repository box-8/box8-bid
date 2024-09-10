import os
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from objects.Affaires import Affaire, Intervenant, Macrolot, Lot, LotIntervenant
from utils.Session import SQL_LITE_AFFAIRES_PATH

# Initialisation de la base de données
engine = create_engine(SQL_LITE_AFFAIRES_PATH)
Session = sessionmaker(bind=engine)
session = Session()

st.set_page_config(page_title="Gestion des Chantiers", page_icon="🏉", layout="wide") 

# Fonction pour afficher les intervenants
def afficher_intervenants(affaire):
    st.subheader(f"Intervenants pour {affaire.nom}")
    for intervenant in affaire.intervenants:
        st.write(f"{intervenant.prenom} {intervenant.nom} - {intervenant.role} ({intervenant.tel}, {intervenant.mail})")
        if st.button(f"Supprimer {intervenant.prenom} {intervenant.nom}", key=f"delete_intervenant_{intervenant.id}"):
            session.delete(intervenant)
            session.commit()
            st.experimental_rerun()

# Fonction pour ajouter un intervenant
def ajouter_intervenant(affaire):
    st.subheader(f"Ajouter un intervenant pour {affaire.nom}")
    with st.form(key='ajouter_intervenant'):
        prenom = st.text_input("Prénom")
        nom = st.text_input("Nom")
        role = st.selectbox("Rôle", ["maitre d'ouvrage", "bureau d'études", "coordinateur sécurité", "Entreprise"])
        tel = st.text_input("Téléphone")
        mail = st.text_input("Email")
        submit_button = st.form_submit_button("Ajouter Intervenant")

        if submit_button:
            intervenant = Intervenant(prenom=prenom, nom=nom, role=role, tel=tel, mail=mail, affaire_id=affaire.id)
            session.add(intervenant)
            session.commit()
            st.success("Intervenant ajouté avec succès.")
            st.experimental_rerun()

# Fonction pour afficher les macrolots et leurs lots
def afficher_macrolots(affaire):
    st.subheader(f"Macrolots pour {affaire.nom}")
    for macrolot in affaire.macrolots:
        st.write(f"Macrolot: {macrolot.nom}, Type: {macrolot.type}, Montant Total: {macrolot.montant}")
        for lot in macrolot.lots:
            st.write(f" - Lot: {lot.categorie}, Montant Commande: {lot.montant_commande}")
            if st.button(f"Supprimer Lot {lot.id}", key=f"delete_lot_{lot.id}"):
                session.delete(lot)
                session.commit()
                st.experimental_rerun()

# Fonction pour ajouter un lot à un macrolot
def ajouter_lot(macrolot):
    st.subheader(f"Ajouter un lot pour le macrolot {macrolot.nom}")
    with st.form(key=f'ajouter_lot_{macrolot.id}'):
        categorie = st.selectbox("Catégorie", ["terrassements", "VRD", "fondations", "génie civil", "tuyauterie", 
                                                "montage électromécanique", "électricité", "automatisme", 
                                                "espaces verts", "charpente", "couverture", "bardages", 
                                                "menuiseries", "peintures", "clôture", "télésurveillance"])
        devis = st.file_uploader("Téléverser le devis (PDF)", type="pdf")
        montant_commande = st.number_input("Montant Commande", min_value=0.0, format="%.2f")
        retenu = st.checkbox("Devis retenu")
        submit_button = st.form_submit_button("Ajouter Lot")

        if submit_button and devis is not None:
            devis_path = os.path.join("devis", devis.name)
            with open(devis_path, "wb") as f:
                f.write(devis.getbuffer())
            lot = Lot(categorie=categorie, devis=devis_path, montant_commande=montant_commande, retenu=retenu, macrolot_id=macrolot.id)
            session.add(lot)
            session.commit()
            st.success("Lot ajouté avec succès.")
            st.experimental_rerun()

# Gestion des affaires
def gerer_affaires():
    st.title("Gestion des Affaires")

    # Onglets pour gérer chaque section
    tab_affaires, tab_intervenants, tab_macrolots, tab_lots = st.tabs(["Affaires", "Intervenants", "Macrolots", "Lots"])

    with tab_affaires:
        st.subheader("Liste des Affaires")
        affaires = session.query(Affaire).all()
        for affaire in affaires:
            st.subheader(f"{affaire.nom} - {affaire.state}")
            st.write(f"Type: {affaire.type}, Montant: {affaire.montant}")
            if st.button(f"Supprimer {affaire.nom}", key=f"delete_affaire_{affaire.id}"):
                session.delete(affaire)
                session.commit()
                st.experimental_rerun()

        # Formulaire pour ajouter une affaire
        with st.form(key='affaire_form'):
            nom = st.text_input("Nom de l'affaire")
            description = st.text_area("Description")
            type_affaire = st.selectbox("Type d'affaire", ["Génie civil", "Équipements", "Autres"])
            montant = st.number_input("Montant total", min_value=0.0, format="%.2f")
            state = st.selectbox("État de l'affaire", ["Prospect", "En cours", "Terminée"])
            submit_button = st.form_submit_button("Ajouter Affaire")

            if submit_button:
                nouvelle_affaire = Affaire(nom=nom, description=description, type=type_affaire, montant=montant, state=state)
                session.add(nouvelle_affaire)
                session.commit()
                st.success("Affaire ajoutée avec succès.")
                st.experimental_rerun()

    with tab_intervenants:
        # Sélectionner une affaire pour voir ses intervenants
        affaire_id = st.selectbox("Sélectionner une affaire", [affaire.id for affaire in affaires], format_func=lambda id: session.query(Affaire).get(id).nom)
        affaire = session.query(Affaire).get(affaire_id)
        afficher_intervenants(affaire)
        ajouter_intervenant(affaire)

    with tab_macrolots:
        # Sélectionner une affaire pour voir ses macrolots
        affaire_id = st.selectbox("Sélectionner une affaire", [affaire.id for affaire in affaires], format_func=lambda id: session.query(Affaire).get(id).nom, key='macrolots_affaire')
        affaire = session.query(Affaire).get(affaire_id)
        afficher_macrolots(affaire)

    with tab_lots:
        # Sélectionner un macrolot pour ajouter un lot
        macrolot_id = st.selectbox("Sélectionner un macrolot", [macrolot.id for affaire in affaires for macrolot in affaire.macrolots], format_func=lambda id: session.query(Macrolot).get(id).nom)
        macrolot = session.query(Macrolot).get(macrolot_id)
        ajouter_lot(macrolot)


if __name__ == "__main__":
    gerer_affaires()
