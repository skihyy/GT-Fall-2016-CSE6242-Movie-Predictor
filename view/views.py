from django.shortcuts import render
from view.models import *
import random
import math
import json
import moviescorepredictorml
from urllib import urlopen


# Create your views here.
def add(request):
    """
    Go to add a movie page.
    :param request: http request
    :return: web page of adding a movie
    """
    testMovieScore()

    genre = Genre.objects.all()
    director_data, actor_data = get_directors_actors()
    return render(request,
                  'input.html',
                  {'genres': genre,
                   'directors': director_data,
                   'actors': actor_data})


def testMovieScore():
    print(moviescorepredictorml.movie_score('Robert Pattinson', 'David Yates', 'Romance'))  # actor, director, genre


def show(request):
    """
    Handling the new movie information and generate result page.
    :param request: http request
    :return: web page of result
    """
    genre_selected = Genre.objects.get(id=request.POST["genre"])

    # handle actors entered
    # if in the DB, get her or him
    # if not, create one
    actors_name_from_form = request.POST["actors"]
    actor_name_list = actors_name_from_form.split(",")
    # get rid of space
    actor_range = range(len(actor_name_list))
    for i in actor_range:
        actor_name_list[i] = actor_name_list[i].strip()
    actor_list = []
    actor_id = ""
    for temp_actor_name in actor_name_list:
        temp_actor_list = Person.objects.filter(name=temp_actor_name, type_is_director=False)
        if 0 == len(temp_actor_list):
            if 0 == random.uniform(0, 1):
                temp_actor = Person(name=temp_actor_name, type_is_director=False,
                                    sex_is_male=False, average_score=0, num_of_movies=0)
            else:
                temp_actor = Person(name=temp_actor_name, type_is_director=False,
                                    sex_is_male=True, average_score=0, num_of_movies=0)
            temp_actor.save()
            temp_actor = Person.objects.last()
        else:
            temp_actor = temp_actor_list[0]

        actor_list.append(temp_actor)
        actor_id += str(temp_actor.id) + ","

    director_name = request.POST["director"]
    director_list = Person.objects.filter(name=director_name, type_is_director=True)

    # same way for a director
    if 0 == len(director_list):
        if 0 == random.uniform(0, 1):
            director = Person(name=director_name, type_is_director=True, average_score=0,
                              num_of_movies=0, sex_is_male=False)
        else:
            director = Person(name=director_name, type_is_director=True, average_score=0,
                              num_of_movies=0, sex_is_male=True)
        director.save()
        director = Person.objects.last()
    else:
        director = director_list[0]

    director_id = director.id

    movie_info = MovieInfo(
        title=request.POST["title"],
        genre=genre_selected,
        actor_ids=actor_id,
        director_id=director_id,
        duration=request.POST["duration"]
    )

    movie_info.save()
    saved_movie_info = MovieInfo.objects.last()
    # for general use
    saved_movie_score, saved_aggregate_info = compute_score(saved_movie_info, actor_list, director)
    # for radar chart
    chart_js_data = get_chart_js_value(saved_aggregate_info=saved_aggregate_info, saved_movie_score=saved_movie_score)
    # for radar chart analysis
    general_analysis = create_genreal_analysis(saved_movie_score)
    # for score percentages
    score_components = score_components_maker()
    # for comparison chart
    num_of_movies_list, avg_director_score_list, avg_actor_score_list, avg_actress_score_list = get_num_of_movies_list()

    return render(request,
                  'output.html',
                  {'chart_js_data': chart_js_data,
                   'movie_title': saved_movie_info.title,
                   'movie_score': json_score(saved_movie_score),
                   'general_analysis': general_analysis,
                   'score_components': score_components,
                   'num_of_movies_list': num_of_movies_list,
                   'avg_director_score_list': avg_director_score_list,
                   'avg_actor_score_list': avg_actor_score_list,
                   'avg_actress_score_list': avg_actress_score_list})


