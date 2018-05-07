#!/usr/bin/python3


from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import urllib.request
import math
import qrcode
from argparse import Namespace

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
def draw_multiline(drawer, bounding_box, fontname, text, numlines=10000):
    yprogress = 0
    size = 300
    font = ImageFont.truetype(fontname, size)
    lineheight = font.getsize(text.split("\n")[0])[1]
    
    lines = []
    
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
                #drawer.text((bounding_box[0], bounding_box[1] + yprogress), line, (0,0,0,255), font=font)
                lines.append(line)
                yprogress += lineheight
                line = word
            else:
                line = newline
        lines.append(line)
        #drawer.text((bounding_box[0], bounding_box[1] + yprogress), line, (0,0,0,255), font=font)
        yprogress += lineheight
    while(yprogress > bounding_box[3] - bounding_box[1] or (len(lines) > numlines)):
        lines = []
        yprogress = 0
        lineheight = font.getsize(text.split("\n")[0])[1]
        font = ImageFont.truetype(fontname, size - 1)
        size -= 1
        print("Size = " + str(size))

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
                    #drawer.text((bounding_box[0], bounding_box[1] + yprogress), line, (0,0,0,255), font=font)
                    lines.append(line)
                    yprogress += lineheight
                    line = word
                else:
                    line = newline
            lines.append(line)
            #drawer.text((bounding_box[0], bounding_box[1] + yprogress), line, (0,0,0,255), font=font)
            yprogress += lineheight
    yprogress = 0
    for line in lines:
        drawer.text((bounding_box[0], bounding_box[1] + yprogress), line, (0,0,0,255), font=font)
        yprogress += lineheight
    return font

def build_logistics(when, where, pizza):
    output = "When: " + str(when)
    output += " \n"
    output += "Where: " + str(where)
    if(pizza):
        output += "\nFree pizza and drinks"
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
        print("Generating poster anyway...")
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


    # set up text drawing 
    draw = ImageDraw.Draw(background)
    supersmallfont = ImageFont.truetype("keep-calm.ttf", 50)
    

    # Title must be one line
    titlefont = draw_multiline(draw, (leftMargin, topMargin, rightMargin, 200 + pageMargin), "keep-calm.ttf", results.name, numlines=1)
    background.save("output.jpg")

    # LUG Promo
    topOfLUGPromo = bottomMargin - 90
    draw_multiline(draw, (sideOfFeaturedImage + internalMargin, topOfLUGPromo, rightMargin, bottomMargin), "keep-calm.ttf", "Brought to you by the Linux Users' Group")
    background.save("output.jpg")

    # Draw event description
    bottomOfTitle = titlefont.getsize(results.name)[1] + pageMargin
    draw_multiline(draw, (pageMargin, bottomOfTitle + internalMargin + pageMargin, math.floor(background.size[0] * 0.5), topOfFeaturedImage - internalMargin), "keep-calm.ttf", results.desc)
    background.save("output.jpg")
    
    numberOfQRCodes = 0
    if(results.facebook != None):
        numberOfQRCodes += 1
    if(results.gcal != None):
        numberOfQRCodes += 1
    if(results.website != None):
        numberOfQRCodes += 1
    # Draw qr codes
    currentQr = 0
    if(numberOfQRCodes != 0):
        qrHeight = math.floor((topOfFeaturedImage - internalMargin) / (numberOfQRCodes + 1))
    
    qrPositions = [(math.floor(background.size[0] * 0.5) + internalMargin, bottomOfTitle + internalMargin),
                (math.floor(background.size[0] * 0.5) + internalMargin + qrHeight + internalMargin, bottomOfTitle + internalMargin),
                (math.floor(background.size[0] * 0.5) + internalMargin, bottomOfTitle + internalMargin + internalMargin + qrHeight)]

    def getQRCaptionPosition(index, text):
        if(index == 0):
            return (math.floor(background.size[0] * 0.5) + internalMargin + (qrHeight / 2) - (supersmallfont.getsize(text)[0] / 2), bottomOfTitle + (internalMargin / 2) + qrHeight)
        elif(index == 1):
            return (math.floor(background.size[0] * 0.5) + internalMargin + internalMargin + qrHeight + (qrHeight / 2) - (supersmallfont.getsize(text)[0] / 2), bottomOfTitle + (internalMargin / 2) + qrHeight)
        elif(index == 2):
            return (math.floor(background.size[0] * 0.5) + internalMargin + (qrHeight / 2) - (supersmallfont.getsize(text)[0] / 2), bottomOfTitle + internalMargin + qrHeight + (internalMargin / 2) + qrHeight)
    

    if(results.facebook != None):
        facebook = qrcode.make(str(results.facebook)).resize((qrHeight, qrHeight), Image.ANTIALIAS)
        background.paste(facebook, qrPositions[currentQr])
        fbcaption = "Facebook"
        draw.text(getQRCaptionPosition(currentQr, fbcaption), fbcaption, (0,0,0,255), font=supersmallfont)
        currentQr += 1
    background.save("output.jpg")
    if(results.gcal != None):
        gcal = qrcode.make(str(results.gcal)).resize((qrHeight, qrHeight), Image.ANTIALIAS)
        background.paste(gcal, qrPositions[currentQr])
        gcalcaption = "Google Calendar"
        draw.text(getQRCaptionPosition(currentQr, gcalcaption), gcalcaption, (0,0,0,255), font=supersmallfont)
        currentQr += 1
    background.save("output.jpg") 
    if(results.website != None):
        website = qrcode.make(str(results.website)).resize((qrHeight, qrHeight), Image.ANTIALIAS)
        background.paste(website, qrPositions[currentQr])
        websitecaption = "Website"
        draw.text(getQRCaptionPosition(currentQr, websitecaption), websitecaption, (0,0,0,255), font=supersmallfont)
        currentQr += 1
    background.save("output.jpg")
    
    
    

    # Draw event time, date, and/or location
    if(results.date != None):
        dateAndTime = build_logistics(results.date, results.location, results.pizza)
        if(results.time != None):
            dateAndTime = build_logistics(results.date + ", " + results.time, results.location, results.pizza)
        draw_multiline(draw, (sideOfFeaturedImage + internalMargin, topOfFeaturedImage, rightMargin, bottomMargin), "keep-calm.ttf", dateAndTime, numlines=3)
        print("Drew date and time")
        
    background.save("static/output.jpg")
    print("Done")

def buildPoster(name, desc, date, time, location, photo, facebook, gcal, website, pizza):
    if(photo != None):
        urllib.request.urlretrieve(photo, "photo.png")
    results = Namespace(name=name, desc=desc, date=date, time=time, location=location, photo="photo.png", facebook=facebook, gcal=gcal, website=website, pizza=pizza)
    template1(make_blank_page(), results)

if __name__ == '__main__':
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
    parser.add_argument("--pizza", action="store_true", help="include if pizza and drinks will be provided")


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




