#!/usr/bin/python3
""" Module containing Place View """
from api.v1.views import app_views
from flask import jsonify, abort, request
from models import storage, storage_t
from models.place import Place


@app_views.route('/cities/<string:city_id>/places', methods=['GET'],
                 strict_slashes=False)
def get_places(city_id):
    """ Retrieves the list of all Place objects of a City.
        Args:
            city_id (str): The UUID4 string representing a City object.
        Returns:
            List of dictionaries representing Place objects in JSON format.
            Raise 404 error if `city_id` is not linked to any City object.
    """
    city_obj = storage.get("City", city_id)
    if city_obj is None:
        abort(404)
    places = [place.to_dict() for place in city_obj.places]
    return jsonify(places)


@app_views.route('/places/<string:place_id>', methods=['GET'],
                 strict_slashes=False)
def get_place(place_id):
    """ Retrieves a Place object based on `place_id`.
    Args:
        place_id (str): The UUID4 string representing a Place object.
    Returns:
        Dictionary represention of a Place object in JSON format.
        Raise 404 error if `place_id` is not linked to any Place object.
    """
    place_obj = storage.get("Place", place_id)
    if place_obj is None:
        abort(404)
    return jsonify(place_obj.to_dict())


@app_views.route('/places/<string:place_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_place(place_id):
    """ Deletes a Place object based on `place_id`.
    Args:
        place_id (str): The UUID4 string representing a Place object.
    Returns:
        Returns an empty dictionary with the status code 200.
        Raise 404 error if `place_id` is not linked to any Place object.
    """
    place_obj = storage.get("Place", place_id)
    if place_obj is None:
        abort(404)
    place_obj.delete()
    storage.save()
    return jsonify({})


@app_views.route('/cities/<string:city_id>/places', methods=['POST'],
                 strict_slashes=False)
def add_place(city_id):
    """ Creates a Place object using `city_id` and HTTP body request fields.
    Args:
        city_id (str): The UUID4 string representing a City object.
    Returns:
        Returns the new Place object as a  dictionary in JSON format
        with the status code 200.
        Raise 404 error if `state_id` is not linked to any State object.
    """
    city_obj = storage.get("City", city_id)
    if city_obj is None:
        abort(404)
    if request.json is None:
        return "Not a JSON", 400
    fields = request.get_json()
    if fields.get('user_id') is None:
        return "Missing user_id", 400
    user_obj = storage.get("User", fields['user_id'])
    if user_obj is None:
        abort(404)
    if fields.get('name') is None:
        return "Missing name", 400
    fields['city_id'] = city_id
    new_place = Place(**fields)
    new_place.save()
    return jsonify(new_place.to_dict()), 201


@app_views.route('/places/<string:place_id>', methods=['PUT'],
                 strict_slashes=False)
def edit_place(place_id):
    """ Edit a Place object using `place_id` and HTTP body request fields.
    Args:
        place_id (str): The UUID4 string representing a Place object.
    Returns:
        Returns the Place object as a  dictionary in JSON format with the
        status code 200.
        Raise 404 error if `place_id` is not linked to any Place object.
    """
    place_obj = storage.get("Place", place_id)
    if place_obj is None:
        abort(404)
    if request.json is None:
        return "Not a JSON", 400
    fields = request.get_json()
    for key in fields:
        if key not in ['id', 'user_id', 'city_id', 'created_at', 'update_at']:
            if hasattr(place_obj, key):
                setattr(place_obj, key, fields[key])
    place_obj.save()
    return jsonify(place_obj.to_dict()), 200


@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
def filter_places():
    """ Filter Places based on optional JSON keys passed through HTTP body
        request.
    Returns:
        List of dictionaries representing Place objects.
        400 error if JSON was not passed.
    """
    if request.json is None:
        return "Not a JSON", 400
    fields = request.get_json()
    states = fields.get('states', [])
    cities = fields.get('cities', [])
    amenities = fields.get('amenities', [])
    places = set()
    if fields == {} or (states == [] and cities == []):
        places = set(storage.all("Place").values())
    for state_id in states:
        state = storage.get('State', state_id)
        if state is not None:
            for city in state.cities:
                for place in city.places:
                    places.add(place)
    for city_id in cities:
        city = storage.get('City', city_id)
        if city is not None:
            for place in city.places:
                places.add(place)
    if amenities != []:
        amenities = set(amenities)
        temp = set()
        for amenity_id in amenities:
            if storage.get("Amenity", amenity_id) is not None:
                temp.add(amenity_id)
        amenities = temp
        to_remove = set()
        for place in places:
            if storage_t == 'db':
                amenities_id = {amenity.id for amenity in place.amenities}
            else:
                amenities_id = set(place.amenity_ids)
            if not set(amenities).issubset(amenities_id):
                to_remove.add(place)
            del place.amenities
        places -= to_remove
    return jsonify([place.to_dict() for place in places])

# #!/usr/bin/python3
# """ Places routes handler """
# from api.v1.views import app_views
# from flask import jsonify, abort, request
# from models import storage
# from models.city import City
# from models.place import Place
# from models.user import User
# from models.state import State
# from api.v1.views.cities import get_all
# from api.v1.views.places_amenities import do_get_amenities
# import json


# def check(cls, place_id):
#     """
#         If the place_id is not linked to any Place object, raise a 404 error
#     """
#     try:
#         get_place = storage.get(cls, place_id)
#         get_place.to_dict()
#     except Exception:
#         abort(404)
#     return get_place


# def get_places(city_id, place_id):
#     """
#        Retrieves the list of all Place objects
#        if place_id is not none get a Place object
#     """
#     if (place_id is not None):
#         get_place = check(Place, place_id).to_dict()
#         return jsonify(get_place)
#     my_city = storage.get(City, city_id)
#     try:
#         all_places = my_city.places
#     except Exception:
#         abort(404)
#     places = []
#     for c in all_places:
#         places.append(c.to_dict())
#     return jsonify(places)


# def delete_place(place_id):
#     """
#         Deletes a Place object
#         Return: an empty dictionary with the status code 200
#     """
#     get_place = check(Place, place_id)
#     storage.delete(get_place)
#     storage.save()
#     response = {}
#     return jsonify(response)


# def create_place(request, city_id):
#     """
#         Creates a place object
#         Return: new place object
#     """
#     check(City, city_id)
#     body_request = request.get_json()
#     if (body_request is None):
#         abort(400, 'Not a JSON')
#     try:
#         user_id = body_request['user_id']
#     except KeyError:
#         abort(400, 'Missing user_id')
#     check(User, user_id)
#     try:
#         place_name = body_request['name']
#     except KeyError:
#         abort(400, 'Missing name')
#     new_place = Place(name=place_name, city_id=city_id, user_id=user_id)
#     storage.new(new_place)
#     storage.save()
#     return jsonify(new_place.to_dict())


# def update_place(place_id, request):
#     """
#         Updates a Place object
#     """
#     get_place = check(Place, place_id)
#     body_request = request.get_json()
#     if (body_request is None):
#         abort(400, 'Not a JSON')
#     for k, v in body_request.items():
#         if (k not in ('id', 'created_at', 'updated_at')):
#             setattr(get_place, k, v)
#     storage.save()
#     return jsonify(get_place.to_dict())


# def search(request):
#     """
#     retrieves all Place objects depending of the JSON
#     in the body of the request
#     """
#     body_request = request.get_json()
#     if body_request is None:
#         abort(400, 'Not a JSON')
#     places_list = []
#     places_amenity_list = []
#     place_amenities = []
#     all_cities = []
#     states = body_request.get('states')
#     cities = body_request.get('cities')
#     amenities = body_request.get('amenities')
#     if len(body_request) == 0 or (states is None and cities is None):
#         places = storage.all(Place)
#         for p in places.values():
#             places_list.append(p.to_dict())
#     if states is not None and len(states) is not 0:
#         for id in states:
#             get_cities = get_all(id, None).json
#             for city in get_cities:
#                 all_cities.append(city.get('id'))
#         for id in all_cities:
#             places = do_get_places(id, None)
#             for p in places.json:
#                 places_list.append(p)
#     if cities is not None and len(cities) is not 0:
#         for id in cities:
#             places = do_get_places(id, None)
#             for p in places.json:
#                 places_list.append(p)
#     if amenities is not None and len(amenities) is not 0:
#         for p in places_list:
#             place_id = p.get('id')
#             get_amenities = storage.get(Place, place_id)
#             amenity_id = get_amenities.amenities
#             for a in amenity_id:
#                 place_amenities.append(a.id)
#                 if (a.id in amenities):
#                     places_amenity_list.append(p)
#             place_amenities = []
#         return jsonify(places_amenity_list)

#     return jsonify(places_list)


# @app_views.route('/cities/<city_id>/places/', methods=['GET', 'POST'],
#                  defaults={'place_id': None}, strict_slashes=False)
# @app_views.route('/places/<place_id>', defaults={'city_id': None},
#                  methods=['GET', 'DELETE', 'PUT'])
# def places(city_id, place_id):
#     """
#         Handle places requests with needed functions
#     """
#     if (request.method == "GET"):
#         return get_places(city_id, place_id)
#     elif (request.method == "DELETE"):
#         return delete_place(place_id)
#     elif (request.method == "POST"):
#         return create_place(request, city_id), 201
#     elif (request.method == "PUT"):
#         return update_place(place_id, request), 200


# @app_views.route('/places_search', methods=['POST'],
#                  strict_slashes=False)
# def places_search():
#     """
#     retrieves all Place objects depending of the JSON
#     in the body of the request
#     """
#     return search(request)

