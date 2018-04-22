#!/usr/bin/python3


from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import math
import qrcode

import argparse



def params_sanity(result):
    if(result.date == None):
        if(result.time != None):
            raise RuntimeError("Cannot have time without date")
    if(result.photo != None):
        try:
            Image.open(result.photo)
        except IOError:
            raise RuntimeError("Featured photo not found")

    if(result.name == None):
        raise RuntimeError("No event name specified")
    if(result.desc == None):
        raise RuntimeError("No event description specified")


        

def display_args(result):
    print("Name: " + str(result.name))
    print("Description: " + str(result.desc))
    if(result.date != None):
        if(result.time != None):
            print("Date and Time: " + str(result.date) + str(result.time))
        else:
            print("Date: " + str(result.date))

def make_blank_page():
    page = Image.new("RGB", (3300, 2550), 0xFFFFFFFF)
    return page


# wraps words in a bounding box. basic.
def draw_multiline(drawer, bounding_box, font, text):
    yprogress = 0
    lineheight = font.getsize(text.split("\n")[0])[1]
    for lineOfText in text.split("\n"):
        line = ""
        for word in lineOfText.split(" "):
            newline = ""
            if(line == ""):
                line = word
                newline = word
            else:
                newline = line + " " + word
            if(font.getsize(newline)[0] > bounding_box[2] - bounding_box[0]):
                drawer.text((bounding_box[0], bounding_box[1] + yprogress), line, (0,0,0,255), font=font)
                yprogress += lineheight
                line = word
            else:
                line = newline
        drawer.text((bounding_box[0], bounding_box[1] + yprogress), line, (0,0,0,255), font=font)
        yprogress += lineheight
   

def build_logistics(when, where):
    output = "When: " + str(when)
    output += " \n"
    output += "Where: " + str(where)
    return output

def template1(background, results):
    featuredImage = Image.open(results.photo)
    print(featuredImage.size)
    # We want the featured image to be 1/5 of the size of background page
    finalSize = (math.floor(background.size[0] / math.sqrt(4)), math.floor(background.size[1] / math.sqrt(4)))
    ratio = min(finalSize[0]/(featuredImage.size[0]), finalSize[1]/(featuredImage.size[1]))
    print("Ratio: " + str(ratio))
    if(ratio > 1):
        print("You might want to find a larger image! Preferably one that is at least " + str(finalSize[0]) + "x" + str(finalSize[1]) + "(WxL)")
    resizeSize = (math.floor(ratio * featuredImage.size[0]), math.floor(ratio * featuredImage.size[1]))
    featuredImage = featuredImage.resize(resizeSize, Image.ANTIALIAS)

    pageMargin = 75
    internalMargin = 50
    
    bottomMargin = background.size[1] - pageMargin
    topMargin = pageMargin
    rightMargin = background.size[0] - pageMargin
    leftMargin = pageMargin
    sideOfFeaturedImage = featuredImage.size[0] + pageMargin
    topOfFeaturedImage = bottomMargin - pageMargin - featuredImage.size[1]
    background.paste(featuredImage, (pageMargin, topOfFeaturedImage))
    
    # create qr codes


    # set up text drawing 
    draw = ImageDraw.Draw(background)
    titlefont = ImageFont.truetype("keep-calm.ttf", 300)
    smallfont = ImageFont.truetype("keep-calm.ttf", 150)
    reallysmallfont = ImageFont.truetype("keep-calm.ttf", 75)

    # Title must be one line
    draw.text((75,75), results.name, (0,0,0,255), font=titlefont)
    
    # LUG Promo
    topOfLUGPromo = bottomMargin - (reallysmallfont.getsize("LUG")[1] * 3)
    draw_multiline(draw, (sideOfFeaturedImage + internalMargin, topOfLUGPromo, rightMargin, bottomMargin), reallysmallfont, "Brought to you by the Linux Users' Group")

    # Draw event description
    draw_multiline(draw, (pageMargin, titlefont.getsize(results.name)[1] + internalMargin + pageMargin + pageMargin, math.floor(background.size[0] * 0.75), topOfFeaturedImage - internalMargin), smallfont, results.desc)
    
    # Draw 

    # Draw event time, date, and/or location
    if(results.date != None):
        dateAndTime = build_logistics(results.date, results.location)
        if(results.time != None):
            dateAndTime = build_logistics(results.date + ", " + results.time, results.location)
        draw_multiline(draw, (sideOfFeaturedImage + internalMargin, topOfFeaturedImage, rightMargin, bottomMargin), smallfont, dateAndTime)
    
    background.save("output.jpg")

parser = argparse.ArgumentParser(description="Creates a poster for a LUG event")

# Add necessary command line args
parser.add_argument("-n", "--name", action="store", help="name of event")
parser.add_argument("--desc", help="short description of event")
parser.add_argument("-d", "--date", help="date of event", required=True)
parser.add_argument("-t", "--time", help="time of event", required=True)
parser.add_argument("-l", "--location", help="location of event", required=True)
parser.add_argument("--photo", help="featured image for event", required=False)
parser.add_argument("--facebook", help="facebook event page link", required=False)
parser.add_argument("--gcal", help="instant add google calendar link", required=False)
parser.add_argument("--website", help="more info website")

result = parser.parse_args()

params_sanity(result)
print("We received...")
display_args(result)

print("Is this correct? [yY/nN]")
response = input("")
if(response in ["y", "Y"]):
    print("hooray!")
    template1(make_blank_page(), result)

else:
    print("rip :(")




