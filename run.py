import os
from app import create_app
from app.models import db, User
from seed_data import seed_database

app = create_app()

# Initialisation automatique au chargement (essentiel pour Vercel Serverless & Production)
with app.app_context():
    try:
        db.create_all()
        if User.query.count() == 0:
            print("Initialisation automatique des données de démonstration pour Nador...")
            seed_database()
    except Exception as e:
        print("Note d'initialisation de la base :", e)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n=======================================================")
    print(f"  CLINIQUE MÉDICO-CHIRURGICALE DU RIF - NADOR (MAROC)  ")
    print(f"  SIH / EMR Production-Ready - Port: {port}            ")
    print(f"  URL: http://localhost:{port}                         ")
    print(f"=======================================================\n")
    app.run(host='0.0.0.0', port=port, debug=False)

