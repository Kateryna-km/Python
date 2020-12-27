import unittest
from Hello import *


class MyTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
        self.client = app.test_client()

    def test_hello(self):
        response = self.client.get('/api/v1/hello-world-10')
        self.assertEqual(200, response.status_code)

    def test_create_user(self):
        #response = self.client.post('/user?username=nh&firstName=n&lastName=h&email=nh@example.com&password=password&phone=1234567000')
        data = {'username': 'test', 'firstName': 'test', 'lastName': 'test', 'email': 'test@ex.com', 'password': 'password',
                'phone': '0000000009'}
        response = self.client.open('/user', method="POST", json=data)
        if not User.query.filter_by(email='test@ex.com').first():
            self.assertEqual(400, response.status_code)
        self.assertEqual(200, response.status_code)


if __name__ == '__main__':
    unittest.main()

# python test.py
# coverage run test.py
# coverage report