def compute_score(saved_movie_info, actor_list, director):
    """
    A method used to compute the score of a movie.
    Currently, it used a random number genreator for predicting movie score.
    But later this should be fixed by using a real learner.
    :param saved_movie_info: A movie information object
    :param actor_list: A list of person objects for actors / actresses
    :param director: A person object for director
    :return: A movie score object contains all score of it and the aggregate score information
    """
    # actors score
    temp_actor_score = 0.0
    num_of_actors = 0
    temp_actress_score = 0.0
    num_of_actress = 0
    for actor in actor_list:
        temp_genreated_score = random.uniform(3, 9)
        if actor.sex_is_male:
            temp_actor_score += temp_genreated_score
            num_of_actors += 1
        else:
            temp_actress_score += temp_genreated_score
            num_of_actress += 1
        # update data
        temp_actor_total_score = float(actor.average_score) * float(actor.num_of_movies) + temp_genreated_score
        actor.num_of_movies += 1
        actor.average_score = temp_actor_total_score / actor.num_of_movies
        actor.save()

    if 0 != num_of_actors:
        temp_actor_score /= num_of_actors
    if 0 != num_of_actress:
        temp_actress_score /= num_of_actress

    # director score
    temp_director_score = random.uniform(3, 9)
    director.num_of_movies += 1
    director.average_score = (float(director.average_score) * (director.num_of_movies - 1)
                              + temp_director_score) / float(director.num_of_movies)
    director.save()

    temp_duration_score = random.uniform(3, 9)
    temp_genre_score = random.uniform(3, 9)
    temp_box_score = random.uniform(3, 9)
    temp_score = (temp_actor_score + temp_actress_score +
                  temp_director_score + temp_duration_score +
                  temp_genre_score + temp_box_score) / 6

    movie_score = MovieScore(movie=saved_movie_info,
                             actor_score=temp_actor_score,
                             director_score=temp_director_score,
                             duration_score=temp_duration_score,
                             genre_score=temp_genre_score,
                             score=temp_score,
                             actress_score=temp_actress_score,
                             avg_movie_box=temp_box_score)

    # save to database
    movie_score.save()

    # get from database object since it has strict format requirement
    saved_movie_score = MovieScore.objects.last()

    aggregate_score_object = AggregateInfo.objects.get(id=1)

    # update information
    aggregate_score_object.number_of_movies += 1
    aggregate_score_object.actor_score += saved_movie_score.actor_score
    aggregate_score_object.actress_score += saved_movie_score.actress_score
    aggregate_score_object.director_score += saved_movie_score.director_score
    aggregate_score_object.duration_score += saved_movie_score.duration_score
    aggregate_score_object.genre_score += saved_movie_score.genre_score
    aggregate_score_object.avg_movie_box += saved_movie_score.avg_movie_box
    aggregate_score_object.score += saved_movie_score.score

    # update database
    aggregate_score_object.save()

    saved_aggregate_info = AggregateInfo.objects.get(id=1)

    return saved_movie_score, saved_aggregate_info


def create_genreal_analysis(saved_movie_score):
    """
    Based on the score received, genreate analysis.
    :param saved_movie_score: a movie score object
    :return: a plain text paragraph for analysis
    """
    analysis = {}
    if 5 > saved_movie_score.score:
        analysis["general"] = "Compared to other movies, yours may need improvement. " \
                              "Did you make a mistake by entering incorrect information? "
    elif 7 > saved_movie_score.score:
        analysis["general"] = "Compared to other movies, not bad! Actually, it is a good movie. "
    else:
        analysis["general"] = "Compared to other movies, your movie will be the best-seller! "

    if 0 != saved_movie_score.actor_score:
        if 5 > saved_movie_score.actor_score:
            analysis["actor"] = "Maybe you could have other actors here. " \
                                "They may have different experiences which may help you be even " \
                                "more successful in this movie!"
        elif 7 > saved_movie_score.actor_score:
            analysis["actor"] = "Good choice in actors. To be honest, actors are very important " \
                                "in a movie. And you made it! Great team with great actors!"
        else:
            analysis["actor"] = "**!! What a talent producer here who made such a talent decision! " \
                                "I'm sure your movie will be great in actor list!"

    if 0 != saved_movie_score.actress_score:
        if 5 > saved_movie_score.actress_score:
            analysis["actress"] = "Lovely beauties in actress list. But that may not be enough to make you a success."
        elif 7 > saved_movie_score.actress_score:
            analysis["actress"] = "Wow! What a nice actress group. Being honest, this team can make some difference! " \
                                  "Your film may be even better if you could have more considerations about scenes, " \
                                  "environment, and etc. But it seems very good now."
        else:
            analysis["actress"] = "110 / 100 actress team!"

    if 5 > saved_movie_score.director_score:
        analysis["director"] = "Hum ... Let me check ... The director is relatively new hum? Nice try!"
    elif 7 > saved_movie_score.director_score:
        analysis["director"] = "Good director. I always like him."
    else:
        analysis["director"] = "What!?? You have the best director!!?? Awesome!!!"

    if 5 > saved_movie_score.duration_score:
        analysis["duration"] = "The duration of this film is really ... hum ... interesting."

    return analysis


