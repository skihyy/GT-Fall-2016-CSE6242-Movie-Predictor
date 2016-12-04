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

    # fields = ['title', 'genre', 'actorIDs', 'directorID', 'duration']
    fieldsets = [
        (None, {'fields': ['title']}),
        ('General Information', {'fields': ['genre', 'actor_ids', 'director_id']}),
        ('Other Information', {'fields': ['duration'], 'classes': ['collapse']})
    ]
    inlines = [MovieScoreInLine]


class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'genre')


class PersonInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'num_of_movies', 'sex_is_male', 'average_score', 'type_is_director')


class AggregateInfoAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'number_of_movies',
                    'score',
                    'actor_score',
                    'actress_score',
                    'director_score',
                    'duration_score',
                    'genre_score',
                    'avg_movie_box')


admin.site.register(Person, PersonInfoAdmin)
admin.site.register(MovieInfo, MovieInfoAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(AggregateInfo, AggregateInfoAdmin)
