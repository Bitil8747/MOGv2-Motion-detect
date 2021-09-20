import numpy as np
from typing import List
import math
from features_motion.VisibleObject import VisibleObject


# : List[VisibleObject]

def calcDirection(objects_history: List[VisibleObject], distance_frame: List, angle_frame: List):
    new_objects_history = objects_history
    if len(distance_frame) == 0 and len(angle_frame) == 0:
        direction = []
        return direction

    distance_tresh = 0.1
    delta_pred = 50
    phi_tresh = 0.05 * 57.2958

    direction = np.zeros(len(distance_frame))

    for i in range(len(distance_frame)):
        current_distance = distance_frame[i]
        current_angle = angle_frame[i]
        current_number_obj = -1

        for num_obj in range(len(objects_history)):
            # print(str(num_obj) + '; len = ' + str(len(objects_history)))
            obj_distance_list = objects_history[num_obj].dist_arr
            obj_angle_list = objects_history[num_obj].angle_arr
            if abs(current_distance - obj_distance_list[-1] <= distance_tresh):
                if abs(current_angle - obj_angle_list[-1] <= phi_tresh):
                    current_number_obj = num_obj
                    break

        if current_number_obj == -1:
            new_object = VisibleObject(current_distance, current_angle)
            new_objects_history.append(new_object)
            direction[i] = -1
            continue

        history_object = objects_history[current_number_obj]
        history_object_distance_list = history_object.dist_arr
        history_object_angle_list = history_object.angle_arr
        history_object_angle_list = history_object_angle_list / 57.2958
        line_direction = 1
        if len(history_object_distance_list) > 0 and len(history_object_angle_list) > 0:

            x = history_object_distance_list * np.cos(history_object_angle_list)
            y = history_object_distance_list * np.sin(history_object_angle_list)

            p = np.polyfit(x, y, 1)

            a1 = p[0]
            b1 = p[1]
            x_curr = current_distance * math.cos(current_angle / 57.2958)
            y_curr = current_distance * math.sin(current_angle / 57.2958)

            if x[-1] - x[-2] > 0:
                line_direction = 1
            elif x[-1] - x[-2] > 0:
                line_direction = -1
            elif y[-1] - y[-2] > 0:
                line_direction = 1
            elif y[-1] - y[-2] < 0:
                line_direction = -1

            x_new = x_curr + line_direction * delta_pred
            y_new = a1 * x_new + b1

            current_direction = math.atan((y_new - y_curr) / (x_new - x_curr))
            if current_direction < 0:
                current_direction += math.pi
            current_direction = current_direction * 57.2958
            direction[i] = current_direction

        else:
            history_object = history_object.add_point(current_distance, current_angle)
            new_objects_history[current_number_obj] = history_object
            direction[i] = -1
            continue

        history_object.add_point(current_distance, current_angle)
        new_objects_history[current_number_obj] = history_object

        # if new_objects_history is None and len(direction) == 0:
        #     print('000')
        #     return [], []
        # else:
        #     print('111')
        #     return direction, new_objects_history

        return direction, new_objects_history
