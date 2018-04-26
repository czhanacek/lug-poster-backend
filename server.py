from flask import Flask
from flask import request
from flask import make_response
from flask import jsonify


import main

def none_if_empty(a_request, key):
    if(key in a_request.args):
        return a_request.args[key]
    else:
        return None

app = Flask(__name__)

@app.route("/generate", methods=["POST"])
def generate():
    name = none_if_empty(request, "name")
    
    date = none_if_empty(request, "date")
    desc = none_if_empty(request, "desc")
    time = none_if_empty(request, "time")
    location = none_if_empty(request, "location")
    photo = none_if_empty(request, "photo_url")
    facebook = none_if_empty(request, "facebook")
    gcal = none_if_empty(request, "gcal")
    website = none_if_empty(request, "website")
    pizza = bool(none_if_empty(request, "pizza"))
    main.buildPoster(name, desc, date, time, location, photo, facebook, gcal, website, pizza)
    print("WE RECEIVED: " + str(name))
    return app.send_static_file("output.jpg")