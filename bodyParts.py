from roboflow import Roboflow
from random import randint
import supervision as sv
import cv2

rf = Roboflow(api_key="MKreIfQxYrRTc7oZ2d9d")
project = rf.workspace().project("humanfigure-v4.5")
model = project.version(1).model
translation = {
    "kafa": "head",
    "govde": "body",
    "kol": "arm",
    "bacak": "legs",
    "ayak": "foot"
}

class BodyParts:
    def __init__(self, image_path):
        self.image_path = image_path
        global result, image
        image = cv2.imread(image_path)
        result = model.predict(image_path, confidence=50).json()

    def find_and_label(self):
        data = []
        for prediction in result["predictions"]:
            temp = []
            temp.append(prediction["class"])
            temp.extend([int(prediction[k]) for k in ["x", "y", "width", "height"]])
            data.append(temp)
        for part in data:
            name, x, y, w, h = part #x and y are the mid-points of both planes
            name = translation[name]
            exec(f"global {name}_w, {name}_h; {name}_w, {name}_h = {w}, {h}")
            cv2.rectangle(image, (x-w//2,y-h//2), (x+w//2, y+h//2), (0,255,0), 2)
            cv2.putText(image, name, (x-w//2+5, y-h//2+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
        body_head = body_w/head_w  #should be around 2-3
        head_arm  = head_h/arm_h   #should be around 1
        head_legs = head_h/legs_h  #should be around 1
        cv2.putText(image, f"Govde/kafa {round(govde_w/kafa_w, 2)}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
        cv2.putText(image, f"Kafa/kol {round(kafa_h/kol_h, 2)}", (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
        cv2.putText(image, f"Kafa/bacak {round(kafa_h/bacak_h, 2)}", (10,90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
        cv2.imshow("image",image)
        cv2.waitKey(0) 
        cv2.destroyAllWindows()
    
    def evaluate(self):
        print("")


BodyParts(f"images/pic21.jpg").find_and_label()