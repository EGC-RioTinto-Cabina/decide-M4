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

    def test_get_user(self):
        username = 'alvaro'
        password = 'entrar123'

        url = 'http://127.0.0.1:8000/gateway/authentication/login/'
        payload = {'username': username, 'password': password}

        token = requests.post(url, data=payload).json()["token"]

        result = GUI.get_user(self, token)
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["username"], "alvaro")
        self.assertEqual(result["is_staff"], True)

    def test_voting_access(self):
        username = 'alvaro'
        password = 'entrar123'
        voting_id = 1

        url = 'http://127.0.0.1:8000/gateway/authentication/login/'
        payload = {'username': username, 'password': password}
        token = requests.post(url, data=payload).json()["token"]

        url = 'http://127.0.0.1:8000/gateway/authentication/getuser/'
        payload = {'token': token}
        user = requests.post(url, data=payload).json()

        result = GUI.check_voting_access(self, user, voting_id)

        self.assertEqual(result, True)

    def test_voting_access_wrong_voting(self):
        username = 'alvaro'
        password = 'entrar123'
        voting_id = 999

        url = 'http://127.0.0.1:8000/gateway/authentication/login/'
        payload = {'username': username, 'password': password}
        token = requests.post(url, data=payload).json()["token"]

        url = 'http://127.0.0.1:8000/gateway/authentication/getuser/'
        payload = {'token': token}
        user = requests.post(url, data=payload).json()

        result = GUI.check_voting_access(self, user, voting_id)

        self.assertEqual(result, False)

    def test_find_voting(self):
        username = 'alvaro'
        password = 'entrar123'
        voting_id = 1

        url = 'http://127.0.0.1:8000/gateway/authentication/login/'
        payload = {'username': username, 'password': password}
        token = requests.post(url, data=payload).json()["token"]

        url = 'http://127.0.0.1:8000/gateway/authentication/getuser/'
        payload = {'token': token}
        user = requests.post(url, data=payload).json()

        voting_access = GUI.check_voting_access(self, user, voting_id)
        self.assertEqual(voting_access, True)

        result = GUI.find_voting(self, voting_id)
        self.assertEqual(result["id"], voting_id)

if __name__ == '__main__':
    unittest.main()
