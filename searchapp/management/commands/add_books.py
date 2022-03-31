from django.core.management.base import BaseCommand
from django.utils import timezone

from searchapp.models import Book
from .add_data import load_and_clean_books


class Command(BaseCommand):
    help = (
        "Generates a Book table with only unique books."
    )

    def handle(self, *args, **options):
        start_time = timezone.now()
        # Load cleaned books
        books = load_and_clean_books()
        # Filter to get only unique books
        books_unique = books.drop_duplicates(subset=['Book-Title'], keep='first')
        # Load data into sql table in bulks
        data = []
        for index, row in books_unique.iterrows():
            data_temp = Book(
                isbn=row[0],
                book_title=row[1],
                book_author=row[2],
                year_of_publication=row[3],
                publisher=row[4],
                image_url_s=row[5],
                image_url_m=row[6],
                image_url_l=row[7]
            )
            data.append(data_temp)
            # Not loading books one at a time but 5000 at a time
            if len(data) > 5000:
                Book.objects.bulk_create(data)
                data = []
        # After last iteration there can be leftover data
        if data:
            Book.objects.bulk_create(data)

        end_time = timezone.now()
        self.stdout.write(
            self.style.SUCCESS(
                f"Loading CSV took: {(end_time - start_time).total_seconds()} seconds."
            )
        )
