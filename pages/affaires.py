import json
import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text as ttxt
from sqlalchemy.orm import sessionmaker
from entities.Affaires import Affaire, Intervenant, Macrolot, Lot, LotIntervenant, get_entity_dataframe

from utils.Prompts import PromptSumarizeDevis
from utils.Session import SQL_LITE_AFFAIRES_PATH, app_upload_file, init_session, trouver_index, confirmbox, string_to_float
from utils.Agents import RagPdf

st.set_page_config(page_title="Gestion des Affaires", page_icon="🕴️", layout="wide") 
init_session()
# Initialisation de la base de données
engine = create_engine(SQL_LITE_AFFAIRES_PATH)
Session = sessionmaker(bind=engine)
DbSession = Session()






############################################################################################################
######## AFFAIRES
############################################################################################################

def selectionner_affaires(affaires):
    affaire_name = st.radio("Selectionner une affaire", 
            options=[affaire.nom for affaire in affaires],
            key="selected_affaire",
    )
    affaire = DbSession.query(Affaire).filter_by(nom=affaire_name).first()
    st.session_state.affaire = affaire
    
    delete_button = st.button("Effacer Affaire ")
    if delete_button:
        # confirmbox()
        if st.session_state.confirm :
            DbSession.delete(affaire)
            DbSession.commit()
            st.success("Affaire effacée avec succès.")
            st.rerun()
    return affaire

# affaire = DbSession.get(Affaire, id)
@st.dialog("Ajouter une Affaire")
def create_affaire():
    with st.form(key='affaire_form_new'):
        types = ["SUPERVISION DE TRAVAUX", "MAITRISE D'OEUVRE", "DIRECTION DE PROJET", "AUTRE"]
        states = ["Prospect", "En cours", "Terminée"]
        st.toast(f"Affaire traitée : {st.session_state.affaire.nom}")
        # Champs de saisie du formulaire
        nom = st.text_input("Nom de l'affaire")
        description = st.text_area("Description")
        montant = st.number_input("Montant total", min_value=0.0)
        type_affaire = st.selectbox("Type d'affaire", types)
        state = st.radio("État de l'affaire", states)
        
        update_button = st.form_submit_button("Mettre à jour")
        if update_button:
            affaire = Affaire(
            nom = nom,
            description = description,
            montant = montant,
            type = type_affaire,
            state = state)
            DbSession.add(affaire)
            DbSession.commit()
            st.success("Affaire créée avec succès.")
            st.rerun()

            
def update_affaire(affaire):
    with st.form(key='affaire_form'):
        types = ["SUPERVISION DE TRAVAUX", "MAITRISE D'OEUVRE", "DIRECTION DE PROJET", "AUTRE"]
        states = ["Prospect", "En cours", "Terminée"]
        # Trouver les index des valeurs actuelles
        index_state = trouver_index(affaire.state, states)
        index_type = trouver_index(affaire.type, types)
        # Afficher les valeurs actuelles pour le toast (pour le débogage)
        st.toast(f"Affaire traitée : {st.session_state.affaire.nom}")
        # Champs de saisie du formulaire
        nom = st.text_input("Nom de l'affaire", value=affaire.nom)
        description = st.text_area("Description", value=affaire.description)
        montant = st.number_input("Montant total", min_value=0.0, value=affaire.montant)
        type_affaire = st.selectbox("Type d'affaire", types, index=index_type)
        state = st.selectbox("État de l'affaire", states, index=index_state)
        
        update_button = st.form_submit_button("Mettre à jour")
        if update_button:
            affaire.nom = nom
            affaire.description = description
            affaire.montant = montant
            affaire.type = type_affaire
            affaire.state = state
            DbSession.commit()
            
            st.success("Affaire mise à jour avec succès.")




def subcat(cat):
    if cat=="génie civil":
        retour = ["terrassements", "VRD", "fondations", "gros euvre", "charpente"]
        
    elif cat =="équipement":
        retour = ["Machines de process","montage électromécanique", "tuyauterie", "levage"]
    
    elif cat =="électricité":
        retour = ["électricité", "automatisme","télésurveillance"]
    else:
        retour = ["espaces verts", "couverture", "bardages", 
            "menuiseries", "peintures", "clôture", "divers"]
    
    return retour




