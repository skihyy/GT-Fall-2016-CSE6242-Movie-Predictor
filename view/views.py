from django.shortcuts import render
from view.models import *
import random
import math
import moviescorepredictorml


# Create your views here.
def add(request):
    """
    Go to add a movie page.
    :param request: http request
    :return: web page of adding a movie
    """
    genre = Genre.objects.all()
    director_names, actor_names, director_data, actor_data = get_directors_actors()
    return render(request,
                  'input.html',
                  {'genres': genre,
                   'directors': director_data,
                   'director_autocomplete': director_names,
                   'actors': actor_data,
                   'actors_autocomplete': actor_names})


def show(request):
    """
    Handling the new movie information and generate result page.
    :param request: http request
    :return: web page of result
    """
    genre_selected = Genre.objects.get(id=request.POST["genre"])
    leading_actor_name = request.POST["actor1"]
    support_actor_name = request.POST["actor2"]
    director_name = request.POST["director"]

    # find data in database
    leading_actor_list = Person.objects.filter(name=leading_actor_name)
    if 0 == len(leading_actor_list):
        leading_actor = Person(name=leading_actor_name, type_is_director=False,
                               average_score=0, num_of_movies=0)
        leading_actor.save()
        # this will have id information
        leading_actor = Person.objects.last()
    else:
        leading_actor = leading_actor_list[0]

    # find data in database
    support_actor_list = Person.objects.filter(name=support_actor_name)
    if 0 == len(support_actor_list):
        support_actor = Person(name=leading_actor_name, type_is_director=False,
                               average_score=0, num_of_movies=0)
        support_actor.save()
        # this will have id information
        support_actor = Person.objects.last()
    else:
        support_actor = support_actor_list[0]

    # find data in database
    director_list = Person.objects.filter(name=director_name, type_is_director=True)
    if 0 == len(director_list):
        director = Person(name=director_name, type_is_director=True,
                          average_score=0, num_of_movies=0)
        director.save()
        # this will have id information
        director = Person.objects.last()
    else:
        director = director_list[0]

    # compute the score
    # actor, director, genre
    first_set_score = moviescorepredictorml.movie_score(str(leading_actor.name),
                                                        str(director.name),
                                                        str(genre_selected.genre))
    second_set_score = moviescorepredictorml.movie_score(str(support_actor.name),
                                                         str(director.name),
                                                         str(genre_selected.genre))

    # save this movie
    movie_info = MovieInfo(title=request.POST["title"],
                           genre=genre_selected,
                           first_actor_id=leading_actor.id,
                           second_actor_id=support_actor.id,
                           director_id=director.id)
    movie_info.save()
    saved_movie_info = MovieInfo.objects.last()

    # for general use
    saved_movie_score, saved_aggregate_info = compute_score(saved_movie_info, leading_actor, support_actor, director,
                                                            first_set_score, second_set_score)
    # for radar chart and analysis
    chart_js_data = get_chart_js_value(saved_aggregate_info, saved_movie_score)
    # for radar chart analysis
    general_analysis = create_general_analysis(saved_movie_score)
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


def compute_score(saved_movie_info, leading_actor, support_actor, director,
                  first_set_score, second_set_score):
    """
    A method used to compute the score of a movie.
    Currently, it used a random number genreator for predicting movie score.
    But later this should be fixed by using a real learner.
    :param saved_movie_info: A movie information object
    :param actor_list: A list of person objects for actors / actresses
    :param director: A person object for director
    :return: A movie score object contains all score of it and the aggregate score information
    """
    # movie score
    score = (float(first_set_score["score"]) + float(second_set_score["score"])) / 2
    first_actor_genre_score = float(first_set_score["actor-genre"])
    second_actor_genre_score = float(second_set_score["actor-genre"])
    first_actor_director_score = float(first_set_score["actor-director"])
    second_actor_director_score = float(second_set_score["actor-director"])
    director_genre_score = float(first_set_score["score"])
    first_actor_score = (first_actor_genre_score + first_actor_director_score) / 2
    second_actor_score = (second_actor_genre_score + second_actor_director_score) / 2
    genre_score = (first_actor_genre_score + second_actor_genre_score) / 2
    director_score = score

    # update data
    leading_actor.average_score = (float(leading_actor.average_score) * leading_actor.num_of_movies
                                   + first_actor_score) / (1 + leading_actor.num_of_movies)
    leading_actor.num_of_movies += 1
    leading_actor.save()

    print(support_actor.average_score)
    support_actor.average_score = (float(support_actor.average_score) * support_actor.num_of_movies
                                   + second_actor_score) / (1 + support_actor.num_of_movies)
    support_actor.num_of_movies += 1
    support_actor.save()

    movie_score = MovieScore(movie=saved_movie_info,
                             score=score,
                             first_actor_genre_score=first_actor_genre_score,
                             second_actor_genre_score=second_actor_genre_score,
                             first_actor_director_score=first_actor_director_score,
                             second_actor_director_score=second_actor_director_score,
                             director_genre_score=director_genre_score,
                             first_actor_score=first_actor_score,
                             second_actor_score=second_actor_score,
                             genre_score=genre_score,
                             director_score=director_score)
    # save to database
    movie_score.save()
    # get from database object since it has strict format requirement
    saved_movie_score = MovieScore.objects.last()

    aggregate_score_object = AggregateInfo.objects.get(id=1)

    # update information
    aggregate_score_object.number_of_movies += 1
    aggregate_score_object.score += saved_movie_score.score
    aggregate_score_object.first_actor_genre_score += saved_movie_score.first_actor_genre_score
    aggregate_score_object.second_actor_genre_score += saved_movie_score.second_actor_genre_score
    aggregate_score_object.first_actor_director_score += saved_movie_score.first_actor_director_score
    aggregate_score_object.second_actor_director_score += saved_movie_score.second_actor_director_score
    aggregate_score_object.director_genre_score += saved_movie_score.director_genre_score
    aggregate_score_object.first_actor_score += saved_movie_score.first_actor_score
    aggregate_score_object.second_actor_score += saved_movie_score.second_actor_score
    aggregate_score_object.genre_score += saved_movie_score.genre_score
    aggregate_score_object.director_score += saved_movie_score.director_score
    # update database
    aggregate_score_object.save()

    saved_aggregate_info = AggregateInfo.objects.get(id=1)

    return saved_movie_score, saved_aggregate_info


