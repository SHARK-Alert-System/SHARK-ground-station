#import RPi.GPIO as GPIO
from time import sleep
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime


# initialize constants
TIME_PHOTO_TRIGGER = 0.002 # seconds
TIME_TOGGLE_MEDIA_TRANSFER = 0.0015 # seconds
TIME_NEUTRAL = 0.001 # seconds

PHOTO_INTERVAL = 10 # take a photo every x seconds
NUM_PHOTOS = 10

CAMERA_PWM_PIN = 18 # GPIO pin on the Pi connected to the camera
CAMERA_DIRECTORY = "./Photo" # directory where the camera files can be viewed at

#initialize variables
media_transfer_mode = False

def is_camera_mounted(camera_path):
    try:
        # Check if the provided path exists in the file system
        return os.path.exists(camera_path)

    except Exception as e:
        return False  # Return False in case of any exceptions

#resets to neutral 
def set_neutral():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    time.sleep(0.001)
    GPIO.cleanup(TIME_NEUTRAL)

# takes a photo on the camera
def take_pic():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(TIME_PHOTO_TRIGGER) #1500us pulse width - take photo
    GPIO.cleanup()

# toggles media transfer mode
def toggle_media_transfer():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(TIME_TOGGLE_MEDIA_TRANSFER) #2000us pulse width - toggle media transfer
    GPIO.cleanup()

#returns an array of all file names on the camera, sorted
def listdir():
    return sorted(os.listdir(CAMERA_DIRECTORY))

# gets the most recently taken photo. Assumes filenames are date and timestamps
def get_recent_photo_path():
    return str(CAMERA_DIRECTORY + "/" + str(listdir().pop()))

#gets a cv2 image of the most recently taken photo
def get_recent_photo_img():
    return cv2.imread(get_recent_photo_path(),0)

def get_gps_coordinates():
    return [40.3573, 74.6672]

def take_get_photo():
    take_pic()
    sleep(1)
    toggle_media_transfer()
    sleep(1)
    img = get_recent_photo_img()
    coords = get_gps_coordinates()
    time = datetime.now().strftime("%H:%M:%S")
    infolog = [time,get_recent_photo_path(),coords]
    return img, infolog

def take_photo_and_get_path():
    try:
        # Take a photo
        take_pic()
        time.sleep(1)

        # Turn on media access mode
        toggle_media_transfer()
        while not is_camera_mounted()

        # Get the path of the most recent image
        recent_photo_path = get_recent_photo_path()

        return recent_photo_path

    except Exception as e:
        return str(e)


    
###################################################################################################

#initialization
initialize_gpio()
camera_pwm = initialize_camera()

# Main script logic
print("Time of Mission: ", np.round(NUM_PHOTOS*PHOTO_INTERVAL/60, 2), " mins")



#finally:
    #camera_pwm.stop()
    #GPIO.cleanup()