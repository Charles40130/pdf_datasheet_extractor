import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

options = Options()
# Ne pas utiliser headless pour éviter le blocage
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

print("Starting visible browser...")
driver = webdriver.Chrome(options=options)
ref = "02111100"

try:
    print(f"Loading https://www.sidv.fr/recherche?q={ref}")
    driver.get(f"https://www.sidv.fr/recherche?q={ref}")
    print("Waiting 10 seconds for content to load...")
    time.sleep(10)
    print("CURRENT URL:", driver.current_url)
    
    links = driver.find_elements(By.TAG_NAME, "a")
    print(f"Total links found: {len(links)}")
    
    for link in links:
        href = link.get_attribute("href")
        cls = link.get_attribute("class")
        
        # Check if the text matches the ref, or if it has typical product link structure
        if href and "sidv.fr/produit" in href.lower():
            text = link.text.strip().replace("\n", " ")
            print(f"Product Link: class='{cls}', text='{text}', href='{href}'")
            
except Exception as e:
    print("Erreur:", e)
finally:
    driver.quit()
