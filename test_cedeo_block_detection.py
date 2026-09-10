import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scraper import is_cedeo_blocked_page


class CedeoBlockDetectionTests(unittest.TestCase):
    def test_detects_datadome_capture_page(self):
        html = """
        <html><body><script>var dd={'host':'geo.captcha-delivery.com'}</script>
        <iframe src="https://geo.captcha-delivery.com/captcha/?initialcid=abc"></iframe>
        </body></html>
        """
        self.assertTrue(is_cedeo_blocked_page("https://www.cedeo.fr/", html))

    def test_allows_login_page(self):
        html = """
        <html><body><form><input type='email' name='email'><input type='password' name='password'></form></body></html>
        """
        self.assertFalse(is_cedeo_blocked_page("https://www.cedeo.fr/connexion", html))


if __name__ == "__main__":
    unittest.main()
