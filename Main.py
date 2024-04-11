import PerspectiveDrawingComponent
import os 

def StartPerspectiveMode():

    print("Welcome to the Perspective Drawing Mode! \n")

    print("\033[31;3m# DISCLAIMER: This is demo software. Some features may not work as intended.")
    print("\033[33;3m# SUGGESTION: Take the photos in a well-lit enviorment for fair grading.\033[0m")

    LoadFilePerspectiveMode()

def LoadFilePerspectiveMode():

    path = input("\nPlease Drag And Drop A File Or Enter The Location Manually: \n\n")
        
    process = pdc.ScoreCriterions(path)

    if (process == 0):
        LoadFilePerspectiveMode()

        
pdc = PerspectiveDrawingComponent.PerspectiveDrawingComponent()
StartPerspectiveMode()