############################################################################################################
#### MACROLOTS
############################################################################################################

# Fonction pour afficher les macrolots et leurs lots
# Fonction pour afficher les macrolots et leurs lots
def afficher_macrolots(affaire):
    st.subheader(f"Macrolots pour {affaire.nom}")
    
    # Si l'affaire n'a pas de macrolots
    if not affaire.macrolots:
        st.write("Aucun macrolot disponible pour cette affaire.")
        
    # Sélectionner un macrolot parmi ceux de l'affaire
    macrolot_ids = [str(macrolot.id) for macrolot in affaire.macrolots]
    macrolot_names = [macrolot.nom for macrolot in affaire.macrolots]
    
    radio_macrolots_options = []
    montant_affaire = 0
    for mcLot in affaire.macrolots : 
        radio_macrolots_options.append(mcLot.nom)  
        montant_affaire += mcLot.montant      
    
    macrolot_selectionne_name = st.radio(
        "Sélectionner un macrolot", 
        options = radio_macrolots_options,
    )
    st.write(f"Montant de l'affaire {str(montant_affaire)}")
    
    # Récupérer le macrolot sélectionné
    for mcLot in affaire.macrolots : 
        if mcLot.nom == macrolot_selectionne_name:
            macrolot_selectionne_id = mcLot.id 
    try:

        macrolot_selectionne = DbSession.get(Macrolot, macrolot_selectionne_id)
    except Exception as e:
        st.session_state.key_macrolot_nom = ""
        macrolot_selectionne = None
    
    
    if macrolot_selectionne:
        # Bouton pour supprimer le macrolot sélectionné
        if st.button(f"Supprimer le Macrolot ", key=f"delete_macrolot_{macrolot_selectionne.id}"):
            # Supprimer les lots associés et le macrolot
            for lot in macrolot_selectionne.lots:
                DbSession.delete(lot)
            DbSession.delete(macrolot_selectionne)
            DbSession.commit()
            st.success(f"Macrolot {macrolot_selectionne.nom} supprimé avec succès.")
            st.rerun()

        # Mettre à jour la liste des lots pour l'onglet numéro 4
        st.session_state.selected_macrolot_lots = macrolot_selectionne.lots
    else:
        pass
    submit_button = st.button("Ajouter Macrolot")
    if submit_button:
        create_macrolot(affaire)
    return macrolot_selectionne


@st.dialog("Ajouter un lot")
def create_macrolot(affaire):
    
    types = ["génie civil", "équipement", "électricité", "autres"]
    
    with st.form(key=f'ajouter_macrolot'):
        nom = st.text_input("   ", "")
        type = st.selectbox("Téléverser le CCTP", types)
        montant = st.number_input("Montant", min_value=0.0, format="%.2f")
        
        create_button = st.form_submit_button("Créer Macrolot")
        if create_button:        
            macrolot_selectionne = Macrolot(
                nom=nom, 
                type=type, 
                montant=montant, 
                affaire_id=affaire.id)
            DbSession.add(macrolot_selectionne)
            DbSession.commit()
            st.toast("Macrolot ajouté avec succès.")
            st.rerun()
            
# Fonction pour mettre à jour u macrolot
def update_macrolot (macrolot):
    with st.form(key='update_macrolot'):
        
        types = ["génie civil", "équipement", "électricité", "autres"]
        if macrolot is None:
            type = types[0]
            nom = st.session_state.get("key_macrolot_nom", "")
            type = st.session_state.get("key_macrolot_type", "")
            
            macrolot = Macrolot(id=0, nom=nom, type=type, montant=0.0, affaire_id= st.session_state.affaire.id)
            index_type = trouver_index(macrolot.type, types)
        else:
            index_type = trouver_index(macrolot.type, types)
        
        nom = st.text_input("Nom du macrolot", value=macrolot.nom, key="key_macrolot_nom")
        type_macrolot = st.selectbox("Type de macrolot", types, index=index_type, key="key_macrolot_type")  
        montant = st.number_input("Montant k€", value=macrolot.montant, min_value=0.0, format="%.2f", key="key_macrolot_montant")
        

        update_button = st.form_submit_button("Mettre à jour")
        if update_button:
            # Mettre à jour l'macrolot existante
            macrolot.nom = nom
            macrolot.montant = montant
            macrolot.type = type_macrolot
            DbSession.commit()
            st.toast("Macrolot mis à jour avec succès")
            st.rerun()









