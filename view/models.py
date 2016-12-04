from django.db import models


# Create your models here.


class Person(models.Model):
    """
    This person can be either a director or a actor or both.
    If she is both, then there will be 2 records in this table,
    one as a actress, and the other one as a director.
    """
    name = models.CharField(max_length=40)
    average_score = models.FloatField()
    type_is_director = models.BooleanField()
    num_of_movies = models.IntegerField()

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class AggregateInfo(models.Model):
    """
    Aggregate information is used to show the average score of all recorded movies.
    It should only contain 1 record, which is all total score of all movies in each fields.
    Every time when a user add a new movie, the system should automatically update this score.
    And then parse the new average score back to user to show the differences in radar chart.
    """
    number_of_movies = models.IntegerField()
    score = models.FloatField()
    first_actor_genre_score = models.FloatField()
    second_actor_genre_score = models.FloatField()
    first_actor_director_score = models.FloatField()
    second_actor_director_score = models.FloatField()
    director_genre_score = models.FloatField()
    first_actor_score = models.FloatField()
    second_actor_score = models.FloatField()
    director_score = models.FloatField()
    genre_score = models.FloatField()

    def __str__(self):
        return str(self.number_of_movies) + " movies"

    def __unicode__(self):
        return str(self.number_of_movies) + " movies"


class Genre(models.Model):
    """
    This table contains 2 attributes, id and movie genre, which later will be used as a foreign key in the movie.
    """
    genre = models.CharField(max_length=100)

    def __str__(self):
        return self.genre

    def __unicode__(self):
        return self.genre


class MovieInfo(models.Model):
    """
    This class is what a user will enter, containing the information of a user defined movie.
    Title must be shorter than 200 characters.
    Genre is provided.
    Actors should also be provided.
    Directors should also be provided.
    duration is in minutes.
    """
    title = models.CharField(max_length=200)
    genre = models.ForeignKey(Genre)
    first_actor_id = models.IntegerField()
    second_actor_id = models.IntegerField()
    director_id = models.IntegerField()

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title


class MovieScore(models.Model):
    """
    This class should be generated after user enter the information of a new user defined movie.
    This will provide a new score for the movie.
    And then information will be parsed to the sample.html to show the differences in radar chart.
    """
    movie = models.ForeignKey(MovieInfo)
    score = models.FloatField()
    first_actor_genre_score = models.FloatField()
    second_actor_genre_score = models.FloatField()
    first_actor_director_score = models.FloatField()
    second_actor_director_score = models.FloatField()
    director_genre_score = models.FloatField()
    first_actor_score = models.FloatField()
    second_actor_score = models.FloatField()
    director_score = models.FloatField()
    genre_score = models.FloatField()

    def __str__(self):
        return self.movie.title

    def __unicode__(self):
        return self.movie.title
