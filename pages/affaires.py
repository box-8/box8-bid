import os
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from objects.Affaires import Affaire, Intervenant, Macrolot, Lot, LotIntervenant, get_entity_dataframe
from utils.Session import SQL_LITE_AFFAIRES_PATH, init_session, trouver_index

st.set_page_config(page_title="Gestion des Affaires", page_icon="🕴️", layout="wide") 
init_session()

idx = trouver_index(st.session_state.llm_model, st.session_state.llm_allowed)
selected_llm = st.sidebar.radio("Choose LLM",
        st.session_state.llm_allowed,
        captions=st.session_state.llm_allowed_def,
        key="selected_llm_options",
        index=idx
    )
if selected_llm :
    st.session_state.llm_model = selected_llm




# Initialisation de la base de données
engine = create_engine(SQL_LITE_AFFAIRES_PATH)
Session = sessionmaker(bind=engine)
DbSession = Session()


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
            DbSession.add(intervenant)
            DbSession.commit()
            st.success("Intervenant ajouté avec succès.")
            st.rerun()



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
    radio_macrolots_options.append("Nouveau Macrolot")
    
    
    macrolot_selectionne_name = st.radio(
        "Sélectionner un macrolot", 
        options = radio_macrolots_options,
        #format_func=lambda id: DbSession.query(Macrolot).get(id).nom + " - " + str(DbSession.query(Macrolot).get(id).montant)
    )
    st.write(f"Montant de l'affaire {str(montant_affaire)}")
    
    # Récupérer le macrolot sélectionné
    for mcLot in affaire.macrolots : 
        if mcLot.nom == macrolot_selectionne_name:
            macrolot_selectionne_id = mcLot.id 
    try:
        macrolot_selectionne = DbSession.query(Macrolot).get(macrolot_selectionne_id)
    except Exception as e:
        macrolot_selectionne = None
    
    
    if macrolot_selectionne:
        # Bouton pour supprimer le macrolot sélectionné
        if st.button(f"Supprimer le Macrolot {macrolot_selectionne.nom}", key=f"delete_macrolot_{macrolot_selectionne.id}"):
            # Supprimer les lots associés et le macrolot
            for lot in macrolot_selectionne.lots:
                DbSession.delete(lot)
            DbSession.delete(macrolot_selectionne)
            DbSession.commit()
            st.success(f"Macrolot {macrolot_selectionne.nom} supprimé avec succès.")
            #st.rerun()

        # Mettre à jour la liste des lots pour l'onglet numéro 4
        st.session_state.selected_macrolot_lots = macrolot_selectionne.lots
    else:
        submit_button = st.button("Ajouter Macrolot")
        if submit_button:
            macrolot_selectionne = Macrolot(nom="nom", type="autres", montant=0, affaire_id=affaire.id)
            DbSession.add(macrolot_selectionne)
            DbSession.commit()
            st.toast("Macrolot ajouté avec succès.")
            st.rerun()
    return macrolot_selectionne



# Fonction pour mettre à jour u macrolot
def update_macrolot (macrolot):
    # st.subheader(f"{st.session_state.current_affaire.nom} / {macrolot.nom} ")
    with st.form(key='update_macrolot'):
        
        types = ["génie civil", "équipement", "électricité", "autres"]
        if macrolot is None:
            type = types[0]
            macrolot = Macrolot(id=0, nom="nom", type=type, montant=0.0, affaire_id= st.session_state.current_affaire.id)
            index_type = trouver_index(macrolot.type, types)
        else:
            index_type = trouver_index(macrolot.type, types)
        
        nom = st.text_input("Nom du macrolot", value=macrolot.nom)
        type_macrolot = st.selectbox("Type de macrolot", types, index=index_type)  
        montant = st.number_input("Montant k€", value=macrolot.montant, min_value=0.0, format="%.2f")
        

        update_button = st.form_submit_button("Mettre à jour")
        if update_button:
            # Mettre à jour l'macrolot existante
            macrolot.nom = nom
            macrolot.montant = montant
            macrolot.type = type_macrolot
            DbSession.commit()
            st.success("Macrolot mis à jour avec succès.")
            #st.rerun()




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
            DbSession.add(lot)
            DbSession.commit()
            st.success("Lot ajouté avec succès.")
            st.experimental_rerun()







         