############################################################################################################
###### LOTS
############################################################################################################

def lister_lots(macrolot):
    # Filtrer les lots pour qu'ils appartiennent au macrolot donné
    lots = DbSession.query(Lot).filter_by(macrolot_id=macrolot.id).all()
    
    # Ajouter une option pour créer un nouveau lot
    options = [lot.categorie for lot in lots] 
    
    # Afficher les options dans un menu radio
    lotname = st.radio(f"{macrolot.nom} > lots", 
            options=options,
            key="selected_lot",
    )
    
    lot = DbSession.query(Lot).filter_by(categorie=lotname, macrolot_id=macrolot.id).first()        
    st.session_state.lot = lot
    
    if lotname:
        # Bouton pour supprimer le macrolot sélectionné
        if st.button(f"Supprimer le Lot ", key=f"delete_lot_{lot.id}"):
            # Supprimer les lots associés et le macrolot
            DbSession.delete(lot)
            DbSession.commit()
            st.success(f"Macrolot {lot.categorie} supprimé avec succès.")
            st.rerun()
    
    submit_button = st.button("Ajouter Lot")
    
    if submit_button:
        ajouter_lot(macrolot)
    
    return lot


def update_lot(lot : Lot, current_macrolot):
    cat = subcat(current_macrolot.type)
    
    index_lot = 0
    if lot is not None:
        index_lot = trouver_index(lot.categorie, cat)
    
    if lot is None : 
        st.write("Ajouter des lots sur ce macrolots")
        return False
    else:
        id =lot.id
    with st.form(key=f'update_lot_{id}'):
        categorie = st.selectbox("Catégorie", cat, index=index_lot)
        description=lot.description
        montant_commande=lot.montant_commande
        if lot.devis is None:
            devis = st.file_uploader("Téléverser le CCTP", type="pdf")
        else :
            devis1 = st.file_uploader("Téléverser le CCTP", type="pdf")
            devis = st.text_input("Devis", value=lot.devis, disabled=True)
            col1, col2 = st.columns(2)
            with col1:
                voir_button = st.form_submit_button("Voir le pdf")
            with col2:
                analyser_button = st.form_submit_button("Analyser")
            if voir_button:
                os.startfile(lot.devis)
            if analyser_button:
                ragAgent = RagPdf(lot.devis)
                jsonResponse = ragAgent.ask(PromptSumarizeDevis)
                try :
                    data = json.loads(jsonResponse)
                    jsdescription = data.get('description')
                    jsmontant = string_to_float(data.get("montant"))
                    st.write("IA found relevant information")
                    montant_commande = st.number_input(f"Montant Commande ({lot.montant_commande})", value=jsmontant, min_value=0.0, format="%.2f")
                    description = st.text_area("Description ", value=jsdescription)
                    lot.description = description
                    lot.montant_commande = montant_commande
                    DbSession.commit()
                    
                except Exception as e:
                    # montant_commande = st.number_input("Montant Commande", value=lot.montant_commande, min_value=0.0, format="%.2f")
                    # description = st.text_area("Description ", value=lot.description)
                    st.write(jsonResponse)
                    st.write(e)
        
        exp = st.expander("détails")
        with exp:
            st.write("description")
            st.write(description)
            st.header(montant_commande)
            
                    
        retenu = st.checkbox("Devis retenu", value=lot.retenu)
        update_button = st.form_submit_button("Mettre à jour")
        if update_button:
            # Mettre à jour l'macrolot existante
            lot.categorie = categorie
            if devis1 is not None:
                devis_path = app_upload_file(devis1)
                lot.devis = devis_path
            lot.description = description
            lot.retenu = retenu
            lot.montant_commande = montant_commande
            DbSession.commit()
            st.toast("Macrolot mis à jour avec succès")
            st.rerun()
            
        
       
    


