from flask import Flask, render_template, request, redirect, url_for
from flask import flash
from models import db, Client , Vehicule,RendezVous,DossierReparation,Photo 
from decorators import role_required
from s3_utils import upload_file_to_s3
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)
from datetime import datetime
from models import Employe
from config import Config
app = Flask(__name__)
app.config.from_object(Config)
from datetime import datetime
db.init_app(app)

with app.app_context():
    db.create_all()

with app.app_context():

    if not Employe.query.filter_by(email="admin@garage.com").first():

        admin = Employe(
            nom="Administrateur",
            email="admin@garage.com",
            role="admin"
        )

        admin.set_password("admin123")

        db.session.add(admin)

    if not Employe.query.filter_by(email="conseiller@garage.com").first():

        conseiller = Employe(
            nom="Conseiller",
            email="conseiller@garage.com",
            role="conseiller"
        )

        conseiller.set_password("123456")

        db.session.add(conseiller)

    if not Employe.query.filter_by(email="mecanicien@garage.com").first():

        mecanicien = Employe(
            nom="Mécanicien",
            email="mecanicien@garage.com",
            role="mecanicien"
        )

        mecanicien.set_password("123456")

        db.session.add(mecanicien)

    if not Employe.query.filter_by(email="direction@garage.com").first():

        direction = Employe(
            nom="Direction",
            email="direction@garage.com",
            role="direction"
        )

        direction.set_password("123456")

        db.session.add(direction)

    db.session.commit()




@app.route("/prendre_rendezvous", methods=["GET", "POST"])
def prendre_rendezvous():

    if request.method == "POST":

        # Recherche du client par email
        client = Client.query.filter_by(
            email=request.form["email"]
        ).first()

        # Création du client s'il n'existe pas
        if not client:

            client = Client(
                nom=request.form["nom"],
                prenom=request.form["prenom"],
                telephone=request.form["telephone"],
                email=request.form["email"],
                adresse=""
            )

            db.session.add(client)
            db.session.commit()

        # Création du véhicule
        vehicule = Vehicule(
            marque=request.form["marque"],
            modele=request.form["modele"],
            annee=int(request.form["annee"]),
            immatriculation=request.form["immatriculation"],
            vin=request.form["vin"],
            client_id=client.id
        )

        db.session.add(vehicule)
        db.session.commit()

        # Conversion de la date
        date_rdv = datetime.strptime(
            request.form["date_rdv"],
            "%Y-%m-%dT%H:%M"
        )

        # Création du rendez-vous
        rdv = RendezVous(
            date_rdv=date_rdv,
            description=request.form["description"],
            statut="En attente",
            vehicule_id=vehicule.id
        )

        db.session.add(rdv)
        db.session.commit()

        flash(
            "Votre demande de rendez-vous a été enregistrée avec succès. Un conseiller vous contactera rapidement.",
            "success"
        )

        return redirect(url_for("prendre_rendezvous"))

    return render_template("prendre_rendezvous.html")


@app.route("/admin")
@login_required
@role_required("admin")
def admin():
    return "Administration"


@app.route("/")
def index():
    return render_template("index.html")
@app.route("/clients")
@login_required
@role_required("admin","conseiller","direction")
def clients():
    liste_clients = Client.query.all()
    return render_template("clients.html", clients=liste_clients)


@app.errorhandler(403)
def acces_interdit(error):

    return render_template(
        "403.html"
    ), 403


@app.route("/ajouter_client", methods=["GET", "POST"])
@login_required
def ajouter_client():

    if request.method == "POST":

        nouveau_client = Client(
            nom=request.form["nom"],
            prenom=request.form["prenom"],
            telephone=request.form["telephone"],
            email=request.form["email"],
            adresse=request.form["adresse"]
        )

        db.session.add(nouveau_client)
        db.session.commit()

        return redirect(url_for("clients"))

    return render_template("ajouter_client.html")


@app.route("/photos/<int:dossier_id>")
@login_required
@role_required("admin", "conseiller", "mecanicien", "direction")
def voir_photos(dossier_id):

    dossier = DossierReparation.query.get_or_404(dossier_id)

    return render_template(
        "photos.html",
        dossier=dossier
    )


