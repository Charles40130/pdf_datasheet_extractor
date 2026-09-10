import json
import os
import time
import requests
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

import config


def is_cedeo_blocked_page(url: str, html: str) -> bool:
    """Retourne True si Cedeo affiche une page de protection anti-bot ou de captcha."""
    if not html:
        return False
    lower = html.lower()
    blocked_indicators = [
        "captcha",
        "data dome",
        "datadome",
        "verify you are human",
        "please verify",
        "vérifiez que vous êtes humain",
        "security check",
        "human verification",
        "robot",
        "captcha-delivery.com",
        "geo.captcha-delivery.com",
    ]
    if any(token in lower for token in blocked_indicators):
        return True
    if "cedeo.fr" in (url or "").lower() and "connexion" not in lower and "se connecter" not in lower and "mon compte" not in lower and "email" not in lower and "password" not in lower and "captcha-delivery.com" in lower:
        return True
    return False


def download_pdf(url, dest_path):
    """Télécharge le fichier PDF à l'URL donnée."""
    try:
        response = requests.get(url, stream=True, timeout=15)
        response.raise_for_status()
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"    Erreur lors du téléchargement : {e}")
        return False


def build_chrome_options(use_persistent_profile: bool = True) -> Options:
    options = Options()
    options.add_experimental_option("detach", True)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    if use_persistent_profile:
        os.makedirs(config.CHROME_PROFILE_DIR, exist_ok=True)
        options.add_argument(f"--user-data-dir={config.CHROME_PROFILE_DIR}")

    return options


def save_cookies_to_file(driver, file_path: str = None):
    file_path = file_path or config.CEDEO_COOKIES_FILE
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    try:
        cookies = driver.get_cookies()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=2)
        return True
    except Exception as e:
        print(f"    Impossible de sauvegarder les cookies : {e}")
        return False


def restore_cookies_from_file(driver, file_path: str = None):
    file_path = file_path or config.CEDEO_COOKIES_FILE
    if not os.path.exists(file_path):
        return False

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            cookies = json.load(f)
        driver.get("https://www.cedeo.fr/")
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except Exception:
                pass
        return True
    except Exception as e:
        print(f"    Impossible de restaurer les cookies : {e}")
        return False


def open_cedeo_manual_session():
    """Ouvre une session Chrome persistante pour qu'un humain résolve le défi Cedeo manuellement."""
    print("\nCedeo impose un défi anti-bot. Aucun contournement automatique n'est tenté.")
    print("Ouverture d'une fenêtre Chrome avec profil persistant pour une connexion manuelle.")
    print("1) Connectez-vous manuellement sur Cedeo et résolvez le challenge.")
    print("2) Une fois la session active, appuyez sur Entrée dans le terminal pour poursuivre.")
    options = build_chrome_options(use_persistent_profile=True)
    driver = webdriver.Chrome(options=options)
    try:
        driver.get("https://www.cedeo.fr/")
        time.sleep(2)
        input("Appuyez sur Entrée après connexion manuelle à Cedeo...")
        save_cookies_to_file(driver)
        return True
    except KeyboardInterrupt:
        print("    Session manuelle interrompue.")
        return False
    finally:
        driver.quit()


