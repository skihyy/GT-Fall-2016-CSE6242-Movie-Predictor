from django.contrib import admin
from view.models import *


# Register your models here.
class MovieScoreInLine(admin.TabularInline):
    model = MovieScore
    extra = 0


class MovieInfoAdmin(admin.ModelAdmin):
    #  the list view of all movies
    list_display = ('id', 'title', 'genre')

    # search bar
    search_fields = ['title']

    # fields = ['title', 'genre', 'actorIDs', 'directorID', 'length']
    fieldsets = [
        (None, {'fields': ['title']}),
        ('General Information', {'fields': ['genre', 'actor_ids', 'director_id']}),
        ('Other Information', {'fields': ['length'], 'classes': ['collapse']})
    ]
    inlines = [MovieScoreInLine]


class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'genre')


class AggregateInfoAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'number_of_movies',
                    'score',
                    'actor_score',
                    'actress_score',
                    'director_score',
                    'length_score',
                    'genre_score',
                    'avg_movie_box')


admin.site.register(MovieInfo, MovieInfoAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(AggregateInfo, AggregateInfoAdmin)
# admin.site.register(MovieScore)
