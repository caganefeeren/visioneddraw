from Libraries import PerspectiveComponent
import re
import json
import os
import time

class PerspectiveShell:
    # CONFIGURATION INFORMATION
    TAG_CONF = "Config/PerspectiveConfiguration.json"

    # REGEX INFORMATION
    PATH = "\"[^\"]*\"" 
    TAGS = "--[A-Za-z]+\\s[A-Za-z]+"

    # COLOR CODING INFORMATION
    PRIORTY_HIGH = "\033[31;3m"
    PRIORTY_MEDIUM = "\033[33;3m"
    PRIORTY_LOW = "\033[32;3m"
    SCORING_HIGH = "\033[32;1m"
    SCORING_MEDIUM = "\033[33;1m"
    SCORING_LOW = "\033[31;1m"
    FINISH = "\033[0m" 

    pc = PerspectiveComponent.PerspectiveComponent()

    def LoadFileOrDirectory(self):

        text_input = input("\nPlease Drag And Drop A File Or Directory: (Type \"Return\" to return to the main shell.) \n\n")
 
        # A return of 100 means Return To Mode Selection.
        if text_input == "Return":

            return 100

        stringData = self.GetStringData(text_input)

        # A return of 200 means Return To File Selection.
        if (stringData == 200):

            print("\n\033[31;3m# ERROR: Operation couldn't be completed. Returning to file selection.\033[0m \n")
            return 200
        
        # Execute file operations.
        if (stringData[2] == True):

            directoryTimerStart = time.perf_counter()

            directoryStringData = self.GetStringDataDirectory(stringData)

            if directoryStringData == 200 or directoryStringData == 100:
                return

            for fileData in directoryStringData:
               
               self.PerformFileOperations(fileData, True)

            directoryTimerFinish = time.perf_counter()

            directoryTimer = directoryTimerFinish - directoryTimerStart
            directoryTimer = round(directoryTimer, 3)
            directoryTimer = directoryTimer * pow(10, 3)
            directoryTimer = int(directoryTimer)
                   
            input(self.PRIORTY_LOW + "# PROCESS COMPLETED. " + str(len(directoryStringData)) + " items located in \"" + stringData[0] + "\" were processed in " + str(directoryTimer) + " ms." + " Press Enter To Return Back To File Selection... " + self.FINISH + "\n")
            self.LoadFileOrDirectory()

        
        else:
            
            self.PerformFileOperations(stringData)

    def PerformFileOperations(self, stringData, isFromDirectory = False):

        fileTimerStart = time.perf_counter()

        profile = self.CreateProfile(stringData)

        finalPath = str(stringData[0]).strip("\"")

        print("\n" + finalPath)

        results = self.pc.ScoreCriterions(finalPath, profile)
        if (results == 100 or results is None):

            print("\n\033[31;3m# ERROR: Operation couldn't be completed. Returning to file selection.\033[0m \n")
            return 100

        fileTimerFinish = time.perf_counter()

        fileTimer = fileTimerFinish - fileTimerStart
        fileTimer = round(fileTimer, 3)
        fileTimer = fileTimer * pow(10, 3)
        fileTimer = int(fileTimer)

        return self.PrintFinalVerdict(results, profile[0], isFromDirectory, fileTimer)
    


    def GetStringData(self, text):
        regex_path = self.PATH
        regex_tags = self.TAGS

        path = re.findall(regex_path, text)
        tags = re.findall(regex_tags, text)

        if (not path):
            print("\n\033[31;3m# ERROR: Operation couldn't be completed. Returning to file selection.\033[0m \n")
            return 200
        elif (len(path) > 1):
            print("\n\033[31;3m# ERROR: Multiple possible file locations entered. Returning to file selection.\033[0m \n")
            return 200

        isDirectory = False

        # Modify shell arguments if the input is a directory.
        path = path[0].strip("\"")

        if (os.path.isdir(path)):
            isDirectory = True

        result = [path, tags, isDirectory]

        return result
        
    def GetStringDataDirectory(self, directoryData):

        # Check if any files exist within the directory.
        dirList = []
        for x in (os.listdir(directoryData[0])):
            
            if (os.path.isfile(directoryData[0] + os.path.sep + x)):

                dirList.append(directoryData[0] + os.path.sep + x)

        if (not dirList):
            print("\n\033[31;3m# ERROR: Provided directory was empty. Returning to file selection.\033[0m \n")
            return 200

        supportedFileList = []
        for file in dirList:
            if self.pc.CheckFileCompatibility(file):
                supportedFileList.append(file)

        if (not supportedFileList):
            print("\n\033[31;3m# ERROR: None of the files in the provided directory are compatible. Returning to file selection.\033[0m \n")
            return 200
        
        directoryStringData = []
        for file in supportedFileList:
            regexFile = "\"" + file + "\""
            directoryStringData.append(self.GetStringData(regexFile))

        return directoryStringData
       
    def CreateProfile(self, data):

        with open(self.TAG_CONF, "r") as file:

            json_data = json.load(file)

        criterionTags = json_data["criterions-tags"]

        profile = [[],[]]

        # Criterion Tags Profile Creation
        for i in data[1]:
            
            for j in criterionTags:
                
                if (i == j["tag-text"]):

                    profile[0] = j["criterions-multiplier"]
                    profile[1] = j["criterions"]


        if not (profile[1]):
            
            profile[0] = criterionTags[0]["criterions-multiplier"]
            profile[1] = criterionTags[0]["criterions"]

        return profile
                    
    def PrintFinalVerdict(self, results, resultsMultipliers, isFromDirectory, totalTime):

        typographyList = []

        for i in results:
            
            if (i[1] >= 0.75):

                typographyList.append(self.SCORING_HIGH)

            elif (i[1] >= 0.5):

                typographyList.append(self.SCORING_MEDIUM)

            else:
                typographyList.append(self.SCORING_LOW)

        print(f"\n------------------ FINAL VERDICT ------------------")

        index = 0
        total = 0
        for i in results:

            print(f"{typographyList[index]}{i[0]}: {str(i[1] * resultsMultipliers[index])}/{resultsMultipliers[index]} {self.FINISH}")

            total += i[1] * resultsMultipliers[index]
            index += 1

        maximum = 0
        for i in resultsMultipliers:
            
            maximum += i

        if (total/maximum >= 0.75):
        
            totalTypography = self.SCORING_HIGH

        elif (total/maximum >= 0.5):
            
            totalTypography = self.SCORING_MEDIUM

        else:

            totalTypography = self.SCORING_LOW

        print(f"{totalTypography}TOTAL: {total}/{maximum} {self.FINISH}")

        print(f"{self.FINISH}---------------------------------------------------\n")

        if (isFromDirectory):
            
            print(self.PRIORTY_LOW + "# PROCESS COMPLETED SUCCESSFULLY in " + str(totalTime) + " ms." + self.FINISH + "\n")
        
        else:
        
            input(self.PRIORTY_LOW + "# PROCESS COMPLETED SUCCESSFULLY. Press Enter To Return Back To File Selection..." + self.FINISH)

            self.LoadFileOrDirectory()
        
        return 200
        

