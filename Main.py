from Libraries import PerspectiveShell
from Libraries import PerspectiveComponent
from Libraries import BodyPartEvaluation

import sys

def StartProjectShell():
    print("Welcome to VisionEdDraw!")

    print("\n\033[31;3m# This is demo software, some features may not function as intended. \033[0m")
    print("\033[33;3m# Take the photos in a well-lit enviorment for fair grading.\033[0m")

    ModeSelect()

def ModeSelect():

    directive = input("\nType \"Perspective Mode\" or \"Body Parts Mode\" to start the components. (Type \"Exit\" to exit.)\n\n")

    if directive == "Exit":
        print("\n\033[31;3m# Closing Program")
        sys.exit()
    elif directive == "Perspective Mode":

        StartPerspectiveMode()

    elif directive == "Body Parts Mode":
        StartBodyPartsMode()
    else:
        print("\033[31;3m# ERROR: Couldn't find the specified mode, returning to mode select.\033[0m \n\n")
        ModeSelect()

def StartPerspectiveMode():

    print("\nWelcome to the Perspective Drawing Mode!")

    LoadFilePerspectiveMode()

def LoadFilePerspectiveMode():

    ps = PerspectiveShell.PerspectiveShell()

    process = ps.LoadFile()

    if (process == 100):

        ModeSelect()

    elif (process == 200):

        LoadFilePerspectiveMode()

def StartBodyPartsMode():

    path = input("\nPlease Drag And Drop A File Or Enter The Location Manually: (Type \"Return\" to return to the main shell.) \n\n")

    if path == "Return":
        ModeSelect()

    finalPath = path.strip("\"")

    bpe = BodyPartEvaluation.BodyPartEvaluation(finalPath)
    process = bpe.find_and_label()

    if (process == 1):
        StartBodyPartsMode()

pc = PerspectiveComponent.PerspectiveComponent()

StartProjectShell()
