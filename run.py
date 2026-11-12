import os
from app import create_app
from app.models import db, User
from seed_data import seed_database

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Initialiser les données de démo si la base est vide
        if User.query.count() == 0:
            print("Base de données vide. Insertion automatique des données de démo réalistes pour Nador...")
            seed_database()
            print("Données initialisées avec succès !")

    port = int(os.environ.get('PORT', 5000))
    print(f"\n=======================================================")
    print(f"  CLINIQUE MÉDICO-CHIRURGICALE DU RIF - NADOR (MAROC)  ")
    print(f"  SIH / EMR Production-Ready - Port: {port}            ")
    print(f"  URL: http://localhost:{port}                         ")
    print(f"=======================================================\n")
    app.run(host='0.0.0.0', port=port, debug=False)
