# PDF Datasheet Extractor

Ce projet automatise l’analyse de devis PDF pour identifier les références de produits, puis recherche automatiquement les fiches techniques correspondantes sur un site fournisseur (actuellement SIDV).

Il combine :
- l’extraction d’informations depuis un PDF,
- l’intelligence artificielle pour repérer les articles et leurs références,
- le scraping navigateur pour retrouver et télécharger les fiches techniques associées.

---

## Objectif

À partir d’un devis PDF, le logiciel :

1. lit le document,
2. récupère les références et libellés des produits,
3. interroge Gemini pour extraire les articles au format JSON,
4. ouvre le navigateur sur SIDV,
5. recherche chaque référence,
6. tente de localiser la fiche technique et la télécharge dans le dossier de sortie.

---

## Fonctionnement

### Étape 1 — Extraction du devis
Le script principal détecte un PDF dans `data/input/` et l’envoie à Google Gemini.

Le modèle retourne une liste de produits sous la forme :

```json
[
  {"ref": "4647994", "nom": "Unité extérieure + panels Ixtra M 17 tri"},
  {"ref": "4647988", "nom": "Unité intérieure Ixtra M compact"}
]
```

### Étape 2 — Recherche des fiches techniques
Pour chaque article extrait, le programme lance une recherche sur le site SIDV, puis tente de trouver un lien PDF de documentation technique.

Quand il trouve une fiche compatible, il la télécharge dans :

```text
data/output/
```

---

## Structure du projet

```text
pdf_datasheet_extractor/
├── data/
│   ├── input/          # PDF de devis à traiter
│   └── output/         # fiches techniques téléchargées
├── src/
│   ├── config.py       # configuration du projet
│   ├── extractor.py    # extraction IA des références depuis le PDF
│   ├── scraper.py      # recherche SIDV et téléchargement
│   └── main.py         # point d’entrée
├── .env.example        # exemple de configuration
├── requirements.txt    # dépendances Python
├── README.md           # documentation du projet
├── test_extract.py     # test d’extraction
├── test_scraper.py     # test de navigation/scraping
└── venv/               # environnement virtuel local
```

---

## Prérequis

- Python 3.10+
- Google Chrome installé sur la machine
- Une clé API Gemini valide
- Accès internet pour les recherches SIDV

---

## Installation

1. Créez un environnement virtuel :

```bash
python -m venv venv
source venv/bin/activate
```

2. Installez les dépendances :

```bash
pip install -r requirements.txt
```

3. Configurez les variables d’environnement :

```bash
cp .env.example .env
```

Puis éditez le fichier `.env` et ajoutez :

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

---

## Utilisation

1. Placez un devis PDF dans le dossier :

```text
data/input/
```

2. Lancez le programme :

```bash
python src/main.py
```

3. Le script détecte automatiquement le premier PDF présent.
4. Il extrait les articles via Gemini.
5. Il vous propose ensuite de lancer la recherche SIDV pour récupérer les fiches techniques.

---

## Exemple de flux

```bash
# 1. installation
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. config
cp .env.example .env
# renseigner GEMINI_API_KEY

# 3. ajout d'un devis
cp mon_devis.pdf data/input/

# 4. lancement
python src/main.py
```

---

## Points techniques importants

- Le modèle Gemini utilisé doit être compatible avec l’API actuelle.
- Le scraping Selenium dépend fortement de la structure HTML du site SIDV.
- Les liens de fiches techniques peuvent varier selon les produits ou les pages de fournisseur.
- Si un produit n’a pas de fiche visible sur la page, il est simplement ignoré sans bloquer le traitement global.

---

## Limitations actuelles

- L’extraction repose sur un modèle IA, donc les résultats peuvent varier selon le PDF.
- Le scraping dépend de la stabilité du site cible.
- Les pages fournisseur peuvent changer leur structure HTML et casser le détecteur de pdf.
- Le projet est optimisé pour un workflow de devis et fiches techniques SIDV, mais reste adaptable.

---

## À retenir

Ce projet sert à automatiser un processus de bureau de conception ou commercial :
- extraction des références depuis un devis,
- récupération des dossiers techniques,
- gain de temps sur les tâches répétitives.

Si vous souhaitez, je peux aussi te faire une version encore plus premium avec :
- un README en français plus orienté “projet client”,
- une section “architecture technique”,
- une section “déploiement / CI”,
- ou un README avec badges et exemples visuels.
