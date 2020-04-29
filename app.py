from flask import Flask, request, jsonify, make_response, abort
from werkzeug.exceptions import HTTPException

from db import db

app = Flask(__name__)


@app.errorhandler(HTTPException)
def err_handler(error):
    return make_response(jsonify({'status': error.code,
                                  'reason': error.description}), error.code)


def validate_post(err_code):
    if not request.json:
        abort(err_code, "Fields is required")
    if 'movie' not in request.json:
        abort(err_code, "Field 'movie' is required")

    for i in ['title', 'year', 'director', 'length', 'rating']:
        if i not in request.json['movie']:
            abort(err_code, "Field '" + i + "' is required")


def gen_return(movie):
    return {"movie": {
        "id": movie.id,
        "title": movie.title,
        "year": movie.year,
        "director": movie.director,
        "length": movie.length,
        "rating": movie.rating
    }}


def get_movies():
    ret = {"list": []}
    for movies in db.session.query(db.Movies):
        ret["list"].append(gen_return(movies)['movie'])
    return jsonify(ret)


def post_movies():
    validate_post(500)
    json_inp = request.json['movie']
    try:
        movie = db.Movies(json_inp['title'], json_inp['year'],
                          json_inp['director'], json_inp['length'],
                          json_inp['rating'])  # TODO: А разве надо использовать id от клиенета
    except AssertionError as e:
        abort(400, e.args[0])
    else:
        db.session.add(movie)
        db.session.commit()
        return jsonify(gen_return(movie))


def get_one_movies(movies_id):
    movie = db.session.query(db.Movies).get(movies_id)
    if movie is None:
        abort(404, "Movie not found")
    return jsonify(gen_return(movie))


def patch_movie(movies_id):
    validate_post(400) # Код нужен потому, что в задание они указаны разные
    movie = db.session.query(db.Movies).get(movies_id)
    if movie is None:
        abort(404, "Movie not found")
    json_inp = request.json['movie']

    try:
        movie.title = json_inp['title']
        movie.year = json_inp['year']
        movie.director = json_inp['director']
        movie.length = json_inp['length']
        movie.rating = json_inp['rating']
    except AssertionError as e:
        abort(400, e.args[0])
    else:
        db.session.commit()
        return jsonify(gen_return(movie))


def delete_movie(movies_id):
    movie = db.session.query(db.Movies).get(movies_id)
    if movie is None:
        abort(404, "Movie not found")
    db.session.delete(movie)
    db.session.commit()
    return make_response(jsonify("Accepted"), 202)


@app.route('/api/movies', methods=["GET", "POST"])
def api_movies():
    if request.method == "GET":
        return get_movies()
    elif request.method == "POST":
        return post_movies()


@app.route('/api/movies/<int:movies_id>', methods=["GET", "PATCH", "DELETE"])
def api_movies_ids(movies_id):
    if request.method == "GET":
        return get_one_movies(movies_id)
    elif request.method == "PATCH":
        return patch_movie(movies_id)
    elif request.method == "DELETE":
        return delete_movie(movies_id)


if __name__ == '__main__':
    app.run()
