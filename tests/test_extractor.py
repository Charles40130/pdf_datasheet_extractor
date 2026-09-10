import types

import sys

sys.path.append("src")

import config
import extractor


def test_extract_products_uses_supported_gemini_model(monkeypatch, tmp_path):
    pdf_path = tmp_path / "quote.pdf"
    pdf_path.write_bytes(b"fake pdf")

    captured = {}

    class DummyResponse:
        text = "```json\n[{\"ref\": \"ABC123\", \"nom\": \"Produit test\"}]\n```"

    class DummyModels:
        def generate_content(self, *, model, contents):
            captured["model"] = model
            return DummyResponse()

    class DummyClient:
        def __init__(self, api_key):
            self.api_key = api_key
            self.models = DummyModels()

    monkeypatch.setattr(config, "API_KEY", "dummy-key")
    monkeypatch.setattr(extractor.genai, "Client", lambda api_key: DummyClient(api_key))

    results = extractor.extract_products_from_pdf(str(pdf_path))

    assert results == [{"ref": "ABC123", "nom": "Produit test"}]
    assert captured["model"] == "gemini-2.5-flash"
