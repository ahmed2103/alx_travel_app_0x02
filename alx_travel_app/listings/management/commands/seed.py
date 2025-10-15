from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from alx_travel_app.listings.models import Listing
import random
from faker import Faker

class Command(BaseCommand):
    help = 'seed the data with fake data'

    def handle(self, *args, **options):
        fake = Faker()
        User = get_user_model()

        self.stdout.write(self.style.SUCCESS('Seeding database...'))

        user, created = User.objects.get_or_create(email='test@test.cpm', defaults={'password': 'testpassword'})

        for _ in range(20):
            Listing.objects.create(
                title=fake.sentence(nb_words=5),
                description=fake.paragraph(nb_sentences=3),
                location=fake.city(),
                price_per_night= random.uniform(50.00, 500.00),
                owner=user)

        self.stdout.write(self.style.SUCCESS('Database seeded successfully'))