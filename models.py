from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# ==========================
# CLIENT
# ==========================
class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100))
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    adresse = db.Column(db.String(200))

    vehicules = db.relationship("Vehicule", backref="client", lazy=True)


# ==========================
# VEHICULE
# ==========================
class Vehicule(db.Model):
    __tablename__ = "vehicules"

    id = db.Column(db.Integer, primary_key=True)
    marque = db.Column(db.String(50))
    modele = db.Column(db.String(50))
    annee = db.Column(db.Integer)
    immatriculation = db.Column(db.String(20))
    vin = db.Column(db.String(50))

    client_id = db.Column(
        db.Integer,
        db.ForeignKey('clients.id'),
        nullable=False
    )

    rendezvous = db.relationship("RendezVous", backref="vehicule", lazy=True)
    dossiers = db.relationship("DossierReparation", backref="vehicule", lazy=True)


# ==========================
# EMPLOYE
# ==========================
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Employe(UserMixin, db.Model):

    __tablename__ = "employes"

    id = db.Column(db.Integer, primary_key=True)

    nom = db.Column(db.String(100))

    email = db.Column(db.String(120), unique=True)

    mot_de_passe = db.Column(db.String(255))

    role = db.Column(db.String(50))


    def set_password(self, password):
        self.mot_de_passe = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(
            self.mot_de_passe,
            password
        )

# ==========================
# RENDEZ-VOUS
# ==========================
class RendezVous(db.Model):
    __tablename__ = "rendezvous"

    id = db.Column(db.Integer, primary_key=True)
    date_rdv = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
    statut = db.Column(db.String(50), default="En attente")

    vehicule_id = db.Column(
        db.Integer,
        db.ForeignKey('vehicules.id'),
        nullable=False
    )


# ==========================
# DOSSIER REPARATION
# ==========================
class DossierReparation(db.Model):
    __tablename__ = "dossiers"

    id = db.Column(db.Integer, primary_key=True)
    etat = db.Column(db.String(50))
    cout_estime = db.Column(db.Float)
    validation_client = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)

    vehicule_id = db.Column(
        db.Integer,
        db.ForeignKey('vehicules.id'),
        nullable=False
    )

    photos = db.relationship("Photo", backref="dossier", lazy=True,cascade="all, delete-orphan")


# ==========================
# PHOTO
# ==========================
class Photo(db.Model):

    __tablename__ = "photos"

    id = db.Column(db.Integer, primary_key=True)

    photo_url = db.Column(db.String(255))

    dossier_id = db.Column(
        db.Integer,
        db.ForeignKey('dossiers.id'),
        nullable=False
    )

# ==========================
# FACTURE
# ==========================
class Facture(db.Model):
    __tablename__ = "factures"

    id = db.Column(db.Integer, primary_key=True)
    montant = db.Column(db.Float)
    date_facture = db.Column(db.DateTime, default=datetime.utcnow)
    statut_paiement = db.Column(db.String(50))
