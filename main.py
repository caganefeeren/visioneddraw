import cv2 as cv
import sys

import PerspectiveDrawingComponent
pictures = ["image.png", "image2.png", "image3.png", "image4.png", "hallway.png", "image5.png", "image6.png"]

vpc = PerspectiveDrawingComponent.PerspectiveDrawingComponent()

def StartAnalysis():
    PictureRoulette(pictures)


def PictureRoulette(pictures):
    
    for picture in pictures:
        
        vpc.FinalVerdict(picture)
        
StartAnalysis()