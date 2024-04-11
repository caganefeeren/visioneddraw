import cv2
import os
import math
import numpy

class PerspectiveDrawingComponent:

    # COLOR INFORMATION
    PRIORTY_HIGH = "\033[31;3m"
    PRIORTY_MEDIUM = "\033[33;3m"
    PRIORTY_LOW = "\033[32;3m"
    SCORING_HIGH = "\033[32;1m"
    SCORING_MEDIUM = "\033[33;1m"
    SCORING_LOW = "\033[31;1m"
    FINISH = "\033[0m" 


    REJECT_DEGREE_TH = 4.0
    TILT_TH = 25
    HORIZONTAL_VERTICAL_TH = 7

    # Line Extraction Methods
    # Advanced line detection system, used for criterion #3 and #4
    def GetLinesLineSegmentDetector(self, image):

        lsd = cv2.createLineSegmentDetector(0)

        lines = lsd.detect(image)[0]

        return lines
    
    # Basic line detection system, used for criterion #1, #2 and a little bit of #3
    def FilterLines(self, lines):
        finalLines = []

        for line in lines:
            [[x1, y1, x2, y2]] = line

            # Calculating equation of the line: y = mx + c

            if x1 != x2:
                m = (y2 - y1) / (x2- x1)
            else:
                m = 20000000

            numpy.seterr(over="ignore")
            
            c = y2 - m*x2

            # theta will contain values between -90 -> +90
            theta = math.degrees(math.atan(m))

            # Rejecting lines of slope near to 0 or 90 degrees and keeping others
            if self.REJECT_DEGREE_TH <= abs(theta) <= (90 - self.REJECT_DEGREE_TH):
                # l is the length of the line
                l = math.sqrt((y2 - y1)**2 + (x2 - x1)**2)
                # Adds the successful lines to the final array
                finalLines.append([x1, y1, x2, y2, m, c, l])

        # Having so many lines can slow down computations.
        # So the code takes only the longest 15 lines to avoid slowing down.
        if len(finalLines) > 15:
            finalLines = sorted(finalLines, key=lambda x: x[-1], reverse=True)
            finalLines = finalLines[:15]

        return finalLines

    def GetLinesHoughLinesP(self, image):

        grayscaleImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurredImage = cv2.GaussianBlur(grayscaleImage, (5,5), 0)
        edges = cv2.Canny(blurredImage, 40, 255)

        lines = cv2.HoughLinesP(edges, 1, numpy.pi / 180, 20, 10, 15)

        if lines is None:
            return None

        filteredLines = self.FilterLines(lines)

        return filteredLines


    # Criterion Scoring Methods
    def FindVanishingPoint(self, lines):

        # We will apply RANSAC inspired algorith for this. We will take combination
        # of 2 lines one by one, find their intersection point, and calculate the
        # total error(loss) of that point. Error of the point means root of sum of
        # squares of distance of that point from each line.
        vanishingPoint = None
        minError = 20000000000

        if lines is None:
            return vanishingPoint

        # This algorith is too hard to explain.
        for i in range(len(lines)):
            for j in range(i+1, len(lines)):
                m1, c1 = lines[i][4], lines[i][5]
                m2, c2 = lines[j][4], lines[j][5]

                if m1 != m2:
                    x0 = (c1 - c2) / (m2 - m1)
                    y0 = m1 * x0 + c1

                    err = 0
                    for k in range(len(lines)):
                        m, c = lines[k][4], lines[k][5]
                        m_ = (-1 / m)
                        c_ = y0 - m_ * x0

                        x_ = (c - c_) / (m_ - m)
                        y_ = m_ * x_ + c_

                        l = math.sqrt((y_ - y0)**2 + (x_ - x0)**2)

                        err += l**2

                    err = math.sqrt(err)

                    if minError > err:
                        minError = err
                        vanishingPoint = [x0, y0]
                    
        return vanishingPoint

    def FindTiltAverage(self, image, lines, vanishingPoint):

        vanishingX = vanishingPoint[0]
        vanishingY = vanishingPoint[1]

        totalTilt = 0
        linesTowardsVanishingPoint = 0
        tiltAverage = 0

        if (lines is None):
            return tiltAverage

        for line in lines:
            x1 = int(round(line[0][0]))
            y1 = int(round(line[0][1]))
            x2 = int(round(line[0][2]))
            y2 = int(round(line[0][3]))

            dx = x2 - x1
            dy = y2 - y1

            verticalDifference = abs(x1 - x2)
            horizontalDifference = abs(y1 - y2)

            if dx == 0:
                distance = abs(vanishingX - x1)
            elif dy == 0:
                distance = abs(vanishingY - y1)
            else:
                tilt = dy / dx
                intersectionY = y1 - tilt * x1
                distance = abs(tilt * vanishingX - vanishingY + intersectionY) / numpy.sqrt(tilt ** 2 + 1)
            
            if distance < self.TILT_TH and verticalDifference > 20 and horizontalDifference > 20:
                totalTilt += abs(tilt) 
                linesTowardsVanishingPoint += 1

        if linesTowardsVanishingPoint > 0:
            tiltAverage = totalTilt / linesTowardsVanishingPoint

        if tiltAverage > 1:
            tiltAverage = 20
        else:
            tiltAverage *= 20

        return round(tiltAverage)

    def FindHorizontalAndVerticalLines(self, image, lines):
        
        verticalLines = 0
        horizontalLines = 0

        finalScore = 5

        for line in lines:
            x1 = int(round(line[0][0]))
            y1 = int(round(line[0][1]))
            x2 = int(round(line[0][2]))
            y2 = int(round(line[0][3]))

            if abs(x1 - x2) < self.HORIZONTAL_VERTICAL_TH:
                verticalLines += 1
                cv2.line(image, (x1, y1), (x2, y2), (0, 140, 255), 2)
            elif abs(y1 - y2) < self.HORIZONTAL_VERTICAL_TH: 
                horizontalLines += 1
                cv2.line(image, (x1, y1), (x2, y2), (0, 140, 255), 2)
        
        if verticalLines + horizontalLines > 700:
            finalScore = 20
        elif verticalLines + horizontalLines > 500:
            finalScore = 15
        elif verticalLines + horizontalLines > 300:
            finalScore = 10
        
        return finalScore

    def FindLightDarkBalance(self, image):

        grayscaleImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        grayHistogram = cv2.calcHist([grayscaleImage], [0], None, [256], [0, 256])

        totalValue = 0
        totalPixels = 0

        for i in range(1, len(grayHistogram) + 1):

            totalValue += (i - 1) * grayHistogram[i - 1][0]
            totalPixels += grayHistogram[i - 1][0]

        result = totalValue / totalPixels
        deviation = abs(128 - result)

        score = 0

        if 100 > deviation:

            if deviation > 75:
                score = 5
            elif deviation > 60:
                score = 10
            elif deviation > 45:
                score = 15
            elif deviation > 30:
                score = 20

        return score

    def FindColorPerpective(self, event, x, y, flags, params):

        if event == cv2.EVENT_LBUTTONDBLCLK:

            grayscaleImage = cv2.cvtColor(params[1], cv2.COLOR_BGR2GRAY)

            # Gets 4 points from the line. (6 in total, including the start and end positions)
            xPositions = [x, int(round(params[0][0]))]
            yPositions = [y, int(round(params[0][1]))]

            numberOfPoints = 4

            xPoints = numpy.linspace(xPositions[0], xPositions[1], numberOfPoints + 2)
            yPoints = numpy.linspace(yPositions[0], yPositions[1], numberOfPoints + 2)

            finalCoordinates = []

            for i in range(len(xPoints)):
                finalCoordinates.append((int(round(xPoints[i])), int(round(yPoints[i]))))    

            colorValues = []

            for i in range(1, 5):

                x, y = finalCoordinates[i] 
                regionOfInterest = grayscaleImage[y-2:y+3, x-2:x+3]

                (b, g, r) = cv2.mean(regionOfInterest)[:3]
                colorValues.append(b + g + r)

            score = 5

            if colorValues[0] > colorValues[1] > colorValues[2] > colorValues[3]:
                score = 20
            elif colorValues[0] > colorValues[1] > colorValues[2] or colorValues[1] > colorValues[2] > colorValues[3]:
                score = 15
            elif colorValues[0] > colorValues[1] or colorValues[1] > colorValues[2] or colorValues[2] > colorValues[3]:
                score = 10
            
            params[2] = score


    # Main Methods
    def ScoreCriterions(self, imagePath):
        
        if (os.path.isfile(imagePath) == False):
            print("\n\033[31;3m# ERROR: Couldn't find the specified file. Returning to file selection.\033[0m \n")
            return 0

        imageVanishing = cv2.imread(imagePath)
        imagePerspective = cv2.imread(imagePath)
        imageBalance = cv2.imread(imagePath)
        imageLineSegmentDetector = cv2.imread(imagePath, 0)

        if (imageVanishing is None):
            print("\n\033[31;3m# ERROR: Couldn't read the specified file. Returning to file selection.\033[0m \n")
            return 0
        
        houghLines = self.GetLinesHoughLinesP(imageVanishing)
        vanishingPoint = self.FindVanishingPoint(houghLines)

        segmentLines = self.GetLinesLineSegmentDetector(imageLineSegmentDetector)

        if (vanishingPoint is None):
            criterion1 = 0
            criterion2 = 0
            criterion3 = 0
            criterion6 = 0
        else:
            criterion1 = 10
            criterion2 = 10

            if (segmentLines is not None):
                criterion3 = self.FindTiltAverage(imageLineSegmentDetector, segmentLines, vanishingPoint)

            criterion6 = 0
            cv2.circle(imagePerspective, (int(round(vanishingPoint[0])), int(round(vanishingPoint[1]))), 10, (0, 0, 255), 2)
            params = [vanishingPoint, imagePerspective, criterion6]

            cv2.imshow("Color Perspective",imagePerspective)
            cv2.setMouseCallback("Color Perspective", self.FindColorPerpective, params)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

            if (params[2] is None):
                criterion6 = 0
            else:
                criterion6 = params[2]
                        
            # TODO: Handle Criterion 6 here.

        if (segmentLines is None):
            criterion4 = 0
        else:
            criterion4 = self.FindHorizontalAndVerticalLines(imageLineSegmentDetector, segmentLines)

        criterion5 = self.FindLightDarkBalance(imageBalance)

        results = [criterion1, criterion2, criterion3, criterion4, criterion5, criterion6]

        process = self.PrintFinalVerdict(results)

        # TODO: Show Final Image Here

        return process

    def PrintFinalVerdict(self, results):
        typographyList = []

        for i in range(0,2):
            if results[i] == 10:
                typographyList.append(self.SCORING_HIGH)
            else:
                typographyList.append(self.SCORING_LOW)

        for i in range(2,6):
            if results[i] >= 15:
                typographyList.append(self.SCORING_HIGH)
            elif results[i] >= 7.5:
                typographyList.append(self.SCORING_MEDIUM)
            else:
                typographyList.append(self.SCORING_LOW)


        print(f"\n------------------ FINAL VERDICT ------------------")
        print(f"{typographyList[0]}Criterion #1: " + str(results[0]) + "/10")
        print(f"{typographyList[1]}Criterion #2: " + str(results[1]) + "/10")
        print(f"{typographyList[2]}Criterion #3: " + str(results[2]) + "/20")
        print(f"{typographyList[3]}Criterion #4: " + str(results[3]) + "/20")  
        print(f"{typographyList[4]}Criterion #5: " + str(results[4]) + "/20")
        print(f"{typographyList[5]}Criterion #6: " + str(results[5]) + "/20")
        print(f"{self.FINISH}---------------------------------------------------\n")


        input(self.PRIORTY_LOW + "# PROCESS COMPLETED SUCCESSFULLY. Press Enter To Return Back To File Selection..." + self.FINISH)
        return 0