import time
import json
import urllib.parse
from google import genai
from google.genai import types
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURATION ---
API_KEY = "AIzaSyCB6Ncbz-ixuTvOHBI0UUFziQ7hGXL5IXI" 
client = genai.Client(api_key=API_KEY)
PDF_FILE = "CPOU0650-CliDEV4945577.PDF"

def extraire_donnees_avec_gemini(chemin_pdf):
    print(f"--- Analyse du PDF : {chemin_pdf} ---")
    try:
        with open(chemin_pdf, "rb") as f:
            pdf_data = f.read()
        prompt = "Extraire les articles du devis en liste JSON. Clés : 'ref', 'nom'. Répondre uniquement en JSON brut."
        
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=[prompt, types.Part.from_bytes(data=pdf_data, mime_type="application/pdf")]
        )
        return json.loads(response.text.replace('```json', '').replace('```', '').strip())
    except Exception as e:
        print(f"Erreur IA : {e}")
        return []

def ouvrir_recherches_sidv(articles):
    if not articles: return

    options = Options()
    options.add_experimental_option("detach", True)
    
    # --- ASTUCES ANTI-DETECTION ---
    options.add_argument("--disable-blink-features=AutomationControlled") # Cache le mode robot
    options.add_experimental_option("excludeSwitches", ["enable-automation"]) # Enlève le message "contrôlé par..."
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    
    # Bypass navigator.webdriver
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    for i, art in enumerate(articles):
        ref = str(art.get('ref', '')).strip()
        if not ref or ref.upper() == "DIVERS": continue

        print(f"[{i+1}/{len(articles)}] Recherche : {ref}")
        
        try:
            # On va sur l'accueil
            driver.get("https://www.sidv.fr/")
            
            # Attente de la barre de recherche
            wait = WebDriverWait(driver, 10)
            # On cherche par 'name="q"' comme tu l'as trouvé
            barre = wait.until(EC.element_to_be_clickable((By.NAME, "q")))

            barre.clear()
            barre.send_keys(ref)
            time.sleep(0.5) # Petite pause pour simuler un humain
            barre.send_keys(Keys.ENTER)

        except Exception as e:
            print(f"Erreur sur {ref} : {e}")
            continue

        choix = input(">>> Suivant [Entrée] / Quitter [q] : ")
        if choix.lower() == 'q': break

    print("Fin.")

if __name__ == "__main__":
    liste = extraire_donnees_avec_gemini(PDF_FILE)
    if liste:
        if input("Lancer SIDV ? (o/n) : ").lower() == 'o':
            ouvrir_recherches_sidv(liste)