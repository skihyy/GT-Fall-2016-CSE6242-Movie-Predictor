# coding: utf-8
from django.shortcuts import render
from history.models import Movie


def request_handler(request):
    """
    :param request: request from get
    :return: web page based on the GET
    """
    mid = request.GET.get('mid', "")
    # if something to query, go to query the historical data
    if mid:
        return get_movie(mid, request)
    # if nothing input, go to home page
    else:
        return render(request, 'history/home.html')


def get_movie(mid, request):
    movie_chart = []
    movie = Movie.objects.get(id=mid)
    movie_chart.append(movie)
    return render(request, 'history/home.html', {'scoreChat':movie_chart})