def create_general_analysis(saved_movie_score):
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

    if 5 > saved_movie_score.first_actor_score:
        analysis["actor"] = "Maybe you could have other actors here. " \
                            "They may have different experiences which may help you be even " \
                            "more successful in this movie!"
    elif 7 > saved_movie_score.first_actor_score:
        analysis["actor"] = "Good choice in actors. To be honest, actors are very important " \
                            "in a movie. And you made it! Great team with great actors!"
    else:
        analysis["actor"] = "**!! What a talent producer here who made such a talent decision! " \
                            "I'm sure your movie will be great in actor list!"

    if 5 > saved_movie_score.second_actor_score:
        analysis["actress"] = "Lovely beauties in actress list. But that may not be enough to make you a success."
    elif 7 > saved_movie_score.second_actor_score:
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

    return analysis


def get_chart_js_value(saved_aggregate_info, saved_movie_score):
    """
    Get json from score to genreate radar chart.
    :param saved_aggregate_info: genreal score information for all movies
    :param saved_movie_score: specific score information for one movie
    :return: json for create radar chart
    """
    # score of correlation set
    temp_first_actor_genre_score = saved_aggregate_info.first_actor_genre_score / saved_aggregate_info.number_of_movies
    temp_second_actor_genre_score = saved_aggregate_info.second_actor_genre_score / saved_aggregate_info.number_of_movies
    temp_first_actor_director_score = saved_aggregate_info.first_actor_director_score / saved_aggregate_info.number_of_movies
    temp_second_actor_director_score = saved_aggregate_info.second_actor_director_score / saved_aggregate_info.number_of_movies
    temp_director_genre_score = saved_aggregate_info.director_genre_score / saved_aggregate_info.number_of_movies

    correlation_data = generate_chart_js_data(str(saved_movie_score.movie.title),
                                              "Leading Actor - Genre",
                                              "Support Actor - Genre",
                                              "Leading Actor - Director",
                                              "Support Actor - Director",
                                              "Director - Genre",
                                              temp_first_actor_genre_score,
                                              temp_second_actor_genre_score,
                                              temp_first_actor_director_score,
                                              temp_second_actor_director_score,
                                              temp_director_genre_score,
                                              saved_movie_score.first_actor_genre_score,
                                              saved_movie_score.second_actor_genre_score,
                                              saved_movie_score.first_actor_director_score,
                                              saved_movie_score.second_actor_director_score,
                                              saved_movie_score.director_genre_score)

    # score of cast set
    temp_score = saved_aggregate_info.score / saved_aggregate_info.number_of_movies
    temp_first_actor_score = saved_aggregate_info.first_actor_score / saved_aggregate_info.number_of_movies
    temp_second_actor_score = saved_aggregate_info.second_actor_score / saved_aggregate_info.number_of_movies
    temp_director_score = saved_aggregate_info.director_score / saved_aggregate_info.number_of_movies
    temp_genre_score = saved_aggregate_info.genre_score / saved_aggregate_info.number_of_movies

    cast_data = generate_chart_js_data(str(saved_movie_score.movie.title),
                                       "General Score",
                                       "Leading Actor",
                                       "Support Actor",
                                       "Director",
                                       "Genre",
                                       temp_score,
                                       temp_first_actor_score,
                                       temp_second_actor_score,
                                       temp_director_score,
                                       temp_genre_score,
                                       saved_movie_score.score,
                                       saved_movie_score.first_actor_score,
                                       saved_movie_score.second_actor_score,
                                       saved_movie_score.director_score,
                                       saved_movie_score.genre_score)

    score_value = json_score(saved_movie_score)

    return [
        {"id": "myChart1", "data_set": cast_data, "analysis": score_value["castScore"]},
        {"id": "myChart2", "data_set": correlation_data, "analysis": score_value["correlation"]}
    ]


