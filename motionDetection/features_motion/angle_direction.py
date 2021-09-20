import math


def calc_angle(left_edge, right_edge):
    img_width = 640
    xmaxmp = img_width / 2
    # phimax = 90
    phimax = 47.4

    box_center_x = left_edge + (right_edge - left_edge) / 2
    xp = xmaxmp - box_center_x
    phi = math.atan((xp / xmaxmp) * math.tan(phimax))

    return phi


def cal_pos(down_edge, up_edge):
    people_height = 1.65
    yp = down_edge - up_edge
    imgH = 512
    ymaxp = imgH / 2
    # psimax = 30 / 57.2958
    psimax = 39 / 57.2958

    pos = people_height / ((yp / ymaxp) * math.tan(psimax))

    return pos
