from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)
ref = "02111100" # Un exemple de reférence qui pourrait exister
print(f"Testing search for {ref}")

try:
    driver.get(f"https://www.sidv.fr/recherche?q={ref}") # Deviner l'URL de recherche
    time.sleep(3)
    print("URL finale:", driver.current_url)
    
    # Cherchons des liens PDF ou le mot fiche technique
    links = driver.find_elements(By.TAG_NAME, "a")
    pdf_links = []
    for link in links:
        href = link.get_attribute("href")
        text = link.text.lower()
        if href and (".pdf" in href.lower() or "fiche" in text or "technique" in text):
            pdf_links.append((text, href))
            
    print("Found potential datasheet links:")
    for text, href in pdf_links:
        print(f"- {text}: {href}")
        
    # Essayons avec une autre forme de recherche
    driver.get("https://www.sidv.fr/")
    time.sleep(2)
    barre = driver.find_element(By.NAME, "q")
    barre.send_keys("chaudiere") # Un mot clé générique pour voir les résultats
    barre.submit()
    time.sleep(3)
    print("\nURL finale après recherche 'chaudiere':", driver.current_url)
    
    # Prendre le premier résultat
    products = driver.find_elements(By.CSS_SELECTOR, "a.product-link, a.product-item, .product-title a") # Divinations CSS
    print(f"Found {len(products)} potential products on search page.")
    if products:
        products[0].click()
        time.sleep(3)
        print("URL produit:", driver.current_url)
        # Chercher PDF
        links = driver.find_elements(By.TAG_NAME, "a")
        for link in links:
            href = link.get_attribute("href")
            text = link.text.lower()
            if href and (".pdf" in href.lower() or "fiche" in text or "technique" in text):
                print(f"Product page PDF link: {text}: {href}")
        
except Exception as e:
    print("Error:", e)
finally:
    driver.quit()
