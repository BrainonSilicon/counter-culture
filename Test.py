import picamera     #camera library
import pygame as pg #audio library
import os           #communicate with os/command line

from google.cloud import vision  #gcp vision library
from time import sleep
from adafruit_crickit import crickit
import time
import signal
import sys
import re           #regular expression lib for string searches!

#set up your GCP credentials - replace the " " in the following line with your .json file and path
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/home/pi/DET-2019-7ea81a376ed2.json"

# this line connects to Google Cloud Vision! 
client = vision.ImageAnnotatorClient()

# global variable for our image file - to be captured soon!
image = 'image.jpg'

def takephoto(camera):
    
    # this triggers an on-screen preview, so you know what you're photographing!
    camera.start_preview() 
    sleep(.5)                   #give it a pause so you can adjust if needed
    camera.capture('image.jpg') #save the image
    camera.stop_preview()       #stop the preview

def localize_objects(image):
    """Localize objects in the local image.

    Args:
    path: The path to the local file.
    """
    client = vision.ImageAnnotatorClient()

    #with open(path, 'rb') as image_file:
    #    content = image_file.read()
    #image = vision.types.Image(content=content)

    objects = client.object_localization(
        image=image).localized_object_annotations

    #print('Number of objects found: {}'.format(len(objects)))
    for object_ in objects:
        #print('\n{} (confidence: {})'.format(object_.name, object_.score))
        area = 0
        if object_.name == 'Person':
            vertices = object_.bounding_poly.normalized_vertices
            #print(vertices) #counterclockwise from bottom left
            length = abs(vertices[0].x - vertices[1].x)
            height = abs(vertices[1].y - vertices[2].y)
            new_area = length*height
            if new_area > area:
                area = new_area
                center_x = vertices[0].x + (length/2)
                center_y = vertices[0].y + (height/2)
                return center_x,center_y

def decision_maker(new,old):
    if (new-old)> 0.3:
        print("picked left")
    elif (new-old)<-0.3:
        print("picked right")
    else:
        print("none chosen")

def offer_choice(choice1, choice2):
    print('{} or {}?'.format(choice1, choice2))
    
        
def main():
    
    #generate a camera object for the takephoto function to
    #work with
    camera = picamera.PiCamera()
    
    #setup our pygame mixer to play audio in subsequent stages
    pg.init()
    pg.mixer.init()
    
    #this while loop lets the script run until you ctrl+c (command line)
    #or press 'stop' (Thonny IDE)
    #while True:
    offer_choice('Hot','Cold')
    takephoto(camera) # First take a picture
    """Run localization request on a single image"""
    with open('image.jpg', 'rb') as image_file:
        #read the image file
        content = image_file.read()
        #convert the image file to a GCP Vision-friendly type
        image = vision.types.Image(content=content)
        (oldx,oldy) = localize_objects(image)
        time.sleep(5)
    
    takephoto(camera)
    with open('image.jpg', 'rb') as image_file:
        #read the image file
        content = image_file.read()
        #convert the image file to a GCP Vision-friendly type
        image = vision.types.Image(content=content)
        (x,y)=localize_objects(image)
        decision_maker(x,oldx)
        (oldx, oldy) = (x,y)
        time.sleep(5)        
        
if __name__ == '__main__':
        main() 