@app.route("/modifier_client/<int:id>", methods=["GET", "POST"])
@login_required
def modifier_client(id):

    client = Client.query.get_or_404(id)

    if request.method == "POST":

        client.nom = request.form["nom"]
        client.prenom = request.form["prenom"]
        client.telephone = request.form["telephone"]
        client.email = request.form["email"]
        client.adresse = request.form["adresse"]

        db.session.commit()

        return redirect(url_for("clients"))

    return render_template("modifier_client.html", client=client)


@app.route("/supprimer_client/<int:id>")
@login_required
@role_required("admin")
def supprimer_client(id):

    client = Client.query.get_or_404(id)

    for vehicule in client.vehicules:

        # Supprimer les dossiers et leurs photos
        for dossier in vehicule.dossiers:

            for photo in dossier.photos:
                db.session.delete(photo)

            db.session.delete(dossier)

        # Supprimer les rendez-vous
        for rdv in vehicule.rendezvous:
            db.session.delete(rdv)

        # Supprimer le véhicule
        db.session.delete(vehicule)

    # Supprimer le client
    db.session.delete(client)

    db.session.commit()

    return redirect(url_for("clients"))


@app.route("/vehicules")
@login_required
@role_required("admin","conseiller","direction")
def vehicules():
    liste_vehicules = Vehicule.query.all()
    return render_template(
        "vehicules.html",
        vehicules=liste_vehicules
    )


@app.route("/ajouter_vehicule", methods=["GET", "POST"])
@login_required
def ajouter_vehicule():

    clients = Client.query.all()

    if request.method == "POST":

        vehicule = Vehicule(
            marque=request.form["marque"],
            modele=request.form["modele"],
            annee=int(request.form["annee"]),
            immatriculation=request.form["immatriculation"],
            vin=request.form["vin"],
            client_id=int(request.form["client_id"])
        )

        db.session.add(vehicule)
        db.session.commit()

        return redirect(url_for("vehicules"))

    return render_template(
        "ajouter_vehicule.html",
        clients=clients
    )



@app.route("/rendezvous")
@login_required
@role_required("admin","conseiller","direction")
def rendezvous():

    liste_rdv = RendezVous.query.all()

    return render_template(
        "rendezvous.html",
        rendezvous=liste_rdv
    )


@app.route("/ajouter_rendezvous", methods=["GET", "POST"])
@login_required
def ajouter_rendezvous():
    vehicules = Vehicule.query.all()
    if request.method == "POST":

        date_rdv = datetime.strptime(
            request.form["date_rdv"],
            "%Y-%m-%dT%H:%M"
        )

        rdv = RendezVous(
            date_rdv=date_rdv,
            description=request.form["description"],
            statut=request.form["statut"],
            vehicule_id=int(request.form["vehicule_id"])
        )

        db.session.add(rdv)
        db.session.commit()

        return redirect(url_for("rendezvous"))

    return render_template(
        "ajouter_rendezvous.html",
        vehicules=vehicules
    )





@app.route("/dossiers")
@login_required
@role_required(
    "admin",
    "conseiller",
    "mecanicien",
    "direction"
)
def dossiers():

    liste_dossiers = DossierReparation.query.all()

    return render_template(
        "dossiers.html",
        dossiers=liste_dossiers
    )

@app.route("/ajouter_dossier", methods=["GET", "POST"])
@login_required
def ajouter_dossier():

    vehicules = Vehicule.query.all()

    if request.method == "POST":

        dossier = DossierReparation(

            etat=request.form["etat"],

            cout_estime=float(
                request.form["cout_estime"]
            ),

            notes=request.form["notes"],

            validation_client=(
                request.form.get("validation_client")
                == "on"
            ),

            vehicule_id=int(
                request.form["vehicule_id"]
            )
        )

        db.session.add(dossier)
        db.session.commit()

        return redirect(url_for("dossiers"))

    return render_template(
        "ajouter_dossier.html",
        vehicules=vehicules
    )

# =========================================
# RAPPORTS
# =========================================

