from django.db import models


class Movie(models.Model):
    name = models.CharField(max_length=100)
    score = models.FloatField(max_length=3)
    score_actor = models.FloatField(max_length=3)
    score_actress = models.FloatField(max_length=3)
    score_director = models.FloatField(max_length=3)
    score_budget = models.FloatField(max_length=3)
    score_movie_box = models.FloatField(max_length=3)
    score_prize = models.FloatField(max_length=3)
    score_investment = models.FloatField(max_length=3)
