from django.db import models


# Create model of book
class Book(models.Model):
    isbn = models.CharField(max_length=150)
    book_title = models.CharField(max_length=255)
    book_author = models.CharField(max_length=150)
    year_of_publication = models.IntegerField()
    publisher = models.CharField(max_length=150)
    image_url_s = models.CharField(max_length=255)
    image_url_m = models.CharField(max_length=255)
    image_url_l = models.CharField(max_length=255)

    class Meta:
        ordering = ('book_title',)

    def __str__(self):
        return self.book_title


# Create mode of merged dataset of rating and books
class Lower(models.Model):
    user_id = models.BigIntegerField()
    isbn = models.CharField(max_length=150)
    book_rating = models.IntegerField()
    book_title = models.CharField(max_length=255)
    book_author = models.CharField(max_length=150)
    year_of_publication = models.IntegerField()
    publisher = models.CharField(max_length=150)
    image_url_s = models.CharField(max_length=255)
    image_url_m = models.CharField(max_length=255)
    image_url_l = models.CharField(max_length=255)

    def __str__(self):
        return self.book_title