@app.route("/rapports")
@login_required
@role_required("admin", "direction")
def rapports():

    nb_clients = Client.query.count()
    nb_vehicules = Vehicule.query.count()
    nb_rdv = RendezVous.query.count()
    nb_dossiers = DossierReparation.query.count()

    return render_template(
        "rapports.html",
        nb_clients=nb_clients,
        nb_vehicules=nb_vehicules,
        nb_rdv=nb_rdv,
        nb_dossiers=nb_dossiers
    )


# =========================================
# EMPLOYÉS
# =========================================

@app.route("/employes")
@login_required
@role_required("admin")
def employes():

    liste_employes = Employe.query.all()

    return render_template(
        "employes.html",
        employes=liste_employes
    )



@app.route("/modifier_employe/<int:id>", methods=["GET", "POST"])
@login_required
@role_required("admin")
def modifier_employe(id):

    employe = Employe.query.get_or_404(id)

    if request.method == "POST":

        employe.nom = request.form["nom"]
        employe.email = request.form["email"]
        employe.role = request.form["role"]

        # Modifier le mot de passe seulement s'il est renseigné
        if request.form["password"] != "":
            employe.set_password(request.form["password"])

        db.session.commit()

        flash("Employé modifié avec succès.", "success")

        return redirect(url_for("employes"))

    return render_template(
        "modifier_employe.html",
        employe=employe
    )


@app.route("/supprimer_employe/<int:id>")
@login_required
@role_required("admin")
def supprimer_employe(id):

    employe = Employe.query.get_or_404(id)

    # Empêcher la suppression de son propre compte
    if employe.id == current_user.id:

        flash(
            "Vous ne pouvez pas supprimer votre propre compte.",
            "danger"
        )

        return redirect(url_for("employes"))

    db.session.delete(employe)
    db.session.commit()

    flash(
        "Employé supprimé avec succès.",
        "success"
    )

    return redirect(url_for("employes"))


@app.route("/upload_photo/<int:dossier_id>",
methods=["GET","POST"])
@login_required
@role_required("admin","mecanicien")
def upload_photo(dossier_id):

    if request.method == "POST":

        fichier = request.files["photo"]

        url = upload_file_to_s3(fichier)

        photo = Photo(
            photo_url=url,
            dossier_id=dossier_id
        )

        db.session.add(photo)
        db.session.commit()

        return redirect(url_for("dossiers"))

    return render_template(
        "upload_photo.html",
        dossier_id=dossier_id
    )


login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"



@login_manager.user_loader
def load_user(user_id):

    return Employe.query.get(int(user_id))



@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        employe = Employe.query.filter_by(
            email=email
        ).first()

        if employe and employe.check_password(password):

            login_user(employe)

            return redirect(url_for("index"))

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("login"))

with app.app_context():

    db.create_all()

    if not Employe.query.filter_by(
        email="admin@garage.com"
    ).first():

        admin = Employe(
            nom="Administrateur",
            email="admin@garage.com",
            role="admin"
        )

        admin.set_password("admin123")

        db.session.add(admin)

        db.session.commit()

@app.route("/suivi", methods=["GET", "POST"])
def suivi():

    rendezvous = None

    if request.method == "POST":

        email = request.form["email"]
        telephone = request.form["telephone"]

        client = Client.query.filter_by(
            email=email,
            telephone=telephone
        ).first()

        if client:

            vehicule = Vehicule.query.filter_by(
                client_id=client.id
            ).first()

            if vehicule:

                rendezvous = RendezVous.query.filter_by(
                    vehicule_id=vehicule.id
                ).order_by(
                    RendezVous.date_rdv.desc()
                ).first()

    return render_template(
        "suivi.html",
        rendezvous=rendezvous
    )


@app.route("/ajouter_employe", methods=["GET", "POST"])
@login_required
@role_required("admin")
def ajouter_employe():

    if request.method == "POST":

        employe = Employe(
            nom=request.form["nom"],
            email=request.form["email"],
            role=request.form["role"]
        )

        employe.set_password(request.form["password"])

        db.session.add(employe)
        db.session.commit()

        flash("Employé ajouté avec succès.", "success")

        return redirect(url_for("employes"))

    return render_template("ajouter_employe.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
