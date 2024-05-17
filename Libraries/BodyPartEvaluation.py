from roboflow import Roboflow
import supervision as sv
import os
import cv2
import json

class BodyPartEvaluation:
    def __init__(self, image_path):

        self.image_path = image_path
        global result, image

    def find_and_label(self):

        if (os.path.isfile(self.image_path) == False):
            print("\n\033[31;3m# ERROR: Couldn't find the specified file. Returning to file selection.\033[0m \n")
            return 1
        
        print()

        rf = Roboflow(api_key="MKreIfQxYrRTc7oZ2d9d")
        project = rf.workspace().project("humanfigure-v4.5")
        model = project.version(1).model

        print()

        try:
            global image
            image = cv2.imread(self.image_path)
        except Exception:
            print("\n\033[31;3m# ERROR: Couldn't read the specified file. Returning to file selection.\033[0m \n")
            return 1

        result = model.predict(self.image_path, confidence=50).json()
        labels = [item["class"] for item in result["predictions"]]
        detections = sv.Detections.from_inference(result)
    
        self.translations = {
            "kafa" : "head",
            "govde": "shoulders",
            "kol"  : "arm",
            "bacak": "legs",
            "ayak" : "foot"
        }

        labels1 = [self.translations[i] for i in labels]

        label_annotator = sv.LabelAnnotator()
        mask_annotator = sv.MaskAnnotator()

        annotated_image = mask_annotator.annotate(
            scene=image, detections=detections)
        annotated_image = label_annotator.annotate(
            scene=annotated_image, detections=detections, labels=labels1)

        evaluate = self.evaluate
        data = []
        for prediction in result["predictions"]:
            temp = []
            temp.append(prediction["class"])
            temp.extend([int(prediction[k]) for k in ["x", "y", "width", "height"]])
            data.append(temp)
            if prediction["class"] == "kol":
                points = prediction["points"]
        for part in data:
            name, x, y, w, h = part #x and y are the mid-points of both planes
            name = self.translations[name]
            if name != "arm":
                exec(f"global {name}_w, {name}_h, {name}_x, {name}_y; {name}_w, {name}_h, {name}_x, {name}_y = {w}, {h}, {x}, {y}")
            else:
                global arm_w, arm_h, arm_x, arm_y
                x1 = points[0]["x"]
                y  = points[0]["y"]
                for point in points:
                    if point["y"] == y:
                        x2 = point["x"]
                arm_w = x2 - x1 if x2 - x1 > 0 else x1 - x2
                arm_h, arm_x, arm_y = h, x, y

        torso_head = (legs_y - (head_y - (head_h/2))) / head_h #3-4
        legs_foot = ((foot_y + (foot_h / 2)) - (legs_y + (legs_h / 2)))/head_h #1.75-2.25
        body_head = ((foot_y + foot_h) - (head_y - head_h)) / head_h #5.5-6.5
        shou_head = shoulders_w / head_h #1.5-2 
        armw_head = arm_w / head_h #0.3-0.5
        armh_head = arm_h / head_h #0.75-1.25

        with open("Config/BodyPartEvalConfig.json", "r") as file:
            json_data = json.load(file)
            total_possible = 0
            for value in json_data.values():
                total_possible += value

        grades = {"body_head": evaluate(body_head, 5.5,  6.5,  0, json_data["body_head"], 0.4),
                  "torso_head": evaluate(torso_head, 3,  4,    0, json_data["torso_head"], 0.4),
                  "legs_foot": evaluate(legs_foot, 1.75, 2.25, 0, json_data["legs_foot"],  0.4),
                  "shou_head": evaluate(shou_head, 1.5,  2,    0, json_data["shou_head"], 0.4),
                  "armw_head": evaluate(armw_head, 0.3,  0.5,  0, json_data["armw_head"], 0.4),
                  "armh_head": evaluate(armh_head, 0.75, 1.25, 0, json_data["armh_head"], 0.4)}
        
        total = 0
        for value in grades.values():
            total += value

        print(f"\n------------------ FINAL VERDICT ------------------")
        print("Body/head: " + str(round(grades["body_head"], 2)) + "/" + str(json_data["body_head"]))
        print("Torso/head: " + str(round(grades["torso_head"], 2)) + "/" + str(json_data["torso_head"]))
        print("Leg/foot: " + str(round(grades["legs_foot"], 2)) + "/" + str(json_data["legs_foot"]))
        print("Shoulders/head: " + str(round(grades["shou_head"], 2)) + "/" + str(json_data["shou_head"]))
        print("Arm width/head: " + str(round(grades["armw_head"], 2)) + "/" + str(json_data["armw_head"]))
        print("Arm length/head: "  + str(round(grades["armh_head"], 2)) + "/" + str(json_data["armh_head"]))
        print("TOTAL: "  + str(round(total, 2)) + "/" + str(total_possible))
        print("----------------------------------------------------\n")


        cv2.line(annotated_image, (foot_x, foot_y+foot_h//2), (head_x, head_y-head_h//2), (0,200,0), 2)

        cv2.imshow("Human Figure Evaluation", annotated_image)

        cv2.waitKey(0) 
        cv2.destroyAllWindows()
        return 1
    
    def evaluate(self, ratio, min_ratio, max_ratio, min_score, max_score, allowed_deviation): #all parameters except score are integer percentage values
        deviation = ((min_ratio + max_ratio) / 2) * allowed_deviation
        if min_ratio <= ratio and ratio <= max_ratio:
            return max_score
        if (max_ratio + deviation) < ratio or ratio < (min_ratio - deviation): 
            return min_score #if provided ratio is out of given range and deviates more than allowed -> return minimum score
        elif ratio < min_ratio: #if provided ratio is out of given range but is in allowed deviation range
            return round(min_score + (max_score - min_score) / deviation * (ratio - (min_ratio - deviation)), 2) #calculates the deviation and takes points off accordingly
        elif max_ratio < ratio:
            return round(min_score + (max_score - min_score) / deviation * ((max_ratio + deviation) - ratio), 2)
