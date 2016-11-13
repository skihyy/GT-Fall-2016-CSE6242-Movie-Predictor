from django.db import models


# Create your models here.


class MovieInfo(models.Model):
    title = models.CharField(max_length=200)
    genre = models.IntegerField()
    actorIDs = models.CharField(max_length=200)
    directorID = models.IntegerField()
    length = models.IntegerField()

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title


class MovieScore(models.Model):
    movie = models.ForeignKey(MovieInfo)
    score = models.FloatField()
    actorScore = models.FloatField()
    directorScore = models.FloatField()
    lengthScore = models.FloatField()
    genreScore = models.FloatField()

    def __str__(self):
        return repr(self.score)

    def __unicode__(self):
        return self.score
