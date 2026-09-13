from django.core.management.base import BaseCommand
from faker import Faker
from main.models import News


class Command(BaseCommand):
    help = 'Fill full_content with random English text'

    def handle(self, *args, **options):
        fake = Faker()   # English

        for news in News.objects.all():
            news.full_content = '\n\n'.join(fake.paragraphs(nb=3))
            news.save()
            self.stdout.write(f'Filled: {news.title}')

        self.stdout.write(self.style.SUCCESS('Done.'))