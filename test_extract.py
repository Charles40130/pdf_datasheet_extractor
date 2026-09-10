import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
import config
from scraper import search_products_on_sidv

def main():
    print("Test du scraper avec des références manuelles...")
    # On va tester sur 2 articles connus et un qui n'existe probablement pas
    arts_to_test = [
        {"ref": "02111100", "nom": "Test Produit Chaudiere"},
        {"ref": "013009", "nom": "Test Tube Cuivre"},
        {"ref": "REF-INCONNUE-9999", "nom": "Produit inexistant"}
    ]
    search_products_on_sidv(arts_to_test)

if __name__ == "__main__":
    main()
