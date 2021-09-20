import cv2
import socket
import posix_ipc
from mmap import mmap
import numpy as np
import time
import struct

from motion_detection_helper.buildBlockMask import *
from motion_detection_helper.segmentationBlockMask import segmentationBlockMask
from motion_detection_helper.getBoxes import getBoxes
from motion_detection_helper.getCenterMass import getCenterMass

from features_motion.angle_direction import cal_pos, calc_angle
from features_motion.calcDirection import calcDirection
from features_motion.VisibleObject import VisibleObject

from calc_pos.calc_pos import PositionCalculator

_mem = None
_sem = None
_mm = None


def init(memory_name: str, semaphore_name: str):
    global _mem
    global _sem
    global _mm

    _mem = posix_ipc.SharedMemory(memory_name, flags=0)
    _sem = posix_ipc.Semaphore(semaphore_name)

    _mm = mmap(_mem.fd, 0)
    _mm.seek(0)


def close():
    global _mem
    global _sem
    global _mm

    _sem.release()
    _mm.close()
    _sem.close()
    _mem.close_fd()


def read_image():
    global _mem
    global _sem
    global _mm
    global num

    _sem.acquire()
    _mm.seek(0)
    img_width = 1224
    img_height = 370
    num_color_channels = 3
    bytes_array1 = _mm.read(img_width * img_height * num_color_channels)
    _sem.release()

    dt = np.dtype('uint8')

    img_array = np.frombuffer(bytes_array1, dt)
    img = np.reshape(img_array, (img_height, img_width, num_color_channels))
    return img


#udp_ip = '127.0.0.1'
#udp_port = 7070
r = 20
rho = 0.2
history = 100
var_threshold = 16
background_ratio = 0.95
positionCalculator = PositionCalculator('../calc_pos/calc_pos_lib/build/libcalc_pos.so')

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

bgSub = cv2.createBackgroundSubtractorMOG2(history=history, varThreshold=var_threshold)
bgSub.setBackgroundRatio(background_ratio)

numFrame = np.uint64(0)

# try:
#     init('/image_transfer_u505071', '/mem_semaphore_u505071')
# except Exception:
#     print('Shared memory init error')
# else:
#     while True:
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
#         frame = read_image()
path_input_video = 'C://Users/Airat/Desktop/test1.avi'
path_out_video = 'C://Users/Airat/Desktop/test2.avi'

cap = cv2.VideoCapture(path_input_video)
out = cv2.VideoWriter(path_out_video, cv2.VideoWriter_fourcc(*'XVID'), 20.0, (640, 512))

while cap.isOpened():
    ret, frame = cap.read()
    if ret:

        prev_objects_history = []

        start_time = time.time()
        imgOrig = frame
        img = frame

        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        cv2.imshow(img)
        __, __, v = cv2.split(img)
        img = v

        foreground = bgSub.apply(img)
        if numFrame > 0:
            __, bwFG = cv2.threshold(src=foreground, thresh=127, maxval=1, type=cv2.THRESH_BINARY)

            blockMask = buildBlockMask(bwFG, r=r, rho=rho)
            blockMask = segmentationBlockMask(blockMask)
            centers_mass = getCenterMass(blockMask, r)
            boxes = getBoxes(blockMask, r)

            distance_frame = []
            angle_frame = []

            cur_objects_history = []
            for i in range(boxes.shape[0]):
                x1, y1, x2, y2 = boxes[i]
                dist = positionCalculator.calc_distance(y2, y1)
                angle = positionCalculator.calc_angle(x1, x2)
                distance_frame.append(dist)
                angle_frame.append(angle)
                cur_objects_history.append(VisibleObject(dist, angle))

            if numFrame > 1:
                direction = positionCalculator.calc_direction(distance_frame, angle_frame)

                if len(direction) > 0:

                    object_count = 0

                    message = b'#'
                    message += int(4).to_bytes(4, byteorder='big')

                    message += bytes(np.uint64(numFrame).data)[::-1]
                    print('num_frame = {:f}'.format(numFrame))
                    message += len(direction).to_bytes(4, byteorder='big')  # Кол-во объектов

                    for k in range(len(direction)):
                        x1, y1, x2, y2 = boxes[k]

                        if x1 >= 0 and y1 >= 0 and x2 >= 0 and y2 >= 0:
                            message += int(0).to_bytes(4, byteorder='big')
                            message += int(x1).to_bytes(4, byteorder='big')
                            message += int(y1).to_bytes(4, byteorder='big')
                            message += int(x2).to_bytes(4, byteorder='big')
                            message += int(y2).to_bytes(4, byteorder='big')
                            message += struct.pack("f", distance_frame[k])[::-1]
                            message += struct.pack("f", angle_frame[k])[::-1]
                            message += struct.pack("f", direction[k])[::-1]
                            print(direction[k])

                            object_count = object_count + 1

                            cv2.putText(imgOrig, str(direction[k]), (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0),
                                        2, cv2.LINE_AA)

                    replace = lambda a,b,s:a[:s]+b+a[s+len(b):]

                    print("send {:d} num objects, {:d} packet size\n".format(object_count, len(message)), end='')
                    message = replace(message, object_count.to_bytes(4, byteorder='big'), 13)
                    # print(message)
                    sock.sendto(message, (udp_ip, udp_port))
                    # Боксы из MD - синие
                    for i in range(boxes.shape[0]):
                        x1, y1, x2, y2 = boxes[i]
                    cv2.rectangle(imgOrig, (x1, y1), (x2, y2), (255, 0, 0), 2)

            # Центры масс - желтые
            for i in range(centers_mass.shape[0]):
                x_c = centers_mass[i, 0]
                y_c = centers_mass[i, 1]
                cv2.circle(imgOrig, (x_c, y_c), 10, (0, 255, 255), -1)

            cv2.imshow('Frame', imgOrig)

        numFrame += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

cap.release()
out.release()
cv2.destroyAllWindows()
