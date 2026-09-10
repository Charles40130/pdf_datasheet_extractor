import json
from google import genai
from google.genai import types
import config

MODEL_CANDIDATES = [
    "gemini-2.5-flash",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
]


def extract_products_from_pdf(pdf_path: str) -> list[dict]:
    print(f"--- Analyse du PDF : {pdf_path} ---")
    if not config.API_KEY:
        print("Erreur : Clé API 'GEMINI_API_KEY' manquante dans .env")
        return []

    client = genai.Client(api_key=config.API_KEY)
    try:
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()

        prompt = """
        Extraire les articles de ce devis en liste JSON.
        Chaque objet doit avoir les clés : 'ref', 'nom'.
        Répondre uniquement en JSON brut, sans balises ```json ni autres textes.
        """

        last_error = None
        for model in MODEL_CANDIDATES:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=[prompt, types.Part.from_bytes(data=pdf_data, mime_type="application/pdf")],
                )
                print(f"Modèle Gemini utilisé : {model}")
                net_text = (getattr(response, "text", "") or "").replace('```json', '').replace('```', '').strip()
                parsed = json.loads(net_text)
                if not isinstance(parsed, list):
                    raise ValueError("La réponse Gemini n'est pas une liste JSON valide.")
                return parsed
            except Exception as exc:
                last_error = exc
                if "404" not in str(exc) and "NOT_FOUND" not in str(exc):
                    raise

        raise last_error or RuntimeError("Aucun modèle Gemini compatible n'est disponible.")
    except Exception as e:
        print(f"Erreur lors de l'extraction par IA : {e}")
        return []
