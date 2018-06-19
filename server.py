from flask import Flask
from flask import request
from flask import make_response
from flask import jsonify
from flask import send_from_directory
import hashlib
import os
from fpdf import FPDF

import main

def none_if_empty(a_request, key):
    if(key in a_request.args):
        return a_request.args[key]
    else:
        return None

# TODO: not scalable, should iterate through list of params that should not be None.
def params_check(name, date, desc, location, photo):
    if((name != None and date != None and desc != None and location != None and photo != None) != True):
        return False
    else:
        return True

app = Flask(__name__)

@app.route("/generate", methods=["POST"])
def generate():
    errors = {}
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
    # buildPoster creates a high-res JPG. We want it to be in pdf for delivery
    errors["param_error"] = params_check(name, date, desc, location, photo)
    if(errors["param_error"]):
        return jsonify(errors)

    poster_errors = main.buildPoster(name, desc, date, time, location, photo, facebook, gcal, website, pizza)
    errors.update(poster_errors)
    eventhash = hashlib.md5(str(name + date + time + location + photo + gcal + website + facebook).encode()).hexdigest()
    pdf = FPDF('L', 'in', 'Letter')
    pdf.add_page()
    pdf.set_margins(0,0,0)
    pdf.image("output.jpg", 0, 0, 11)
    pdf.output("output.pdf", "F")
    os.rename("output.pdf", str(eventhash) + ".pdf")
    return jsonify(
        errors,
        hash=eventhash
    )


@app.route("/result/<string:eventhash>", methods=["GET"])
def returnPoster(eventhash):
    print(eventhash)
    if(os.path.isfile(str(eventhash) + ".pdf")):
        print(os.getcwd() + "/" + str(eventhash) + ".pdf")
        return send_from_directory(os.getcwd(), str(eventhash) + ".pdf")
    else:
        return "none"


print(app.url_map)