def login_to_cedeo(driver, email: str = None, password: str = None, force: bool = False):
    email = email or config.CEDEO_EMAIL
    password = password or config.CEDEO_PASSWORD

    if not email or not password:
        raise ValueError("Les identifiants Cedeo ne sont pas configurés. Ajoutez CEDEO_EMAIL et CEDEO_PASSWORD dans votre .env.")

    try:
        driver.get("https://www.cedeo.fr/")
        time.sleep(2)
        page_text = driver.page_source or ""
        if is_cedeo_blocked_page(driver.current_url, page_text):
            print("    Cedeo bloque actuellement les accès automatiques avec un défi anti-bot (DataDome/Captcha).")
            print("    Le script ne peut pas continuer tant que la protection anti-bot n'est pas contournée ou désactivée.")
            return False

        if "connexion" in page_text.lower() or "se connecter" in page_text.lower() or "mon compte" in page_text.lower():
            # la session peut déjà être active
            if "deconnexion" in page_text.lower() or "se déconnecter" in page_text.lower():
                print("    Session Cedeo déjà active.")
                save_cookies_to_file(driver)
                return True

        login_urls = [
            "https://www.cedeo.fr/connexion",
            "https://www.cedeo.fr/login",
            "https://www.cedeo.fr/compte",
            "https://www.cedeo.fr/account",
        ]

        for url in login_urls:
            try:
                driver.get(url)
                time.sleep(2)
                if "email" in (driver.page_source or "").lower() or "password" in (driver.page_source or "").lower():
                    break
            except Exception:
                continue

        selectors = [
            (By.NAME, "email"),
            (By.NAME, "login"),
            (By.NAME, "username"),
            (By.ID, "email"),
            (By.ID, "login"),
            (By.CSS_SELECTOR, "input[type='email']"),
            (By.CSS_SELECTOR, "input[name*='mail']"),
        ]

        email_field = None
        for by, value in selectors:
            try:
                element = WebDriverWait(driver, 8).until(EC.presence_of_element_located((by, value)))
                if element and element.is_displayed():
                    email_field = element
                    break
            except Exception:
                continue

        if email_field is None:
            print("    Formulaire de login Cedeo introuvable. Vérifie la structure du site ou les cookies déjà enregistrés.")
            return False

        email_field.clear()
        email_field.send_keys(email)

        password_field = None
        for by, value in [
            (By.NAME, "password"),
            (By.ID, "password"),
            (By.CSS_SELECTOR, "input[type='password']"),
            (By.XPATH, "//input[@type='password']"),
        ]:
            try:
                elem = driver.find_element(by, value)
                if elem and elem.is_displayed():
                    password_field = elem
                    break
            except Exception:
                continue

        if password_field is None:
            print("    Champ mot de passe Cedeo introuvable.")
            return False

        password_field.clear()
        password_field.send_keys(password)

        submit_btns = driver.find_elements(By.XPATH, "//button[@type='submit' or contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'connexion') or contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'se connecter')]")
        if submit_btns:
            for btn in submit_btns:
                try:
                    if btn.is_displayed():
                        btn.click()
                        break
                except Exception:
                    continue

        time.sleep(4)
        save_cookies_to_file(driver)
        print("    Connexion Cedeo tentée avec succès (session enregistrée).")
        return True
    except Exception as e:
        print(f"    Erreur de connexion Cedeo : {e}")
        return False


