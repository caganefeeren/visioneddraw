from roboflow import Roboflow
import os
import supervision as sv
import cv2

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

        label_annotator = sv.LabelAnnotator()
        mask_annotator = sv.MaskAnnotator()

        annotated_image = mask_annotator.annotate(
            scene=image, detections=detections)
        annotated_image = label_annotator.annotate(
            scene=annotated_image, detections=detections, labels=labels)

        self.translations = {
            "kafa" : "head",
            "govde": "body",
            "kol"  : "arm",
            "bacak": "legs",
            "ayak" : "foot"
        }

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
        
        legs_head = (legs_y - (head_y - (head_h/2))) / head_h #3-4
        legs_foot = ((foot_y + (foot_h / 2)) - (legs_y + (legs_h / 2)))/head_h #1.75-2.25
        foot_head = ((foot_y + foot_h) - (head_y - head_h)) / head_h #5.5-6.5
        shou_head = body_w / head_h #1.5-2 
        armw_head = arm_w / head_h #0.3-0.5
        armh_head = arm_h / head_h #0.75-1.25

        grades = {"legs_head": evaluate(legs_head, 3,    4,    0, 10, 0.4),
                  "legs_foot": evaluate(legs_foot, 1.75, 2.25, 0, 10, 0.4),
                  "foot_head": evaluate(foot_head, 5.5,  6.5,  0, 10, 0.4),
                  "shou_head": evaluate(shou_head, 1.5,  2,    0, 10, 0.4),
                  "armw_head": evaluate(armw_head, 0.3,  0.5,  0, 10, 0.4),
                  "armh_head": evaluate(armh_head, 0.75, 1.25, 0, 10, 0.4)}

        cv2.putText(annotated_image, f"Bacak/kafa: " + str(round(grades["legs_head"], 2)) + "/10", (10, 30),  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
        cv2.putText(annotated_image, f"Bacak/ayak: " + str(round(grades["legs_foot"], 2)) + "/10", (10, 60),  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
        cv2.putText(annotated_image, f"Ayak/kafa: "  + str(round(grades["foot_head"], 2)) + "/10", (10, 90),  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
        cv2.putText(annotated_image, f"Omuz/kafa: "  + str(round(grades["shou_head"], 2)) + "/10", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
        cv2.putText(annotated_image, f"Kol genislik/kafa: " + str(round(grades["armw_head"], 2)) + "/10", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
        cv2.putText(annotated_image, f"Kol uzunluk/kafa: "  + str(round(grades["armh_head"], 2)) + "/10", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)

        cv2.imshow("image", annotated_image)
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
        
BodyPartEvaluation("Samples\Human Samples\pic3.jpg").find_and_label()