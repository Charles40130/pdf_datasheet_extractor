import os
import sys

# Ajouter le dossier "src" au chemin d'importation
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from extractor import extract_products_from_pdf
from scraper import search_products_on_sidv, search_products_on_cedeo

def main():
    # Vérification et création des dossiers si besoin
    if not os.path.exists(config.INPUT_DIR):
        os.makedirs(config.INPUT_DIR)

    if not os.path.exists(config.OUTPUT_DIR):
        os.makedirs(config.OUTPUT_DIR)

    if not os.path.exists(config.COOKIE_DIR):
        os.makedirs(config.COOKIE_DIR)

    # Récupérer la liste des PDF dans le dossier d'entrée
    pdf_files = [f for f in os.listdir(config.INPUT_DIR) if f.lower().endswith('.pdf')]

    if not pdf_files:
        print(f"Aucun fichier PDF trouvé dans {config.INPUT_DIR}")
        print("Veuillez y placer un devis au format .pdf")
        return

    pdf_file_path = os.path.join(config.INPUT_DIR, pdf_files[0])
    print(f"\nFichier détecté : {pdf_files[0]}\n")

    # 1. Extraction via IA
    print("Étape 1 : Extraction des articles")
    articles = extract_products_from_pdf(pdf_file_path)

    if not articles:
        print("L'extraction n'a retourné aucun article valide.")
        return

    print(f"\n{len(articles)} articles extraits avec succès.")

    # 2. Recherche et téléchargement (Scraping)
    print("\nÉtape 2 : Recherche des fiches techniques")
    print(f"Site cible : {config.PREFERRED_SITE.upper()}")
    reponse = input("Voulez-vous lancer la recherche sur le site cible ? (o/n) : ")
    if reponse.lower() == 'o':
        if config.PREFERRED_SITE == "cedeo":
            print("\nCedeo est connu pour imposer un défi anti-bot (DataDome / captcha).")
            print("Le script bascule automatiquement sur un mode manuel contrôlé si le site bloque l'accès.")
            search_products_on_cedeo(articles)
        else:
            search_products_on_sidv(articles)
    else:
        print("Opération annulée par l'utilisateur.")

if __name__ == "__main__":
    main()
