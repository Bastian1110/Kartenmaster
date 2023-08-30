import cv2
import cv2.aruco as aruco
import numpy as np
import json
from random import choice
import serial
from time import sleep

puerto = "/dev/cu.usbmodem1101"
arduino = serial.Serial("/dev/cu.usbmodem1101", 9600, timeout=1)


parameters = aruco.DetectorParameters()
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)


cap = cv2.VideoCapture(0)

Y_AXIS = 200
X_AXIS = 920

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

start_y = (0, Y_AXIS)
end_y = (frame_width, Y_AXIS)
start_x = (X_AXIS, 0)
end_x = (X_AXIS, frame_height)


def classifyCard(coords) -> str:
    if coords[1] > Y_AXIS:
        if coords[0] >= 0 and coords[0] <= 640:
            return "right"
        if coords[0] >= 641 and coords[0] <= 1000:
            return "center"
        return "left"
    if coords[0] > X_AXIS:
        return "stack"
    return "play"


def check_available(cards, actual) -> dict:
    try:
        options = {}
        for key, value in cards.items():
            print(key, value)
            if value["color"] == actual["color"] or value["number"] == actual["number"]:
                options[key] = value
        return options
    except:
        return {}


with open("marker_metadata.json", "r") as cards_file:
    cards = json.load(cards_file)

card_colors = {
    "RED": (0, 0, 250),
    "BLUE": (250, 0, 0),
    "YELLOW": (0, 255, 255),
    "GREEN": (0, 250, 0),
}


def main() -> None:
    turn = "robot"
    top = {"color": "YELLOW", "number": 2}
    top_change = False
    robot_cards = {"left": None, "center": None, "right": None}
    first_play = True
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print(
                    "No se puede obtener el frame de la cámara. Asegúrate de que la cámara esté funcionando correctamente."
                )
                break

            corners, ids, _ = aruco.detectMarkers(
                frame, aruco_dict, parameters=parameters
            )

            if len(corners) > 0:
                frame = aruco.drawDetectedMarkers(frame, corners=corners, ids=ids)

                for i, corner in enumerate(corners):
                    card_info = cards[str(ids[i][0])]
                    center = np.mean(corner[0], axis=0).astype(int)
                    card_type = classifyCard(center)

                    if card_type == "play" and card_info != top:
                        top = card_info
                        top_change = True
                    if card_type != "play" and card_type != "stack":
                        robot_cards[card_type] = card_info
                    cv2.putText(
                        frame,
                        f"{card_info['number']} {card_type}",
                        tuple(center),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        2,
                        card_colors[card_info["color"]],
                        7,
                    )
            if top_change or first_play:
                if first_play:
                    first_play = False
                if turn == "robot":
                    print("Turno del Robot")
                    options = check_available(robot_cards, top)
                    if options:
                        robot_card = choice(list(options.keys()))
                        print("Robot juega : ", robot_card)
                        arduino.write(robot_card.encode())
                        sleep(5)
                        robot_cards[robot_card] = None
                        # mandar serial al arduino de que carta mover
                    else:
                        print("Robot ya no tiene cartas")
                        arduino.write("stack".encode())
                        sleep(5)
                        # checar si hay espacios dispnibles
                        # mandar serial de agarrar carta del stack
                    print("Fin del Robot")
                    turn = "human"
                else:
                    print("Turno del Humano")
                    # El humano hace cosas
                    turn = "robot"
                top_change = False

            cv2.putText(
                frame,
                f"{top['number']}",
                (1650, 980),
                cv2.FONT_HERSHEY_SIMPLEX,
                10,
                card_colors[top["color"]],
                25,
            )
            cv2.line(frame, start_y, end_y, (255, 255, 255), 2)
            cv2.line(frame, start_x, end_x, (255, 255, 255), 2)

            # Muestra el frame
            cv2.imshow("frame", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    sleep(3)
    main()
