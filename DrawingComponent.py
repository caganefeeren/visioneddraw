import cv2 as cv
import math
import numpy as np
import sys

class VanishingPointComponent(object):

    REJECT_DEGREE_TH = 4.0
    THRESHOLD = 25

    def FilterLines(self, lines):
        finalLines = []

        for line in lines:
            [[x1, y1, x2, y2]] = line

            # Calculating equation of the line: y = mx + c

            if x1 != x2:
                m = (y2 - y1) / (x2- x1)
            else:
                m = 20000000

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

    def FindLines(self, image):
        # Converting to grayscale to make finding lines easier.
        grayscaleImage = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        # Blurring to denoise the image.
        blurredImage = cv.GaussianBlur(grayscaleImage, (5,5), 0)
        # Creating the edge map of the image.
        edges = cv.Canny(blurredImage, 40, 255)

        # Find the lines.
        lines = cv.HoughLinesP(edges, 1, np.pi / 180, 20, 10, 15)

        if lines is None:
            print("No lines were found, can't detect Vanishing Point of the specified image.")
            sys.exit()

        return lines

    def FindVanishingPoint(self, lines):

        # We will apply RANSAC inspired algorith for this. We will take combination
        # of 2 lines one by one, find their intersection point, and calculate the
        # total error(loss) of that point. Error of the point means root of sum of
        # squares of distance of that point from each line.
        vanishingPoint = None
        minError = 20000000000

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
                distance = abs(tilt * vanishingX - vanishingY + intersectionY) / np.sqrt(tilt ** 2 + 1)
            
            if distance < self.THRESHOLD and verticalDifference > 20 and horizontalDifference > 20:
                cv.line(image, (x1, y1), (x2,y2), (0, 255, 0), 2)
                totalTilt += abs(tilt) 
                linesTowardsVanishingPoint += 1

        if linesTowardsVanishingPoint > 0:
            tiltAverage = totalTilt / linesTowardsVanishingPoint

        return tiltAverage

    def FindHorizontalAndVerticalLines(self, image, lines):
        
        verticalLines = 0
        horizontalLines = 0

        finalScore = 5

        for line in lines:
            x1 = int(round(line[0][0]))
            y1 = int(round(line[0][1]))
            x2 = int(round(line[0][2]))
            y2 = int(round(line[0][3]))

            # TODO: Implement A THRESHOLD HERE
            if abs(x1 - x2) < 50:
                verticalLines += 1
                cv.line(image, (x1, y1), (x2, y2), (0, 140, 255), 2)
            elif abs(y1 - y2) < 50: 
                horizontalLines += 1
                cv.line(image, (x1, y1), (x2, y2), (0, 140, 255), 2)
        
        if verticalLines + horizontalLines > 700:
            finalScore = 20
        elif verticalLines + horizontalLines > 500:
            finalScore = 15
        elif verticalLines + horizontalLines > 300:
            finalScore = 10
        
        return finalScore

    def ShowFinalVerdict(self, image):

        # Finding the lines of a image
        lines = self.FindLines(image)
        filteredLines = self.FilterLines(lines)

        # Finding the vanishing point
        vanishingPoint = self.FindVanishingPoint(filteredLines)

        # Scoring Criterion #1 & #2 (They're intertivened)
        if vanishingPoint is None:
            criterion1 = 00
            criterion2 = 00
        else:
            criterion1 = 10
            criterion2 = 10

            # Drawing the lines, filtered lines, the vanishing point and the horizon line
            for line in lines:
                cv.line(image, (line[0][0], line[0][1]), (line[0][2], line[0][3]), (0, 128, 0), 2)

            for filteredLine in filteredLines:
                cv.line(image, (filteredLine[0], filteredLine[1]), (filteredLine[2], filteredLine[3]), (0, 255, 0), 2)

            cv.circle(image, (int(vanishingPoint[0]), int(vanishingPoint[1])), 10, (0,0,255), -1)
            cv.line(image, (0, int(vanishingPoint[1])), (image.shape[1], int(vanishingPoint[1])), (255,0,0), 2)
        
        # Scoring Criterion #3
        if vanishingPoint is None:
            criterion3 = 00
        else:
            criterion3 = self.FindTiltAverage(image, lines, vanishingPoint) * 20

            if criterion3 > 20:
                criterion3 = 20

        # Scoring Criterion #4
        criterion4 = self.FindHorizontalAndVerticalLines(image, lines)

        print("------------------ FINAL VERDICT ------------------")
        print("Criterion #1: " + str(criterion1) + "(Horizon Line)")
        print("Criterion #2: " + str(criterion2) + "(Escape Point)")
        print("Criterion #3: " + str(criterion3) + "(Tilt Average)")
        print("Criterion #4: " + str(criterion4) + "(Horizontal And Vertical Lines)")

        cv.imshow("OutputImage", image)
        cv.waitKey(0)

    def NewShowFinalVerdict(self, image):

        lsd = cv.createLineSegmentDetector(0)
        lines = lsd.detect(image)[0]
        
        finalImage = lsd.drawSegments(image, lines)
        

        cv.imshow("OutputImage", finalImage)
        cv.waitKey(0)
