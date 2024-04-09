import cv2
import sys
import math
import numpy

class PerspectiveDrawingComponent:

    REJECT_DEGREE_TH = 4.0
    THRESHOLD = 25

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
            print("No lines were found, can't detect Vanishing Point of the specified image.")
            sys.exit()

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
                distance = abs(tilt * vanishingX - vanishingY + intersectionY) / numpy.sqrt(tilt ** 2 + 1)
            
            if distance < self.THRESHOLD and verticalDifference > 20 and horizontalDifference > 20:
                cv2.line(image, (x1, y1), (x2,y2), (0, 255, 255), 2)
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
            if abs(x1 - x2) < 7:
                verticalLines += 1
                cv2.line(image, (x1, y1), (x2, y2), (0, 140, 255), 2)
            elif abs(y1 - y2) < 7: 
                horizontalLines += 1
                cv2.line(image, (x1, y1), (x2, y2), (0, 140, 255), 2)
        
        if verticalLines + horizontalLines > 700:
            finalScore = 20
        elif verticalLines + horizontalLines > 500:
            finalScore = 15
        elif verticalLines + horizontalLines > 300:
            finalScore = 10
        
        return finalScore


    # Main Method
    def FinalVerdict(self, imagePath):

        image = cv2.imread(imagePath)
        imageLSD = cv2.imread(imagePath, 0)

        houghLines = self.GetLinesHoughLinesP(image)
        segmentLines = self.GetLinesLineSegmentDetector(imageLSD)

        vanishingPoint = self.FindVanishingPoint(houghLines)

        # Criterions #1, #2 and #3 can't be calculated if there isn't a vanishing point.
        if vanishingPoint == None:
            criterion1 = 0
            criterion2 = 0
            criterion3 = 0
        else:
            criterion1 = 10
            criterion2 = 10
            criterion3 = self.FindTiltAverage(image, segmentLines, vanishingPoint) * 20

        if criterion3 > 20:
            criterion3 = 20

        criterion4 = self.FindHorizontalAndVerticalLines(image, segmentLines)


        # The drawings for criterions #1 and #2 
        if criterion1 == 10 and criterion2 == 10:
            cv2.circle(image, (int(vanishingPoint[0]), int(vanishingPoint[1])), 10, (255, 0, 0), -1)
            cv2.line(image, (0, int(vanishingPoint[1])), (image.shape[1], int(vanishingPoint[1])), (255, 0, 0), 2)

        print("------------------ FINAL VERDICT ------------------")
        print("Criterion #1: " + str(criterion1))
        print("Criterion #2: " + str(criterion2))
        print("Criterion #3: " + str(criterion3))
        print("Criterion #4: " + str(criterion4))


        cv2.imshow("Output Image", image)
        cv2.waitKey(0)
    

