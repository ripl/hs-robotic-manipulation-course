import cv2
import json
import numpy as np
import threading
from robotics.robot.robot import Robot
import time

CONVERSION_FACTOR = 4096 / 360
CENT_X = 1000
CENT_Y = 300
LOWER_BLUE = np.array([80, 100, 80])
UPPER_BLUE = np.array([120, 255, 255])

AREA_THRESH = 12000
CONF_THRESH = 0.4

def track_piece_ml(countours):
    # Attempt to read capture
    closest_dist = np.array([10000000, 10000000])
    closest_norm = 10000000
    closest_pos = np.array([0,0])
    closest_area = 0

    # Check for most central handle with confidence above 0.5
    for x1, y1, x2, y2, label, conf in countours:
        length = abs(x2 - x1)
        width = abs(y2 - y1)
        area = length * width

        if area > AREA_THRESH and conf > CONF_THRESH:
            cont_pos = np.array([(x1 + x2) // 2, (y1 + y2) // 2])
            cent_pos = np.array([CENT_X, CENT_Y])

            dist = cont_pos - cent_pos
            
            print(f"Error: {dist}\nPos:{cont_pos}\nArea: {area}\nConf: {conf}")

            norm =  np.linalg.norm(cent_pos-cont_pos)
            if norm < closest_norm:
                closest_pos = cont_pos
                closest_dist = dist
                closest_norm = norm
                closest_area = area

    movements = {}

    print()
    print("----------------")
    print(f"Closest Pos: {closest_pos}\nClosest Norm: {closest_norm}\nClosest Dist: {closest_dist}")
    print("----------------")
    print()

    if closest_norm < 1000:
        if closest_pos[0] < 840 or closest_pos[0] > 1200:
            movements[1] = -closest_dist[0] / 50
        if closest_pos[1] > 250 or closest_pos[1] < 140:
            movements[4] = closest_dist[1] / 50
        if closest_area < 15000:
            movements[3] = -30

    return movements