# Fonction pour ajouter un lot à un macrolot
@st.dialog("Ajouter un lot")
def ajouter_lot(macrolot):
    cat = subcat(macrolot.type)
    with st.form(key=f'ajouter_lot_{macrolot.id}'):
        st.header(f"{macrolot.nom}")
        categorie = st.selectbox("Catégorie", cat)
        devis = st.file_uploader("Téléverser le Devis", type="pdf")
        # montant_commande = st.number_input("Montant Commande", min_value=0.0, format="%.2f")
        # retenu = st.checkbox("Devis retenu")
        submit_button = st.form_submit_button("Ajouter Lot")
        if submit_button and devis is not None:

            devis_path = app_upload_file(devis)

            lot = Lot(
                categorie=categorie, 
                devis=devis_path,
                # montant_commande=montant_commande,
                # retenu=retenu,
                macrolot_id=macrolot.id)
            DbSession.add(lot)
            DbSession.commit()
            st.success("Lot ajouté avec succès.")
            st.rerun()
        










############################################################################################################
###### intervenants
############################################################################################################

# Fonction pour afficher les intervenants
def afficher_intervenants(affaire):
    st.subheader(f"Intervenants pour {affaire.nom}")
    if affaire is None:
        return None

    for intervenant in affaire.intervenants:
        st.markdown(f"""{intervenant.prenom} {intervenant.nom} {intervenant.role}
         ({intervenant.tel} - 
         {intervenant.mail})""")
        if st.button(f"Supprimer {intervenant.prenom} {intervenant.nom}", key=f"delete_intervenant_{intervenant.id}"):
            DbSession.delete(intervenant)
            DbSession.commit()
            st.rerun()

# Fonction pour ajouter un intervenant
def ajouter_intervenant(affaire):
    st.subheader(f"{affaire.nom} > intervenants")
    with st.form(key='ajouter_intervenant'):
        prenom = st.text_input("Prénom")
        nom = st.text_input("Nom")
        role = st.selectbox("Rôle", ["maitre d'ouvrage", "bureau d'études", "coordinateur sécurité", "Entreprise"])
        tel = st.text_input("Téléphone")
        mail = st.text_input("Email")
        submit_button = st.form_submit_button("Ajouter Intervenant")

        if submit_button:
            intervenant = Intervenant(prenom=prenom, nom=nom, role=role, tel=tel, mail=mail, affaire_id=affaire.id)
            DbSession.add(intervenant)
            DbSession.commit()
            st.success("Intervenant ajouté avec succès.")
            st.rerun()









############################################################################################################
###### MAIN
############################################################################################################
def getSQL(key): 
    queries = [
        {"tout": """
            SELECT 
                affaires.nom AS affaire_nom,
                macrolots.nom AS macrolot_nom,
                lots.categorie AS lot_categorie,
                lots.montant_commande AS lot_montant
            FROM affaires
            LEFT JOIN macrolots 
            ON affaires.id = macrolots.affaire_id
            LEFT JOIN lots 
            ON macrolots.id = lots.macrolot_id
            ORDER BY 
                affaires.id ASC,
                macrolots.nom ASC
                
            ;
        """},
        {"totaux": """
            SELECT 
                affaires.id AS affaire_id, 
                affaires.nom AS affaire_nom, 
                SUM(macrolots.montant) AS budget,
                COUNT(macrolots.id) AS nombre_macrolots, 
                SUM(lots.montant_commande) AS commande,
                COUNT(lots.id) AS nombre_commandes
            FROM 
                affaires 
            LEFT JOIN 
                macrolots ON affaires.id = macrolots.affaire_id
            LEFT JOIN 
                lots ON lots.macrolot_id = macrolots.id
            GROUP BY 
                affaires.id, affaires.nom
            ORDER BY 
                affaires.id ASC,
                macrolots.nom ASC
                ;
            
        """}
    ]
    
    # Parcours de la liste queries
    for query in queries:
        if key in query:
            return query[key]  # Retourne le SQL correspondant à la clé
    
    return None  # Retourne None si la clé n'est pas trouvée