def generate_chart_js_data(title, name1, name2, name3, name4, name5, val1, val2, val3, val4, val5,
                           val6, val7, val8, val9, val10):
    data = {
        'labels': [name1, name2, name3, name4, name5],
        'datasets': [
            {
                'label': title,
                'backgroundColor': "rgba(255,99,132,0.2)",
                'borderColor': "rgba(255,99,132,1)",
                'pointBackgroundColor': "rgba(255,99,132,1)",
                'pointBorderColor': "#fff",
                'pointHoverBackgroundColor': "#fff",
                'pointHoverBorderColor': "rgba(255,99,132,1)",
                'data': [str(val6),
                         str(val7),
                         str(val8),
                         str(val9),
                         str(val10)]
            },
            {
                'label': "Average",
                'fbackgroundColor': "rgba(179,181,198,0.2)",
                'borderColor': "rgba(179,181,198,1)",
                'pointBackgroundColor': "rgba(179,181,198,1)",
                'pointBorderColor': "#fff",
                'pointHoverBackgroundColor': "#fff",
                'pointHoverBorderColor': "rgba(179,181,198,1)",
                'data': [str(val1),
                         str(val2),
                         str(val3),
                         str(val4),
                         str(val5)]
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
    return {
        "castScore": [
            "General Score: " + str(saved_movie_score.score),
            "Leading Actor: " + str(saved_movie_score.first_actor_score),
            "Support Actor: " + str(saved_movie_score.second_actor_score),
            "Director: " + str(saved_movie_score.director_score),
            "Genre: " + str(saved_movie_score.genre_score)
        ],
        "correlation": [
            "Leading Actor - Genre: " + str(saved_movie_score.first_actor_genre_score),
            "Support Actor - Genre" + str(saved_movie_score.second_actor_genre_score),
            "Leading Actor - Director: " + str(saved_movie_score.first_actor_director_score),
            "Support Actor - Director: " + str(saved_movie_score.second_actor_director_score),
            "Director - Genre: " + str(saved_movie_score.director_genre_score)
        ]
    }


def score_components_maker():
    """
    genreate a explanation for components of a score.
    :return:
    """
    director_percentage, actor_percentage, actress_percentage = get_percentage()

    genre_percentage = 15

    score_components = [
        {"percentage": director_percentage,
         "explanation": "Director is the fundamental of a movie. "
                        "If you have a too naive director, the movie may be naive, too.",
         "name": "Director "},
        {"percentage": actor_percentage,
         "explanation": "Leading actor, and actress are the basic but also the most glorious element in the show. "
                        "You need them to make your show perfect. Here your leading actor has "
                        + str(actor_percentage) + "% importance in your movie.",
         "name": "Leading Actor "},
        {"percentage": actress_percentage,
         "explanation": "Secrets make a woman woman. But a support actor also makes a movie movie.",
         "name": "Support Actor "},
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
    # 0 and 10 is the highest / lowest score
    length_of_list = range(10)
    num_of_movies_list = [0 for i in length_of_list]
    director_score_list = [0 for i in length_of_list]
    director_num_movie_list = [0 for i in length_of_list]
    first_actor_score_list = [0 for i in length_of_list]
    actor_num_movie_list = [0 for i in length_of_list]
    second_actor_score_list = [0 for i in length_of_list]
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
        first_actor_score_location = get_location_of_score(movie_score.first_actor_score)
        first_actor_score_list[first_actor_score_location] += movie_score.first_actor_score
        actor_num_movie_list[first_actor_score_location] += 1

        # be careful
        # avg_director_score_list is average score in each interval
        # which is different from num_of_movies_list
        second_actor_score_location = get_location_of_score(movie_score.second_actor_score)
        second_actor_score_list[second_actor_score_location] += movie_score.second_actor_score
        actress_num_movie_list[second_actor_score_location] += 1

    print(director_score_list)

    avg_director_score_list = get_average(director_score_list, director_num_movie_list)
    avg_first_actor_score_list = get_average(first_actor_score_list, actor_num_movie_list)
    avg_second_actor_score_list = get_average(second_actor_score_list, actress_num_movie_list)

    return num_of_movies_list, avg_director_score_list, avg_first_actor_score_list, avg_second_actor_score_list


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
    director_names = []
    directors = []
    actor_names = []
    actors = []

    for person in people:
        if 500 < len(director_names) and 500 < len(actor_names):
            break
        if person.type_is_director:
            if 50 > len(directors):
                directors.append(str(person.name))
            director_names.append(str(person.name))
        else:
            if 50 > len(actors):
                actors.append(str(person.name))
            actor_names.append(str(person.name))

    return director_names, actor_names, directors, actors
