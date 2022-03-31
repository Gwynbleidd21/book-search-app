from django.shortcuts import render
from .models import Book, Lower
from django.db import connection
import json
from django.views import View
import pandas as pd
import numpy as np


class SearchCorrelatedBooks(View):
    """
    View class which holds the whole logic of finding the recommended books for user according to book-title or
    book-author.
    """
    query_title = ''
    query_author = ''
    dataset_lowercase = None
    dataset_for_corr = None
    ratings_data_raw = None
    threshold = 6

    def get(self, request):
        query = str(Lower.objects.all().query)
        self.dataset_lowercase = pd.read_sql_query(query, connection, index_col='id', )
        self.query_title = request.GET.get('search_title').lower()
        self.query_author = request.GET.get('search_author').lower()
        data = json.loads(self.search_engine())
        return render(request, 'search.html', {'query': self.query_title, 'results': data})

    def check_input(self):
        """
        Check input from user. If either book title or both title and author are given -> we can proceed with search
        if not there is no title on input, don't start with search and just return empty json for frontend.
        """
        if self.query_title and self.query_author:
            return self.dataset_lowercase['user_id'][
                (self.dataset_lowercase['book_title'] == self.query_title) &
                (self.dataset_lowercase['book_author'].str.contains(self.query_author, case=False))]
        elif self.query_title:
            return self.dataset_lowercase['user_id'][self.dataset_lowercase['book_title'] == self.query_title]
        else:
            return json.dumps({})

    def find_correlated(self):
        """Compute correlation of books towards the book from input and compose the final DataFrame."""
        dataset_of_other_books = self.dataset_for_corr.copy(deep=False)
        dataset_of_other_books.drop([self.query_title], axis=1, inplace=True)

        book_titles = []
        correlations = []
        avg_rating = []
        # corr computation
        for book_title in list(dataset_of_other_books.columns.values):
            book_titles.append(book_title)
            correlations.append(self.dataset_for_corr[self.query_title].corr(dataset_of_other_books[book_title]))
            tab = (self.ratings_data_raw[self.ratings_data_raw['book_title'] == book_title].groupby(
                self.ratings_data_raw['book_title']).mean())
            avg_rating.append(tab['book_rating'].min())

        # final dataframe of all correlation of each book
        corr_fellowship = pd.DataFrame(list(zip(book_titles, correlations, avg_rating)),
                                       columns=['book', 'corr', 'avg_rating'])
        return corr_fellowship.sort_values('corr', ascending=False).head(10)

    def search_engine(self):
        """
        Searching logic:
         - filter books according to a certain number of rating from users
         - compute mean of all of the ratings
         - create final dataset with 3 columns (Book title, average rating value and value representing correlation
         to the input book
         """
        input_readers = np.unique(self.check_input().tolist())
        # final dataset
        books_of_input_readers = self.dataset_lowercase[(self.dataset_lowercase['user_id'].isin(input_readers))]

        # Number of ratings per other books in dataset
        number_of_rating_per_book = books_of_input_readers.groupby(['book_title']).agg('count').reset_index()

        # Select only books which have actually higher number of ratings than threshold
        books_to_compare = number_of_rating_per_book['book_title'][number_of_rating_per_book['user_id']
                                                                   >= self.threshold]
        books_to_compare = books_to_compare.tolist()
        # Situation, when after being filtered by threshold, there are no books
        if len(books_to_compare) < 1:
            return json.dumps({})

        self.ratings_data_raw = books_of_input_readers[['user_id', 'book_rating', 'book_title']][
            books_of_input_readers['book_title'].isin(books_to_compare)]

        # group by User and Book and compute mean
        ratings_data_raw_nodup = self.ratings_data_raw.groupby(['user_id', 'book_title'])['book_rating'].mean()

        # reset index to see user_id in every row
        ratings_data_raw_nodup = ratings_data_raw_nodup.to_frame().reset_index()

        self.dataset_for_corr = ratings_data_raw_nodup.pivot(
            index='user_id', columns='book_title', values='book_rating'
        )
        result_list = [self.find_correlated()]
        return result_list[0].reset_index().to_json(orient='records')


def book_list(request):
    """View that returns selected number of books to preview in homepage."""
    book = Book.objects.all().order_by('-year_of_publication')
    return render(request, 'book_list.html', {'book': book[100:124]})


def book_detail(request, book_name):
    """View that selects one book according to book_title from user."""
    book = Book.objects.filter(book_title__icontains=book_name)
    return render(request, 'book_detail.html', {'book': book[0]})
