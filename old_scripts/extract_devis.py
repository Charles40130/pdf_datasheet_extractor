from google import genai
from google.genai import types
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import json
import urllib.parse

# --- CONFIGURATION ---
API_KEY = "AIzaSyCB6Ncbz-ixuTvOHBI0UUFziQ7hGXL5IXI"
client = genai.Client(api_key=API_KEY)

def extraire_donnees_avec_gemini(chemin_pdf):
    print("Analyse du PDF par Gemini (nouvelle API)...")
    
    # Lecture du fichier en binaire
    with open(chemin_pdf, "rb") as f:
        pdf_data = f.read()

    prompt = """
    Analyse ce devis et extrait tous les articles sous forme de liste JSON. 
    Chaque objet doit avoir les clés : 'ref', 'marque', 'nom'.
    Ignore l'éco-participation, les taxes et les commentaires généraux.
    Réponds uniquement avec le code JSON brut, sans balises ```json.
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash", # Utilisation de la version la plus récente
        contents=[
            prompt,
            types.Part.from_bytes(data=pdf_data, mime_type="application/pdf")
        ]
    )
    
    # Nettoyage et chargement du JSON
    net_text = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(net_text)

def ouvrir_recherches_selenium(articles):
    print(f"\nPréparation de {len(articles)} recherches.")
    print("Appuyez sur 'Entrée' dans le terminal pour ouvrir l'onglet suivant, ou tapez 'q' pour quitter.\n")
    
    options = Options()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options)

    for i, art in enumerate(articles):
        # Préparation de la recherche
        query = f"{art['ref']} {art['nom']}"
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={encoded_query}"
        
        # Affichage de l'article en cours dans le terminal
        print(f"[{i+1}/{len(articles)}] Ouverture de : {art['ref']} - {art['nom']}")
        
        # Commande pour ouvrir l'onglet
        if i == 0:
            driver.get(url)
        else:
            driver.execute_script(f"window.open('{url}', '_blank');")
            # On bascule le focus sur le nouvel onglet pour que vous le voyiez immédiatement
            driver.switch_to.window(driver.window_handles[-1])

        # Pause et demande à l'utilisateur
        choix = input(">>> Appuyez sur Entrée pour le suivant (ou 'q' pour arrêter) : ")
        if choix.lower() == 'q':
            print("Arrêt des recherches.")
            break

    print("Fin du processus.")

if __name__ == "__main__":
    PDF_FILE = "CPOU0650-CliDEV4945577.PDF"
    
    try:
        # Étape 1 : Extraction
        liste_articles = extraire_donnees_avec_gemini(PDF_FILE)
        
        # --- DEBUG : Vérification des données ---
        print("\n--- ARTICLES EXTRAITS ---")
        if not liste_articles:
            print("Aucun article trouvé ou erreur de format.")
        else:
            # Affichage propre dans la console
            for i, art in enumerate(liste_articles):
                ref = art.get('ref', 'N/A')
                nom = art.get('nom', 'N/A')
                marque = art.get('marque', 'N/A')
                print(f"[{i+1}] REF: {ref} | MARQUE: {marque} | NOM: {nom}")
        
        print(f"Nombre total : {len(liste_articles)}")
        print("--------------------------\n")

        # Étape 2 : Confirmation avant Selenium
        reponse = input("Voulez-vous ouvrir les onglets ? (o/n) : ")
        if reponse.lower() == 'o':
            ouvrir_recherches_selenium(liste_articles)
        else:
            print("Opération annulée.")
            
    except Exception as e:
        print(f"Erreur lors de l'exécution : {e}")