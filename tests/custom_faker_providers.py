from faker import Faker
from faker.providers import BaseProvider


faker = Faker()


class EmailProvider(BaseProvider):
    
    def custom_email(self):
        return f'{faker.first_name().lower()}@gmail.com'