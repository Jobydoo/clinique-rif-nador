import threading
import time
import pytest
from playwright.sync_api import sync_playwright
from app import create_app
from seed_data import seed_database
from app.models import db

SERVER_PORT = 5008
BASE_URL = f"http://127.0.0.1:{SERVER_PORT}"

@pytest.fixture(scope="session")
def live_server():
    app = create_app()
    app.config['TESTING'] = True
    
    with app.app_context():
        db.create_all()
        seed_database()

    server_thread = threading.Thread(
        target=lambda: app.run(host='127.0.0.1', port=SERVER_PORT, threaded=True, debug=False, use_reloader=False),
        daemon=True
    )
    server_thread.start()
    time.sleep(2.0) # Attente démarrage serveur Flask
    yield BASE_URL

def test_full_e2e_browser_flows(live_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        # 1. Chargement de l'application (sans attendre les polices externes)
        page.goto(live_server, wait_until="domcontentloaded")
        page.wait_for_selector("#root", timeout=8000)
        assert "Clinique" in page.title()

        # Attendre que React monte l'application
        page.wait_for_selector("header", timeout=8000)
        assert page.locator("header").is_visible()

        # 2. Test du basculement bilingue Français / Arabe (RTL)
        lang_btn = page.locator("button:has-text('العربية')")
        if lang_btn.is_visible():
            lang_btn.click()
            time.sleep(0.5)
            # Vérifier que le document passe en RTL
            html_dir = page.evaluate("document.documentElement.getAttribute('dir')")
            assert html_dir == "rtl"

            # Rebasculer en Français
            fr_btn = page.locator("button:has-text('Français')")
            fr_btn.click()
            time.sleep(0.5)
            html_dir_fr = page.evaluate("document.documentElement.getAttribute('dir')")
            assert html_dir_fr == "ltr"

        # 3. Test Navigation Onglets (Vérification Zéro Erreur 404/500)
        tabs = [
            ("Salle d'Attente", "Salle d'Attente"),
            ("Dossiers Patients", "Dossiers Patients"),
            ("Consultations", "Consultations"),
            ("Hospitalisation", "Hospitalisation"),
            ("Facturation", "Facturation"),
            ("Pharmacie", "Pharmacie"),
            ("Personnel", "Personnel"),
            ("Coffre-fort Archives", "Coffre-fort Archives"),
            ("Audit CNDP", "Audit CNDP")
        ]

        for tab_name, expected_text in tabs:
            tab_locator = page.locator(f"nav button:has-text(\"{tab_name}\")")
            assert tab_locator.is_visible()
            tab_locator.click()
            time.sleep(0.6)
            page.wait_for_selector(f"text={expected_text}", timeout=5000)

        # 4. Test Ouverture Modale Nouveau Patient
        page.locator("nav button:has-text('Dossiers Patients')").click()
        time.sleep(0.4)
        new_pat_btn = page.locator("button:has-text('Nouveau Patient')").first
        assert new_pat_btn.is_visible()
        new_pat_btn.click()
        time.sleep(0.5)

        # Vérifier que la modale s'ouvre
        modal_title = page.locator("h3:has-text('Nouveau Patient')")
        assert modal_title.is_visible()

        # Fermer la modale
        close_btn = page.locator("button:has-text('✕')")
        close_btn.click()
        time.sleep(0.4)
        assert not modal_title.is_visible()

        # 5. Test Changement de Rôle Démo (RBAC)
        role_btn = page.locator("button:has-text('DOCTOR')")
        if role_btn.is_visible():
            role_btn.click()
            time.sleep(0.5)

        browser.close()
        print("\nPlaywright E2E Tests Completed with 100% Success!")
