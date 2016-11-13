from django.contrib import admin
from view.models import MovieInfo, MovieScore


# Register your models here.
class MovieScoreInLine(admin.TabularInline):
    model = MovieScore
    extra = 0


class MovieInfoAdmin(admin.ModelAdmin):
    #  the list view of all movies
    list_display = ('title', 'genre')

    # search bar
    search_fields = ['title']

    # fields = ['title', 'genre', 'actorIDs', 'directorID', 'length']
    fieldsets = [
        (None, {'fields': ['title']}),
        ('General Information', {'fields': ['genre', 'actorIDs', 'directorID']}),
        ('Other Information', {'fields': ['length'], 'classes': ['collapse']})
    ]
    inlines = [MovieScoreInLine]


admin.site.register(MovieInfo, MovieInfoAdmin)
# admin.site.register(MovieScore)

