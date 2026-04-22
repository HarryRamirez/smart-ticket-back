import factory
from django.contrib.auth.models import User
from tests.custom_faker_providers import EmailProvider
from faker import Faker


fake = Faker()
fake.add_provider(EmailProvider)



class UserFactory(factory.Factory):
    
    class Meta:
        model = User
    
    username = 'KennyHR'
    first_name = 'Kenny Jarrison'
    last_name = 'Ramirez Quezada'
    email = 'kenny@gmail.com'
    password = '12345'
    is_staff = False
    


class UserAdminFactory(factory.Factory):
    
    class Meta:
        model = User
    
    username = 'KennyHR'
    first_name = 'Kenny Jarrison'
    last_name = 'Ramirez Quezada'
    email = 'kenny@gmail.com'
    password = '12345'
    is_staff = True
    is_superuser = True




class UserFactoryFaker(factory.Factory):
    
    class Meta:
        model = User
    
    username = fake.user_name()
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.custom_email()
    password = fake.password()
    




class UserStaffFActory(factory.django.DjangoModelFactory):
    
    class Meta:
        model = User
        
    username = 'KennyHR'
    first_name = 'Kenny Jarrison'
    last_name = 'Ramirez Quezada'
    email = 'kenny@gmail.com'
    password = '12345'
    is_staff = True