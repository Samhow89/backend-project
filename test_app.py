import unittest
from project import app
from base64 import b64encode


class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_root_endpoint(self):
        response = self.app.get('/', headers={
            'Authorization': 'Basic ' + b64encode(b"admin:password123").decode('utf-8')
        })
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
