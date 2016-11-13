from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from view.models import MovieScore, MovieInfo


# Create your views here.
def add(request):
    return render_to_response('sample.html')


def show(request, view_id):
    result = get_object_or_404(MovieInfo, id=view_id)
    return render_to_response('index.html', {'result': result})
