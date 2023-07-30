import cv2
import cv2.aruco as aruco
import json

COLORS = ["RED", "BLUE", "YELLOW", "GREEN"]
NUMBERS = list(range(0, 10))

marker_size = 700
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
marker_metadata = {}

for i, color in enumerate(COLORS):
    for number in NUMBERS:
        marker_id = i * len(NUMBERS) + number
        marker_img = aruco.generateImageMarker(aruco_dict, marker_id, marker_size)
        filename = f"./cards/{color}_{number}.jpg"
        cv2.imwrite(filename, marker_img)

        marker_metadata[marker_id] = {"color": color, "number": number}

with open("marker_metadata.json", "w") as f:
    json.dump(marker_metadata, f, indent=4)
