from django.core.management.base import BaseCommand
from django.utils import timezone

import pandas as pd

from searchapp.models import Lower


def load_and_clean_ratings():
    ratings = pd.read_csv('BX-Book-Ratings.csv', encoding='cp1251', sep=';')
    ratings = ratings[ratings['Book-Rating'] != 0]
    return ratings


def load_and_clean_books():
    books = pd.read_csv('BX-Books.csv', encoding='cp1251', sep='\";\"', error_bad_lines=False)

    books['Book-Title'] = books['Book-Title'].replace('&amp;', '&', regex=True)
    books['Book-Author'] = books['Book-Author'].replace('&amp;', '&', regex=True)
    books['Publisher'] = books['Publisher'].replace('&amp;', '&', regex=True)
    books.columns = books.columns.str.replace("\"", '')
    books['ISBN'] = books['ISBN'].map(lambda x: x.lstrip('"'))
    books['Image-URL-L'] = books['Image-URL-L'].map(lambda x: x[:-1])
    return books


class Command(BaseCommand):
    help = (
        "Generates lowercase dataset, that is created upon merging rating dataset and books dataset "
        " on ISBN column and loads its content into db table Lowers in bulk loads."
    )

    def handle(self, *args, **options):
        start_time = timezone.now()
        # Load cleaned ratings
        ratings = load_and_clean_ratings()
        # Load cleaned books
        books = load_and_clean_books()
        # Merge datasets on ISBN column into one that will be used for searching
        dataset = pd.merge(ratings, books, on=['ISBN'])
        # Convert string values of dataset into lower characters
        dataset_lowercase = dataset.applymap(lambda s: s.lower() if type(s) == str else s)

        print('Dataset ready, starting insertion into db.')
        data = []
        # Load data into sql table in bulks
        for index, row in dataset_lowercase.iterrows():
            data_temp = Lower(
                user_id=row[0],
                isbn=row[1],
                book_rating=row[2],
                book_title=row[3],
                book_author=row[4],
                year_of_publication=row[5],
                publisher=row[6],
                image_url_s=row[7],
                image_url_m=row[8],
                image_url_l=row[9]
            )
            data.append(data_temp)
            if len(data) > 5000:
                Lower.objects.bulk_create(data)
                data = []

        if data:
            Lower.objects.bulk_create(data)
        end_time = timezone.now()
        self.stdout.write(
            self.style.SUCCESS(
                f"Loading CSV took: {(end_time - start_time).total_seconds()} seconds."
            )
        )