def search_products_on_cedeo(articles: list[dict]):
    if not articles:
        print("Aucun article à chercher.")
        return

    options = build_chrome_options(use_persistent_profile=True)
    driver = webdriver.Chrome(options=options)
    try:
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        restore_cookies_from_file(driver)
        if not config.CEDEO_EMAIL or not config.CEDEO_PASSWORD:
            print("Identifiants Cedeo absents. Ajoutez CEDEO_EMAIL et CEDEO_PASSWORD dans .env.")
            return

        connected = False
        try:
            driver.get("https://www.cedeo.fr/")
            time.sleep(2)
            page_text = driver.page_source or ""
            if is_cedeo_blocked_page(driver.current_url, page_text):
                print("    Cedeo affiche un défi anti-bot. Je bascule sur une session manuelle contrôlée.")
                if open_cedeo_manual_session():
                    restore_cookies_from_file(driver)
                    driver.get("https://www.cedeo.fr/")
                    time.sleep(2)
                    page_text = driver.page_source or ""
                    if "deconnexion" in page_text.lower() or "se déconnecter" in page_text.lower() or "mon compte" in page_text.lower():
                        connected = True
                return
            if "deconnexion" in page_text.lower() or "se déconnecter" in page_text.lower() or "mon compte" in page_text.lower():
                connected = True
        except Exception:
            connected = False

        if not connected:
            connected = login_to_cedeo(driver)

        if not connected:
            print("    Impossible d’authentifier le navigateur Cedeo. Vérifiez votre compte, les identifiants et les protections anti-bot.")
            return

        for i, art in enumerate(articles):
            ref = str(art.get('ref', '')).strip()
            nom = str(art.get('nom', '')).strip()

            if not ref or ref.upper() == "DIVERS":
                continue

            print(f"\n[{i+1}/{len(articles)}] Recherche Cedeo : {ref} - {nom[:30]}")

            try:
                driver.get("https://www.cedeo.fr/")
                time.sleep(1.5)

                search_input = None
                for selector in [
                    (By.NAME, "q"),
                    (By.NAME, "search"),
                    (By.NAME, "query"),
                    (By.CSS_SELECTOR, "input[type='search']"),
                    (By.CSS_SELECTOR, "input[placeholder*='Rechercher']"),
                    (By.CSS_SELECTOR, "input[placeholder*='Chercher']"),
                ]:
                    try:
                        element = WebDriverWait(driver, 8).until(EC.presence_of_element_located(selector))
                        if element and element.is_displayed():
                            search_input = element
                            break
                    except Exception:
                        continue

                if search_input is None:
                    search_url = f"https://www.cedeo.fr/?q={ref}"
                    driver.get(search_url)
                    time.sleep(2)
                else:
                    search_input.clear()
                    search_input.send_keys(ref)
                    search_input.submit()
                    time.sleep(2)

                product_links = []
                for selector in [
                    "a[href*='/article']",
                    "a[href*='/produit']",
                    ".product a",
                    "a.product-link",
                    "a[href*='produits']",
                    "a[href*='article']",
                ]:
                    product_links = driver.find_elements(By.CSS_SELECTOR, selector)
                    if product_links:
                        break

                pdf_url = None
                if product_links:
                    href = product_links[0].get_attribute("href")
                    if href:
                        driver.get(urljoin(driver.current_url, href))
                        time.sleep(2)

                if not pdf_url:
                    links = driver.find_elements(By.TAG_NAME, "a")
                    for link in links:
                        href = link.get_attribute("href")
                        if not href:
                            continue
                        text = (link.text or "").lower()
                        href_lower = href.lower()
                        if ".pdf" in href_lower or "fiche technique" in text or "notice" in text or "télécharger" in text or "pdf" in text:
                            pdf_url = href
                            break

                if not pdf_url:
                    print("    => Fiche technique introuvable sur la page Cedeo.")
                    continue

                pdf_url = urljoin(driver.current_url, pdf_url)
                print(f"    => Fiche localisée : {pdf_url}")

                safe_ref = "".join(c for c in ref if c.isalnum() or c in ('-', '_'))
                dest_filename = f"{safe_ref}_Fiche.pdf"
                dest_path = os.path.join(config.OUTPUT_DIR, dest_filename)

                if download_pdf(pdf_url, dest_path):
                    print(f"    => [SUCCÈS] Téléchargé dans {dest_filename}")

            except Exception as e:
                print(f"    Erreur inattendue sur {ref} : {str(e)}")
                continue

        save_cookies_to_file(driver)
        print("\nFin du processus de recherche et téléchargement sur Cedeo.")
    finally:
        driver.quit()


