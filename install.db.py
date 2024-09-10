from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from utils.Session import SQL_LITE_AFFAIRES_PATH
# Initialisation de la base de données avec le système moderne


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

    # Relations
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

    # Relations
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

    # Relations
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

    # Relations
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

    # Relations
    lot = relationship("Lot", back_populates="intervenants")
    intervenant = relationship("Intervenant", back_populates="lots")


# Connexion à la base de données SQLite (ou autre SGBD)
engine = create_engine(SQL_LITE_AFFAIRES_PATH, echo=True)  # 'echo=True' pour voir les logs SQL générés
# C:\_prod\box8-bid
# Création des tables dans la base de données
Base.metadata.create_all(engine)

# Configuration de la session
Session = sessionmaker(bind=engine)
session = Session()

# Exemple d'insertion d'une affaire
nouvelle_affaire = Affaire(nom="Construction de Pont", description="Construction d'un pont moderne", type="Infrastructures", montant=5000000.0, state="En cours")
session.add(nouvelle_affaire)
session.commit()

print("La base de données et les tables ont été créées avec succès.")
