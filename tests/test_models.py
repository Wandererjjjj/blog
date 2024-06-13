import unittest
from app import create_app, db
from app.models import User, Post


class ModelsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_creation(self):
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'testuser')

    def test_password_hashing(self):
        user = User(username='testuser')
        user.set_password('password')
        self.assertFalse(user.check_password('wrongpassword'))
        self.assertTrue(user.check_password('password'))

    def test_post_creation(self):
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        post = Post(title='Test Post', body='This is a test post.', author=user)
        db.session.add(post)
        db.session.commit()
        self.assertEqual(Post.query.count(), 1)
        self.assertEqual(Post.query.first().title, 'Test Post')

    def test_post_author_relationship(self):
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        post = Post(title='Test Post', body='This is a test post.', author=user)
        db.session.add(post)
        db.session.commit()
        self.assertEqual(post.author.username, 'testuser')


if __name__ == '__main__':
    unittest.main()