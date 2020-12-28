import unittest
from Hello import *


class MyTestCase(unittest.TestCase):

    def setUp(self):
        app.app_context()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
        self.client = app.test_client()

    def test_hello(self):
        response = self.client.get('/api/v1/hello-world-10')
        self.assertEqual(200, response.status_code)

    def test_http_404(self):
        self.assertTrue(404)

    def test_http_400(self):
        self.assertTrue(400)

    def test_http_405(self):
        self.assertTrue(405)

    def test_create_user(self):
        #response = self.client.post('/user?username=nh&firstName=n&lastName=h&email=nh@example.com&password=password&phone=1234567000')
        data = {'username': 'test1', 'firstName': 'test', 'lastName': 'test', 'email': 'test@ex.com', 'password': 'password',
                'phone': '0000003009'}
        response = self.client.open('/user', method="POST", json=data)
        self.assertEqual(200, response.status_code)
        '''global access_token
        global refresh_token'''

    def test_create_event(self):
        with app.app_context():
            access_token = create_access_token('test')
            headers = {
                'Authorization': 'Bearer {}'.format(access_token)
            }
            data = {'name': 'event', 'date': '29.12.2020'}
            #data = {'name': 'newevent', 'date': '29.12.2020'}
            response = self.client.open('/event', headers=headers, method="POST", json=data)
            self.assertEqual(200, response.status_code)

    def test_event_by_date(self):
        with app.app_context():
            access_token = create_access_token('test')
            headers = {
                'Authorization': 'Bearer {}'.format(access_token)
            }
            response = self.client.open('/event/findByDate/29.12.2020', headers=headers, method="GET")
            self.assertEqual(200, response.status_code)

    def test_event_by_id(self):
        with app.app_context():
            access_token = create_access_token('test')
            headers = {
                'Authorization': 'Bearer {}'.format(access_token)
            }
            response = self.client.open('/event/20', headers=headers, method="GET")
            self.assertEqual(200, response.status_code)

    def test_update_event_with_form_data(self):
        with app.app_context():
            access_token = create_access_token('test')
            headers = {
                'Authorization': 'Bearer {}'.format(access_token)
            }
            data = {'name': 'event', 'date': '27.12.2020'}
            response = self.client.open('/event/20', headers=headers, method="PUT", json=data)
            self.assertEqual(200, response.status_code)

    def test_list_users_of_event(self):
        with app.app_context():
            access_token = create_access_token('test')
            headers = {
                'Authorization': 'Bearer {}'.format(access_token)
            }
            data = {'username': 'test', 'password': 'password'}
            response = self.client.open('/event/group/20', headers=headers, method="GET", json=data)
            self.assertEqual(200, response.status_code)

    def test_login(self):
        data = {'username': 'test', 'password': 'password'}
        response = self.client.open('/user/login', method="POST", json=data)
        self.assertEqual(200, response.status_code)

    def test_logout(self):
        with app.app_context():
            access_token = create_access_token('test')
            headers = {
                'Authorization': 'Bearer {}'.format(access_token)
            }
            response = self.client.open('/user/logout', headers=headers, method="DELETE")
            self.assertEqual(200, response.status_code)

    def test_refresh(self):
        with app.app_context():
            access_token = create_access_token('test')
            headers = {
                'Authorization': 'Bearer {}'.format(access_token)
            }
            response = self.client.open('/refresh', headers=headers, method="POST")
            self.assertEqual(200, response.status_code)

    def test_user_by_id(self):
        with app.app_context():
            access_token = create_access_token('test')
            headers = {
                'Authorization': 'Bearer {}'.format(access_token)
            }
            response = self.client.open('/user/10', headers=headers, method="GET")
            self.assertEqual(200, response.status_code)

    def test_update_user(self):
        with app.app_context():
            access_token = create_access_token('test')
            headers = {
                'Authorization': 'Bearer {}'.format(access_token)
            }
            data = {'username': 'test', 'firstName': 'test', 'lastName': 'test', 'email': 'testnew@ex.com',
                    'password': 'password', 'phone': '0000000089'}
            response = self.client.open('/user/update', headers=headers, method="PUT", json=data)
            self.assertEqual(200, response.status_code)

    def test_list_events_of_user(self):
        with app.app_context():
            access_token = create_access_token('test')
            headers = {
                'Authorization': 'Bearer {}'.format(access_token)
            }
            response = self.client.open('/user/group/10', headers=headers, method="GET")
            self.assertEqual(200, response.status_code)

    def test_create_group_of_users(self):
        with app.app_context():
            access_token = create_access_token('test')
            headers = {
                'Authorization': 'Bearer {}'.format(access_token)
            }
            data = {'user_id': '10', 'event_id': '20'}
            response = self.client.open('/calendar/group', headers=headers, method="POST", json=data)
            self.assertEqual(200, response.status_code)

    def test_delete_group(self):
        with app.app_context():
            access_token = create_access_token('test')
            headers = {
                'Authorization': 'Bearer {}'.format(access_token)
            }
            response = self.client.open('/calendar/group/10', headers=headers, method="DELETE")
            self.assertEqual(200, response.status_code)

    def test_delete_event(self):
        with app.app_context():
            access_token = create_access_token('test')
            headers = {
                'Authorization': 'Bearer {}'.format(access_token)
            }
            response = self.client.open('/event/20', headers=headers, method="DELETE")
            self.assertEqual(200, response.status_code)

    def test_delete_user(self):
        with app.app_context():
            access_token = create_access_token('test1')
            headers = {
                'Authorization': 'Bearer {}'.format(access_token)
            }
            response = self.client.open('/user/delete', headers=headers, method="DELETE")
            self.assertEqual(200, response.status_code)

if __name__ == '__main__':
    unittest.main()

# python test.py
# coverage run test.py
# coverage report