def get_chart_js_value(saved_aggregate_info, saved_movie_score=None):
    """
    Get json from score to genreate radar chart.
    :param saved_aggregate_info: genreal score information for all movies
    :param saved_movie_score: specific score information for one movie
    :return: json for create radar chart
    """
    if 0 == saved_aggregate_info.number_of_movies:
        temp_score = 0
        temp_actor_score = 0
        temp_actress_score = 0
        temp_director_score = 0
        temp_duration_score = 0
        temp_genre_score = 0
        temp_movie_box = 0
    else:
        temp_score = saved_aggregate_info.score / saved_aggregate_info.number_of_movies
        temp_actor_score = saved_aggregate_info.actor_score / saved_aggregate_info.number_of_movies
        temp_actress_score = saved_aggregate_info.actress_score / saved_aggregate_info.number_of_movies
        temp_director_score = saved_aggregate_info.director_score / saved_aggregate_info.number_of_movies
        temp_duration_score = saved_aggregate_info.duration_score / saved_aggregate_info.number_of_movies
        temp_genre_score = saved_aggregate_info.genre_score / saved_aggregate_info.number_of_movies
        temp_movie_box = saved_aggregate_info.avg_movie_box / saved_aggregate_info.number_of_movies

    if saved_movie_score is None:
        data = {
            'labels': ["genreal Score", "Actor Score", "Actress Score", "Director Score", "Duration",
                       "Genre Score", "Box Office"],
            'datasets': [
                {
                    'label': "Average",
                    'backgroundColor': "rgba(255,99,132,0.2)",
                    'borderColor': "rgba(255,99,132,1)",
                    'pointBackgroundColor': "rgba(255,99,132,1)",
                    'pointBorderColor': "#fff",
                    'pointHoverBackgroundColor': "#fff",
                    'pointHoverBorderColor': "rgba(255,99,132,1)",
                    'data': [str(temp_score),
                             str(temp_actor_score),
                             str(temp_actress_score),
                             str(temp_director_score),
                             str(temp_duration_score),
                             str(temp_genre_score),
                             str(temp_movie_box)]
                }
            ]
        }
    else:
        data = {
            'labels': ["genreal Score", "Actor Score", "Actress Score", "Director Score", "Duration",
                       "Genre Score", "Box Office"],
            'datasets': [
                {
                    'label': str(saved_movie_score.movie.title),
                    'backgroundColor': "rgba(255,99,132,0.2)",
                    'borderColor': "rgba(255,99,132,1)",
                    'pointBackgroundColor': "rgba(255,99,132,1)",
                    'pointBorderColor': "#fff",
                    'pointHoverBackgroundColor': "#fff",
                    'pointHoverBorderColor': "rgba(255,99,132,1)",
                    'data': [str(saved_movie_score.score),
                             str(saved_movie_score.actor_score),
                             str(saved_movie_score.actress_score),
                             str(saved_movie_score.director_score),
                             str(saved_movie_score.duration_score),
                             str(saved_movie_score.genre_score),
                             str(saved_movie_score.avg_movie_box)]
                },
                {
                    'label': "Average",
                    'fbackgroundColor': "rgba(179,181,198,0.2)",
                    'borderColor': "rgba(179,181,198,1)",
                    'pointBackgroundColor': "rgba(179,181,198,1)",
                    'pointBorderColor': "#fff",
                    'pointHoverBackgroundColor': "#fff",
                    'pointHoverBorderColor': "rgba(179,181,198,1)",
                    'data': [str(temp_score),
                             str(temp_actor_score),
                             str(temp_actress_score),
                             str(temp_director_score),
                             str(temp_duration_score),
                             str(temp_genre_score),
                             str(temp_movie_box)]
                }
            ]
        }

    return data


def json_score(saved_movie_score):
    """
    Get JSON format movie score object in order to parse into HTML.
    :param saved_movie_score: Movie score object
    :return: JSON format movie score object
    """
    return {"score": saved_movie_score.score, "actor_score": saved_movie_score.actor_score,
            "actress_score": saved_movie_score.actress_score, "director_score": saved_movie_score.director_score,
            "duration_score": saved_movie_score.duration_score, "genre_score": saved_movie_score.genre_score,
            "avg_movie_box": saved_movie_score.avg_movie_box}


