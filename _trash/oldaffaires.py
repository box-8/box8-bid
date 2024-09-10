import streamlit as st
import sqlite3
from sqlite3 import Error
import pandas as pd
from  utils.Session import * 
# Fonction pour créer une connexion à la base de données SQLite
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('affaires.db')
        return conn
    except Error as e:
        st.error(f"Erreur de connexion à la base de données: {e}")
        return None

# Fonction pour créer la table dans la base de données si elle n'existe pas encore
def create_table(conn):
    try:
        sql_create_affaires_table = """
        CREATE TABLE IF NOT EXISTS affaires (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL,
            montant REAL NOT NULL,
            state TEXT NOT NULL
        );
        """
        cursor = conn.cursor()
        cursor.execute(sql_create_affaires_table)
    except Error as e:
        st.error(f"Erreur lors de la création de la table: {e}")

# Fonction pour insérer une affaire dans la base de données
def insert_affaire(conn, affaire):
    try:
        sql_insert_affaire = """
        INSERT INTO affaires ( nom, description, type, montant, state)
        VALUES (?, ?, ?, ?, ?);
        """
        cursor = conn.cursor()
        cursor.execute(sql_insert_affaire, affaire)
        conn.commit()
    except Error as e:
        st.error(f"Erreur lors de l'insertion de l'affaire: {e}")

# Interface utilisateur avec Streamlit
def app():
    st.title("Enregistrement des Affaires")
    
    conn = create_connection()
    if conn is not None:
        create_table(conn)
    
        col1, col2 = st.columns(2)
        with col1:
            with st.form(key='affaire_form'):
                nom = st.text_input("Nom de l'affaire")
                description = st.text_area("Description succincte")
                type_affaire = st.selectbox("Type d'affaire", ["Stratégie d'entreprise", "Audit de projet", "Suivi construction", "Formation"])
                montant = st.number_input("Montant du consultant", min_value=0.0, format="%.2f")
                state = st.selectbox("Type d'affaire", ["Prospect", "En cours", "Soldée", "Archivée"])
                
                submit_button = st.form_submit_button("Enregistrer")
                
                if submit_button:
                    affaire = (nom, description, type_affaire, montant, state )
                    insert_affaire(conn, affaire)
                    st.success("Affaire enregistrée avec succès!")
        
        with col2:
            # Afficher les affaires enregistrées
            st.subheader("Affaires enregistrées")
            df = pd.read_sql_query("SELECT nom, type, montant, state FROM affaires", conn)
            st.dataframe(df)




if __name__ == "__main__":
    conn = create_connection()
    create_table(conn)

app()
