from Libraries import PerspectiveComponent
import re
import json

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

    def LoadFile(self):

        text_input = input("\nPlease Drag And Drop A File Or Enter The Location Manually: (Type \"Return\" to return to the main shell.) \n\n")
 
        # A return of 100 means Return To Mode Selection.
        if text_input == "Return":

            return 100

        stringData = self.GetStringData(text_input)

        # A return of 200 means Return To File Selection.
        if (stringData == 200):

            print("\n\033[31;3m# ERROR: Operation couldn't be completed. Returning to file selection.\033[0m \n")
            return 200

        profile = self.CreateProfile(stringData)

        finalPath = str(stringData[0][0]).strip("\"")

        results = self.pc.ScoreCriterions(finalPath, profile)

        if (results == 100 or results is None):

            print("\n\033[31;3m# ERROR: Operation couldn't be completed. Returning to file selection.\033[0m \n")
            return 100

        return self.PrintFinalVerdict(results, profile[0])

    def GetStringData(self, text):

        regex_path = self.PATH
        regex_tags = self.TAGS

        path = re.findall(regex_path, text)
        tags = re.findall(regex_tags, text)

        if (not path):

            print("\n\033[31;3m# ERROR: Operation couldn't be completed. Returning to file selection.\033[0m \n")
            return 200


        result = [path, tags]

        return result
        
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
                    
    def PrintFinalVerdict(self, results, resultsMultipliers):

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

        input(self.PRIORTY_LOW + "# PROCESS COMPLETED SUCCESSFULLY. Press Enter To Return Back To File Selection..." + self.FINISH)
        
        return 200
        