def score_components_maker():
    """
    genreate a explanation for components of a score.
    :return:
    """
    director_percentage, actor_percentage, actress_percentage = get_percentage()

    duration_percentage = 10
    genre_percentage = 5

    score_components = [
        {"percentage": director_percentage,
         "explanation": "Director is the fundamental of a movie. "
                        "If you have a too naive director, the movie may be naive, too.",
         "name": "Director "},
        {"percentage": actor_percentage,
         "explanation": "Actor, and actress are the basic but also the most glorious element in the show. "
                        "You need them to make your show perfect. Here your actor has "
                        + str(actor_percentage) + "% importance in your movie.",
         "name": "Actor "},
        {"percentage": actress_percentage,
         "explanation": "Secrets make a woman woman. Thus an actress make a movie movie.",
         "name": "Actress "},
        {"percentage": duration_percentage,
         "explanation": "Duration usually has less importance in one movie. "
                        "The system has assigned " + str(duration_percentage) + "% importance.",
         "name": "Duration "},
        {"percentage": genre_percentage,
         "explanation": "Like duration, different audiences have different favorites, "
                        "which leads this section only stands for " + str(genre_percentage) + "%.",
         "name": "Genre "},
    ]

    return score_components


def get_percentage():
    """
    A simple percentage generator.
    :return: 3 random percentage making .85
    """
    total = 85
    part1 = random.randrange(15, 35)
    total -= part1
    part2 = random.randrange(15, 35)
    total -= part2
    return total, part2, part1


def get_num_of_movies_list():
    """
    Get comparison chart data.
    :return: comparison chart data
    """
    movie_scores = MovieScore.objects.all()
    length_of_list = range(10)
    num_of_movies_list = [0 for i in length_of_list]
    director_score_list = [0 for i in length_of_list]
    director_num_movie_list = [0 for i in length_of_list]
    actor_score_list = [0 for i in length_of_list]
    actor_num_movie_list = [0 for i in length_of_list]
    actress_score_list = [0 for i in length_of_list]
    actress_num_movie_list = [0 for i in length_of_list]

    for movie_score in movie_scores:
        # be careful
        # num_of_movies_list is the number of movies in each interval
        # which is different from others
        score_location = get_location_of_score(movie_score.score)
        num_of_movies_list[score_location] += 1

        # be careful
        # avg_director_score_list is average score in each interval
        # which is different from num_of_movies_list
        director_score_location = get_location_of_score(movie_score.director_score)
        director_score_list[director_score_location] += movie_score.director_score
        director_num_movie_list[director_score_location] += 1

        # be careful
        # avg_director_score_list is average score in each interval
        # which is different from num_of_movies_list
        actor_score_location = get_location_of_score(movie_score.actor_score)
        actor_score_list[actor_score_location] += movie_score.actor_score
        actor_num_movie_list[actor_score_location] += 1

        # be careful
        # avg_director_score_list is average score in each interval
        # which is different from num_of_movies_list
        actress_score_location = get_location_of_score(movie_score.actress_score)
        actress_score_list[actress_score_location] += movie_score.actress_score
        actress_num_movie_list[actress_score_location] += 1

    print(director_score_list)

    avg_director_score_list = get_average(director_score_list, director_num_movie_list)
    avg_actor_score_list = get_average(actor_score_list, actor_num_movie_list)
    avg_actress_score_list = get_average(actress_score_list, actress_num_movie_list)

    return num_of_movies_list, avg_director_score_list, avg_actor_score_list, avg_actress_score_list


def get_location_of_score(score):
    """
    Given a score, return the proper position. E.g. 1.5 -> 0, 3.8 -> 2
    :param score:
    :return:
    """
    return int(math.floor(score) - 1)


def get_average(num_list, frequency_list):
    """
    Given a list of total, return the average.
    :param num_list: score list (in total)
    :param frequency_list: number of items
    :return: the average list
    """
    result = []
    repeat_range = range(len(num_list))

    for i in repeat_range:
        if 0 != frequency_list[i]:
            result.append(float(num_list[i] / frequency_list[i]))
        else:
            result.append(0)

    return result


def get_directors_actors():
    """
    Get information of directors and actors.
    :return: 2 arrays and one of which is director list and the other one is actor list
    """
    people = Person.objects.all()
    directors = []
    actors = []

    for person in people:
        if person.type_is_director:
            directors.append(person.name)
        else:
            actors.append(person.name)

    return directors, actors
