import unittest
from app import create_app, db
from app.models import User, Post
from flask import url_for


class RoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            self.create_test_user()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def create_test_user(self):
        with self.app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()

    def login(self, username, password):
        return self.client.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to Flask Blog', response.data)

    def test_login(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign In', response.data)

        response = self.login('testuser', 'password')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to Flask Blog', response.data)

    def test_register(self):
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)

        response = self.client.post('/register', data=dict(
            username='newuser',
            email='newuser@example.com',
            password='newpassword',
            password2='newpassword'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Congratulations, you are now a registered user!', response.data)

    def test_create_post(self):
        self.login('testuser', 'password')
        response = self.client.get('/create_post')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create Post', response.data)

        response = self.client.post('/create_post', data=dict(
            title='Test Post',
            body='This is a test post.'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your post is now live!', response.data)

        with self.app.app_context():
            post = Post.query.filter_by(title='Test Post').first()
            self.assertIsNotNone(post)

    def test_post_view(self):
        self.login('testuser', 'password')
        with self.app.app_context():
            post = Post(title='Test Post', body='This is a test post.', author=User.query.first())
            db.session.add(post)
            db.session.commit()

        with self.app.app_context():
            response = self.client.get(url_for('main.post', id=post.id))
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Test Post', response.data)
            self.assertIn(b'This is a test post.', response.data)

    def test_api_get_posts(self):
        response = self.client.get('/api/posts')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')

    def test_api_create_post(self):
        self.login('testuser', 'password')
        response = self.client.post('/api/posts', json={
            'title': 'API Test Post',
            'body': 'This is a test post created via API.'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('API Test Post', response.get_json()['title'])

    def test_api_update_post(self):
        self.login('testuser', 'password')
        with self.app.app_context():
            post = Post(title='Test Post', body='This is a test post.', author=User.query.first())
            db.session.add(post)
            db.session.commit()

        with self.app.app_context():
            response = self.client.put(f'/api/posts/{post.id}', json={
                'title': 'Updated Test Post',
                'body': 'This is an updated test post.'
            })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type, 'application/json')
            self.assertIn('Updated Test Post', response.get_json()['title'])

    def test_api_delete_post(self):
        self.login('testuser', 'password')
        with self.app.app_context():
            post = Post(title='Test Post', body='This is a test post.', author=User.query.first())
            db.session.add(post)
            db.session.commit()

        with self.app.app_context():
            response = self.client.delete(f'/api/posts/{post.id}')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type, 'application/json')
            self.assertTrue(response.get_json()['result'])

        with self.app.app_context():
            post = Post.query.get(post.id)
            self.assertIsNone(post)


if __name__ == '__main__':
    unittest.main()