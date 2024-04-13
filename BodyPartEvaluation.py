from roboflow import Roboflow
import cv2

class BodyPartEvaluation:
    def __init__(self, image_path):
        rf = Roboflow(api_key="MKreIfQxYrRTc7oZ2d9d")
        project = rf.workspace().project("humanfigure-v4.5")
        model = project.version(1).model

        self.image_path = image_path
        global result, image
        image = cv2.imread(image_path)
        result = model.predict(image_path, confidence=50).json()
        
        self.translations = {
            "kafa": "head",
            "govde": "body",
            "kol": "arm",
            "bacak": "legs",
            "ayak": "foot"
        }

    def find_and_label(self):
        evaluate = self.evaluate
        data = []
        for prediction in result["predictions"]:
            temp = []
            temp.append(prediction["class"])
            temp.extend([int(prediction[k]) for k in ["x", "y", "width", "height"]])
            data.append(temp)
        for part in data:
            name, x, y, w, h = part #x and y are the mid-points of both planes
            name = self.translations[name]
            exec(f"global {name}_w, {name}_h; {name}_w, {name}_h = {w}, {h}")
            cv2.rectangle(image, (x-w//2,y-h//2), (x+w//2, y+h//2), (0,255,0), 2)
            cv2.putText(image, name, (x-w//2+5, y-h//2+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
        #here comes body part ratios after the meeting
        print(self.evaluate(120,200,300,2,10,30))
        #cv2.putText(image, string, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
        #cv2.putText(image, string, (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
        #cv2.putText(image, string, (10,90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
        #here comes evaluation texts after the meeting
        cv2.imshow("image", image)
        cv2.waitKey(0) 
        cv2.destroyAllWindows()
        return 1
    
    def evaluate(self, ratio, min_ratio, max_ratio, min_score, max_score, allowed_deviation): #all parameters except score are integer percentage values
        deviation = ((min_ratio + max_ratio) / 2) * (allowed_deviation / 100)
        if min_ratio <= ratio and ratio <= max_ratio:
            return max_score
        if (max_ratio + deviation) < ratio or ratio < (min_ratio - deviation): 
            return min_score #if provided ratio is out of given range and deviates more than allowed -> return minimum score
        elif ratio < min_ratio: #if provided ratio is out of given range but is in allowed deviation range
            return round(min_score + (max_score - min_score) / deviation * (ratio - (min_ratio - deviation)), 2) #calculates the deviation and takes points off accordingly
        elif max_ratio < ratio:
            return round(min_score + (max_score - min_score) / deviation * ((max_ratio + deviation) - ratio), 2)
        