def selectionner_affaires(affaires):
    affaire_id = st.selectbox("Sélectionner une affaire", [affaire.id for affaire in affaires], format_func=lambda id: DbSession.query(Affaire).get(id).nom)
    affaire = DbSession.query(Affaire).get(affaire_id)
    st.session_state.current_affaire = affaire
    return affaire
   
   






 
# Gestion des affaires
def gerer_affaires():
    st.title(f"Gestion des Affaires ({st.session_state.llm_model})")

    # Onglets pour gérer chaque section
    tab_affaires, tab_intervenants, tab_macrolots, tab_lots = st.tabs(["Affaires", "Intervenants", "Macrolots", "Lots"])
    affaires = DbSession.query(Affaire).all()

    with tab_affaires:

        col1, col2, col3 = st.columns(3)
        with col1:
            affaire = selectionner_affaires(affaires)
            delete_button = st.button("Effacer Affaire " + affaire.nom)
            if delete_button:
                DbSession.delete(affaire)
                DbSession.commit()
                st.success("Affaire effacée avec succès.")
                st.rerun()
            
            create_button = st.button("Créer une Affaire")
            if create_button:
                
                affaire = Affaire(nom="Nouvelle affaire", description="Description", type="Autre", montant="10000", state="Prospect")
                DbSession.add(affaire)
                DbSession.commit()

                st.success("Affaire Créer avec succès.")
                st.rerun()
            
        with col2:
            # Formulaire pour maj une affaire
            with st.form(key='affaire_form'):
                types = ["SUPERVISION DE TRAVAUX", "MAITRISE D'OEUVRE", "DIRECTION DE PROJET", "AUTRE"]
                states = ["Prospect", "En cours", "Terminée"]

                # Trouver les index des valeurs actuelles
                index_state = trouver_index(affaire.state, states)
                index_type = trouver_index(affaire.type, types)
                
                # Afficher les valeurs actuelles pour le toast (pour le débogage)
                st.toast(f"Affaire traitée : {st.session_state.current_affaire.nom}")
                
                # Champs de saisie du formulaire
                nom = st.text_input("Nom de l'affaire", value=affaire.nom)
                description = st.text_area("Description", value=affaire.description)
                montant = st.number_input("Montant total", min_value=0.0, value=affaire.montant)
                type_affaire = st.selectbox("Type d'affaire", types, index=index_type)
                state = st.selectbox("État de l'affaire", states, index=index_state)
                
                update_button = st.form_submit_button("Mettre à jour")
                if update_button:
                    # Mettre à jour l'affaire existante
                    affaire.nom = nom
                    affaire.description = description
                    affaire.montant = montant
                    affaire.type = type_affaire
                    affaire.state = state
                    
                    # Commit les changements dans la base de données
                    DbSession.commit()
                    
                    # Afficher un message de succès
                    st.success("Affaire mise à jour avec succès.")
                    
                    # Redémarrer l'application pour refléter les changements
                    # st.rerun()

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
            ajouter_intervenant(st.session_state.current_affaire)
        with col2 : 
            afficher_intervenants(st.session_state.current_affaire)

    with tab_macrolots:
        # Sélectionner une affaire pour voir ses macrolots
        # affaire = DbSession.query(Affaire).get(st.session_state.current_affaire.id)
        col1, col2 = st.columns(2)
        with col1 : 
            current_macrolot = afficher_macrolots(st.session_state.current_affaire)
        with col2 : 
            update_macrolot(current_macrolot)
        

    with tab_lots:
        # Sélectionner un macrolot pour ajouter un lot
        macrolot_id = st.selectbox("Sélectionner un macrolot", [macrolot.id for affaire in affaires for macrolot in affaire.macrolots], format_func=lambda id: DbSession.query(Macrolot).get(id).nom)
        macrolot = DbSession.query(Macrolot).get(macrolot_id)
        if not macrolot is None:
            ajouter_lot(macrolot)




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
