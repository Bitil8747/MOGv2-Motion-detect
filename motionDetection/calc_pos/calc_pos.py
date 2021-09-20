from ctypes import *
import os


class ImageSettings(Structure):
    _fields_ = [('width', c_int),
                ('height', c_int)]


class CameraSettings(Structure):
    _fields_ = [('horizontal_angle', c_double),
                ('vertical_angle', c_double)]


class PolarObject(Structure):
    _fields_ = [('distance_list', POINTER(c_double)),
                ('angle_list', POINTER(c_double)),
                ('size', c_int),
                ('max_size', c_size_t)]


class PositionCalculator:
    def __init__(self, lib_path: str):
        self.lib = CDLL(lib_path)
        self.lib.create_default_image_settings.restype = ImageSettings
        self.lib.create_default_camera_settings.restype = CameraSettings
        self.lib.calc_angle.restype = c_double
        self.lib.calc_distance.restype = c_double

        self.image_settings = self.lib.create_default_image_settings()
        self.camera_settings = self.lib.create_default_camera_settings()

        self.history_object = (PolarObject * 1000)()
        self.history_object_size = 0
        self.no_direction = c_double.in_dll(self.lib, "NO_DIRECTION").value
        self.no_angle = c_double.in_dll(self.lib, "NO_ANGLE").value
        self.no_distance = c_double.in_dll(self.lib, "NO_DISTANCE").value


    def set_image_settings(self, width: int, height: int):
        self.image_settings.width = width
        self.image_settings.height = height

    def clear(self):
        for i in range(self.history_object_size):
            self.lib.clear_polar_object(self.history_object[i])

    def set_camera_settings(self, horizontal_angle, vertical_angle):
        self.camera_settings.horizontal_angle = horizontal_angle
        self.camera_settings.vertical_angle = vertical_angle

    def calc_angle(self, left: int, right: int):
        angle = self.lib.calc_angle(self.image_settings, self.camera_settings, c_int(left), c_int(right))
        return angle

    def calc_distance(self, down: int, up: int):
        distance = self.lib.calc_distance(self.image_settings, self.camera_settings, c_int(down), c_int(up))
        return distance

    def generate_c_code(self, distance_list: list, angle_list: list):
        print("printf({})".format('"*** frame ***"'))
        print("new_objects_count = {:d};\n".format(len(distance_list)), end='')
        print("new_distances = calloc((double) new_objects_count, sizeof (double));\n", end='')
        print("new_angles    = calloc((double) new_objects_count, sizeof (double));\n", end='')
        print("directions    = calloc((double) new_objects_count, sizeof (double));\n", end='')

        for i in range(len(distance_list)):
            print("new_distances[{:d}] = {:f};\n".format(i, distance_list[i]), end='')

        for i in range(len(angle_list)):
            print("new_angles[{:d}] = {:f};\n".format(i, angle_list[i]), end='')

        print("calc_direction(objects_history, objects_history_size, new_distances, new_angles, \n", end='')
        print("                new_objects_count, directions, &new_objects_history_size);\n", end='')
        print("objects_history_size = new_objects_history_size;\n", end='')
        print("free(new_distances);\n", end='')
        print("free(new_angles);\n", end='')
        print("free(directions);\n", end='')
        print('\n\n', end='')

    def calc_direction(self, distance_list: list, angle_list: list):
        # self.generate_c_code(distance_list, angle_list)

        c_distance_list = (c_double * len(distance_list))(*distance_list)
        c_angle_list = (c_double * len(angle_list))(*angle_list)
        c_new_object_count = c_int(len(distance_list))
        c_new_object_history_size = c_int(0)
        c_direction = (c_double * 1000)()
        self.lib.calc_direction(self.history_object, self.history_object_size, c_distance_list, c_angle_list,
                                c_new_object_count, c_direction, byref(c_new_object_history_size))
        self.history_object_size = c_new_object_history_size.value
        return [c_direction[i] for i in range(c_new_object_count.value)]


if __name__ == "__main__":
    calc = PositionCalculator(os.getcwd() + '/calc_pos_c.so')
    print(calc.calc_angle(80, 100))
    print(calc.calc_distance(185, 120))


    for i in range(10000000):
        distance_list = [i]
        angle_list = [i]
        directions = calc.calc_direction(distance_list, angle_list)
        # print(len(directions))
