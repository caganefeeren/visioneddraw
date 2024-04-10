import PerspectiveDrawingComponent

import cv2

picturesPath = "./Samples/"
pictures = ["image.png", "image2.png", "image3.png", "image4.png", "image5.png", "image6.png", "image7.png",
             "image8.png", "image9.png", "image10.png"]

vpc = PerspectiveDrawingComponent.PerspectiveDrawingComponent()

def StartAnalysis():
    PictureRoulette(pictures)


def PictureRoulette(pictures):
    for picture in pictures:

        vpc.FinalVerdict(picturesPath + picture)
        
StartAnalysis()