# Gestion des affaires
def gerer_affaires():
    # Onglets pour gérer chaque section
    tab_affaires, tab_intervenants, tab_macrolots, tab_lots, tab_liste = st.tabs(["Affaires", "Intervenants", "Macrolots", "Lots", "Liste"])
    affaires = DbSession.query(Affaire).all()

    with tab_affaires:

        col1, col2, col3 = st.columns(3)
        with col1:
            affaire = selectionner_affaires(affaires)
            create_button = st.button("Créer une Affaire")
            if create_button:
                create_affaire()
        with col2:
            # Formulaire pour maj une affaire
            update_affaire(affaire)

        with col3:
            #affaires = get_entity_dataframe(DbSession, table_class=Affaire)
            
            for affaire in affaires:
                text = f"{affaire.nom} - {affaire.state} - Type: {affaire.type}, Montant: {affaire.montant}"
                if affaire.state =="Terminée":
                    st.error(text)
                elif affaire.state =="En cours":
                    st.success(text)
                elif affaire.state =="Prospect":
                    st.warning(text)                
        

    with tab_intervenants:
        # Sélectionner une affaire pour voir ses intervenants
        #affaire_id = st.selectbox("Sélectionner une affaire", [affaire.id for affaire in affaires], format_func=lambda id: DbSession.query(Affaire).get(id).nom)
        col1, col2 = st.columns(2)
        with col1 : 
            ajouter_intervenant(st.session_state.affaire)
        with col2 : 
            afficher_intervenants(st.session_state.affaire)

    with tab_macrolots:
        # Sélectionner une affaire pour voir ses macrolots
        # affaire = DbSession.query(Affaire).get(st.session_state.affaire.id)
        col1, col2 = st.columns(2)
        with col1 : 
            current_macrolot = afficher_macrolots(st.session_state.affaire)
        with col2 : 
            update_macrolot(current_macrolot)
        

    with tab_lots:
        if st.session_state.affaire.nom is None :
            st.write("Choisir une affaire")    
        elif current_macrolot is None:
            st.subheader(f"{st.session_state.affaire.nom} > ...")
            st.write("Créer ou choisir un macrolot")
            
        else:
            
            st.subheader(f"{st.session_state.affaire.nom} > {current_macrolot.nom}")
            col1,col2= st.columns(2)
            with col1:
                if current_macrolot :
                    current_lot = lister_lots(current_macrolot)
                else:
                    st.write("Choisir un macrolot")
            with col2:
                # Sélectionner un macrolot pour ajouter un lot
                if current_macrolot :
                    lot = update_lot(current_lot, current_macrolot)
                else:
                    st.write(f"Ajouter les lots pour définir {current_macrolot.nom} ({current_macrolot.type})")
                    
    with tab_liste:
                

        

        radioquery = st.radio(f"Choisir le rapport", 
                ["tout","totaux"],
                key="selected_query",
        )
        

        
        
        if radioquery:
            with engine.connect() as connection:
                result = connection.execute(ttxt(getSQL(radioquery)))
                df = pd.DataFrame(result.fetchall(), columns=result.keys())# Récupérer les résultats sous forme de DataFrame
            st.write('Affichage des Affaires, Macrolots et Lots avec SQLAlchemy et SQLite')# Affichage dans Streamlit
            st.dataframe(df)  # Affiche un tableau interactif


         

   
   






 


# Fonction pour ajouter les macrolots aux affaires
# def ajouter_macrolot(affaire):
#     st.subheader(f"Ajouter un macrolot ")
#     with st.form(key='ajouter_macrolot'):
#         nom = st.text_input("Nom du macrolot")
#         type_macrolot = st.selectbox("Type de macrolot", ["génie civil", "équipement", "électricité", "autres"])  
#         montant = st.number_input("Montant", min_value=0.0, format="%.2f")
        
#         submit_button = st.form_submit_button("Ajouter Macrolot")

#         if submit_button:
#             macrolot = Macrolot(nom=nom, type=type_macrolot, montant=montant, affaire_id=affaire.id)
#             DbSession.add(macrolot)
#             DbSession.commit()
#             st.success("Macrolot ajouté avec succès.")
#             st.rerun()


if __name__ == "__main__":
    gerer_affaires()
