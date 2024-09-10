# gestion affaires v2

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

# Fonction pour afficher les intervenants
def afficher_intervenants(intervenants):
    for intervenant in intervenants:
        st.write(f"{intervenant.prenom} {intervenant.nom} - {intervenant.role} ({intervenant.tel}, {intervenant.mail})")

# Fonction pour afficher les lots d'un macrolot
def afficher_lots(macrolot):
    for lot in macrolot.lots:
        st.write(f"Catégorie: {lot.categorie}, Montant Commande: {lot.montant_commande}")
        if st.button(f"Voir devis {lot.id}"):
            os.startfile(lot.devis)  # Ouvre le devis dans le visualiseur PDF par défaut

# Gestion des affaires
def gerer_affaires():
    st.title("Gestion des Affaires")

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

    # Afficher la liste des affaires existantes
    affaires = session.query(Affaire).all()
    for affaire in affaires:
        st.subheader(f"Affaire : {affaire.nom}")
        st.write(f"Description : {affaire.description}")
        st.write(f"Type : {affaire.type}, Montant : {affaire.montant}, État : {affaire.state}")

        # Afficher les intervenants associés
        st.write("Intervenants :")
        afficher_intervenants(affaire.intervenants)

        # Afficher les macrolots associés
        st.write("Macrolots :")
        for macrolot in affaire.macrolots:
            st.write(f"Macrolot : {macrolot.nom} - {macrolot.type}")
            afficher_lots(macrolot)

# Gestion des intervenants
def gerer_intervenants():
    st.title("Gestion des Intervenants")

    with st.form(key='intervenant_form'):
        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        role = st.selectbox("Rôle", ["Maitre d'ouvrage", "Bureau d'études", "Coordinateur sécurité", "Entreprise"])
        tel = st.text_input("Téléphone")
        mail = st.text_input("Email")
        affaire_id = st.number_input("ID de l'affaire", min_value=1)
        submit_button = st.form_submit_button("Ajouter Intervenant")

        if submit_button:
            nouvel_intervenant = Intervenant(nom=nom, prenom=prenom, role=role, tel=tel, mail=mail, affaire_id=affaire_id)
            session.add(nouvel_intervenant)
            session.commit()
            st.success("Intervenant ajouté avec succès.")

# Interface utilisateur principale
def app():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Aller à", ["Affaires", "Intervenants"])

    if page == "Affaires":
        gerer_affaires()
    elif page == "Intervenants":
        gerer_intervenants()

if __name__ == "__main__":
    app()
