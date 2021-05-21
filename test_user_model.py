"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        u1 = User.signup("test1", "email1@email.com", "password", None)
        u2 = User.signup("test2", "email2@email.com", "password", None)

        self.client = app.test_client()

    def tearDown(self):

        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u1 = User.query.get(1)

        # User should have no messages, no followers, no following or likes
        self.assertEqual(len(u1.messages), 0)
        self.assertEqual(len(u1.followers), 0)
        self.assertEqual(len(u1.following), 0)
        self.assertEqual(len(u1.likes), 0)
        # Test the repr function
        repr = u1
        self.assertEqual(u1,repr)

    def test_user_follows(self):
        """Following tests"""

        u1 = User.query.get(1)
        u2 = User.query.get(2)

        u1.following.append(u2)
        db.session.commit()

        # Length of following and following shoud be accurate
        self.assertEqual(len(u1.following),1)
        self.assertEqual(len(u1.followers),0)
        self.assertEqual(len(u2.following),0)
        self.assertEqual(len(u2.followers),1)
        
        # Testing the User model's built in methods
        self.assertTrue(u1.is_following,u2)
        self.assertTrue(u2.is_followed_by,u1)
    
    def test_signup_valid(self):
        u3 = User.signup("test3", "email3@email.com", "password", None)
        u3 = User.query.get(3)

        self.assertEqual(u3.username,'test3')    
        self.assertEqual(u3.email,'email3@email.com')
        
        # Hashing works
        self.assertNotEqual(u3.password,'password')
        self.assertTrue(u3.password.startswith("$2b$"))

    def test_signup_invalid(self):
        """Integrity error should kick in if no email provided"""

        invalid = User.signup("testtest", None, "password", None)
        uid = 123789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_authentication(self):
        u1 = User.query.get(1)

        # User will not be able to login without the right password
        self.assertFalse(User.authenticate(u1.username,'not the password'))