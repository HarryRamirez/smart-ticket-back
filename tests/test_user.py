from django.test import TestCase, Client
import pytest
# from faker import Faker
# from tests.custom_faker_providers import EmailProvider
# from ddf import G, N, F
from django.contrib.auth.models import User

from tests.factories import UserFactory, UserStaffFActory, UserAdminFactory


# 'username', 'first_name', 'last_name', 'email', 'password'

# fake = Faker()
# fake.add_provider(EmailProvider)

# @pytest.fixture
# def user_creation():
#     return N(User)


# @pytest.mark.django_db # damos acceso a la base de datos
# def test_user_creation(user_creation):
#     print(user_creation.username)
#     print(user_creation.email)
#     user_creation.is_staff = False
#     user_creation.save()
#     assert user_creation.is_staff == False
    
    

# @pytest.mark.django_db
# def test_sepueruser_creation(user_creation):
#     user_creation.is_superuser = True
#     user_creation.is_staff = True
#     user_creation.save()
#     assert user_creation.is_superuser
    


# @pytest.mark.django_db
# def test_staff_user_creation(user_creation):
#     user_creation.is_staff = True
#     user_creation.save()
#     assert user_creation.is_staff
    



# @pytest.mark.django_db
# def test_user_creation_fail():
    
#     with pytest.raises(Exception):
#         User.objects.create_user(
#             password='12345678',
#             is_staff=True
#         )





class TestCaseUser(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.common_user = UserFactory.create()
        self.admin_user = UserAdminFactory.create()
        
    
    def test_common_user_creation(self):
        self.assertEqual(self.common_user.is_active, True)
        self.assertEqual(self.common_user.is_staff, False)
        self.assertEqual(self.common_user.is_superuser, False)
        
    
    def test_admin_user_creation(self):
        self.assertEqual(self.admin_user.is_staff, True)
        self.assertEqual(self.admin_user.is_superuser, True)
    
    
    def test_login(self):
        response = self.client.post('/login/', {'username': 'admin', 'password': 'admin'})
        
        print(response.status_code)