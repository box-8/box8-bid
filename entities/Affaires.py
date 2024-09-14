import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import Text, create_engine, Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
import os

# Remplacer l'importation dépréciée par celle-ci
Base = declarative_base()

# Classe Affaire
class Affaire(Base):
    __tablename__ = 'affaires'
    id = Column(Integer, primary_key=True)
    nom = Column(String, nullable=False)
    description = Column(String)
    type = Column(String, nullable=False)
    montant = Column(Float, nullable=False)
    state = Column(String, nullable=False)

    intervenants = relationship("Intervenant", back_populates="affaire")
    macrolots = relationship("Macrolot", back_populates="affaire")

# Classe Intervenant pour Affaire
class Intervenant(Base):
    __tablename__ = 'intervenants'
    id = Column(Integer, primary_key=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    role = Column(String, nullable=False)
    tel = Column(String)
    mail = Column(String)
    affaire_id = Column(Integer, ForeignKey('affaires.id'))

    affaire = relationship("Affaire", back_populates="intervenants")
    lots = relationship("LotIntervenant", back_populates="intervenant")

# Classe Macrolot
class Macrolot(Base):
    __tablename__ = 'macrolots'
    id = Column(Integer, primary_key=True)
    nom = Column(String, nullable=False)
    type = Column(String, nullable=False)
    montant = Column(Float, default=0.0)
    affaire_id = Column(Integer, ForeignKey('affaires.id'))

    affaire = relationship("Affaire", back_populates="macrolots")
    lots = relationship("Lot", back_populates="macrolot")

# Classe Lot
class Lot(Base):
    __tablename__ = 'lots'
    id = Column(Integer, primary_key=True)
    categorie = Column(String, nullable=False)
    devis = Column(String)  # Stocker le chemin du fichier PDF
    retenu = Column(Boolean, default=False)
    montant_commande = Column(Float, default=0.0)
    macrolot_id = Column(Integer, ForeignKey('macrolots.id'))
    description = Column(Text)  # Type texte pour des descriptions longues
    
    macrolot = relationship("Macrolot", back_populates="lots")
    intervenants = relationship("LotIntervenant", back_populates="lot")

# Classe Intervenants sur les Lots
class LotIntervenant(Base):
    __tablename__ = 'lot_intervenants'
    id = Column(Integer, primary_key=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    role = Column(String, nullable=False)
    tel = Column(String)
    mail = Column(String)
    lot_id = Column(Integer, ForeignKey('lots.id'))
    intervenant_id = Column(Integer, ForeignKey('intervenants.id'))

    lot = relationship("Lot", back_populates="intervenants")
    intervenant = relationship("Intervenant", back_populates="lots")

# Créer la base de données
def init_db():
    engine = create_engine('sqlite:///affaires.db')
    Base.metadata.create_all(engine)










def get_entity_dataframe(db_session: Session, table_class, field: str = None, value = None):
    """
    Fonction générique pour afficher une table SQLite sous forme de DataFrame.

    Args:
        db_session (Session): Session SQLAlchemy pour la base de données.
        table_class: Classe représentant la table SQLAlchemy.
        field (str, optional): Nom du champ pour filtrer. Par défaut None.
        value (any, optional): Valeur du champ pour filtrer. Par défaut None.

    Returns:
        pd.DataFrame: DataFrame contenant les résultats de la table.
    """
    # Si un champ et une valeur sont fournis, on applique le filtre
    if field and value:
        query = db_session.query(table_class).filter(getattr(table_class, field) == value)
    else:
        # Sinon, on récupère toutes les données de la table
        query = db_session.query(table_class)
    
    # Exécuter la requête
    results = query.all()

    # Convertir les résultats en DataFrame
    data = [row.__dict__ for row in results]
    
    # Supprimer la colonne _sa_instance_state ajoutée par SQLAlchemy
    for d in data:
        d.pop('_sa_instance_state', None)

    # Retourner les données sous forme de DataFrame
    return pd.DataFrame(data)





















if __name__ == "__main__":
    if not os.path.exists('affaires.db'):
        init_db()
        print("Base de données initialisée avec succès.")
