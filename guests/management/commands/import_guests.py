from django.core.management import BaseCommand
from guests import csv_import


class Command(BaseCommand):
    args = 'filename'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            action='store',
            dest='csv',
            help='Csv of guests to import'
        )

    def handle(self, *args, **options):
        csv_import.import_guests(options['csv'])
