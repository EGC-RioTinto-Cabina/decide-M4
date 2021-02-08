import unittest, requests
from main import GUI


class TestStringMethods(unittest.TestCase):

    def test_login(self):
        username = 'alvaro'
        password = 'entrar123'

        url = 'http://127.0.0.1:8000/gateway/authentication/login/'
        payload = {'username': username, 'password': password}

        token = requests.post(url, data=payload).json()["token"]

        result = GUI.login(self, username, password)
        self.assertEqual(result, token)

    def test_wrong_login(self):
        username = 'alvaro'
        password = 'entrar122'

        result = GUI.login(self, username, password)
        self.assertEqual(result, None)

if __name__ == '__main__':
    unittest.main()
