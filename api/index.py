import sys
import os

# Ajouter le répertoire racine au PATH pour Vercel Serverless
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from run import app

# Vercel WSGI entry point
application = app