def search_products_on_sidv(articles: list[dict]):
    if not articles:
        print("Aucun article à chercher.")
        return

    options = build_chrome_options(use_persistent_profile=True)
    print(f"Lancement du navigateur pour {len(articles)} recherches...")
    driver = webdriver.Chrome(options=options)
    try:
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        try:
            driver.get("https://www.sidv.fr/")
            time.sleep(2)
            cookie_btns = driver.find_elements(By.XPATH, "//button[contains(translate(text(), 'ACPT', 'acpt'), 'accepter') or contains(@class, 'cookie')]")
            if cookie_btns:
                cookie_btns[0].click()
                time.sleep(1)
        except Exception:
            pass

        for i, art in enumerate(articles):
            ref = str(art.get('ref', '')).strip()
            nom = str(art.get('nom', '')).strip()

            if not ref or ref.upper() == "DIVERS":
                continue

            print(f"\n[{i+1}/{len(articles)}] Recherche : {ref} - {nom[:30]}")

            try:
                search_url = f"https://www.sidv.fr/produits/recherche?q={ref}"
                driver.get(search_url)

                try:
                    wait = WebDriverWait(driver, 15)
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".product-item-title, .product-item, .product-title, .page-wrapper, body")))
                except TimeoutException:
                    pass

                time.sleep(1.5)

                product_links = driver.find_elements(By.CSS_SELECTOR, ".product-item-title a, a.product-item-title, .product-title a")

                if product_links:
                    href = product_links[0].get_attribute("href")
                    if href:
                        driver.get(href)
                        try:
                            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
                        except Exception:
                            pass
                        time.sleep(1.5)
                else:
                    if "/recherche" in driver.current_url:
                        print("    => Résultat introuvable ou page produit non atteinte.")
                        continue

                pdf_url = None
                try:
                    telechargements_elements = driver.find_elements(By.XPATH, "//*[contains(translate(text(), 'TÉLÉCHARGEMENT', 'téléchargement'), 'téléchargement')]")
                    for tel in telechargements_elements:
                        if tel.is_displayed() and tel.tag_name not in ['script', 'style', 'html', 'body']:
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", tel)
                            time.sleep(0.5)
                            try:
                                tel.click()
                            except ElementClickInterceptedException:
                                driver.execute_script("arguments[0].click();", tel)
                            print("    => Onglet 'Téléchargements' ouvert.")
                            time.sleep(1.5)
                except Exception:
                    pass

                try:
                    dropdowns = driver.find_elements(By.XPATH, f"//tr[contains(., '{ref}')]//button[contains(@class, 'dropdown-toggle')]")
                    if dropdowns:
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", dropdowns[0])
                        time.sleep(0.5)
                        dropdowns[0].click()
                        time.sleep(1)
                        menu_links = driver.find_elements(By.CSS_SELECTOR, ".dropdown-menu.show .dropdown-item")
                        for link in menu_links:
                            text = link.text.lower()
                            if "notice" in text or "fiche" in text or "technique" in text or "doc" in text:
                                pdf_url = link.get_attribute("href")
                                break
                except Exception:
                    pass

                if not pdf_url:
                    links = driver.find_elements(By.TAG_NAME, "a")
                    for link in links:
                        href = link.get_attribute("href")
                        if not href:
                            continue
                        text = link.text.lower()
                        href_lower = href.lower()
                        if ".pdf" in href_lower or "fiche technique" in text or "docs.sidv.fr" in href_lower or "notice" in text or "télécharger" in text:
                            pdf_url = href
                            break

                if not pdf_url:
                    print("    => Fiche technique introuvable sur la page de ce produit.")
                    continue

                pdf_url = urljoin(driver.current_url, pdf_url)
                print(f"    => Fiche localisée : {pdf_url}")

                safe_ref = "".join(c for c in ref if c.isalnum() or c in ('-', '_'))
                dest_filename = f"{safe_ref}_Fiche.pdf"
                dest_path = os.path.join(config.OUTPUT_DIR, dest_filename)

                if download_pdf(pdf_url, dest_path):
                    print(f"    => [SUCCÈS] Téléchargé dans {dest_filename}")

            except Exception as e:
                print(f"    Erreur inattendue sur {ref} : {str(e)}")
                continue

        print("\nFin du processus de recherche et téléchargement.")
    finally:
        driver.quit()

