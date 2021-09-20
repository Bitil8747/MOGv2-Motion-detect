# Пройдемся по всему изображению непересекающимся квадратным окном со стороной r.
# Если:
# (сумма пикселей в окне)/r^2 < rho,
# то пометим это это окно значением 1, иначе 0. Сформируем блок-маску(двумерный массив) состояющую из единиц и нулей.

import math
import numpy as np


def buildBlockMask(img, r, rho):
    hImg, wImg = img.shape

    m = math.ceil(hImg / r)
    n = math.ceil(wImg / r)

    blockMask = np.zeros((m, n))

    for i in range(0, m-1):
        for j in range(0, n-1):
            iEnd = i + 1
            jEnd = j + 1
            if iEnd >= m:
                iEnd = m-1
            if jEnd >= n:
                jEnd = m-1

            sum = np.sum(img[i*r:iEnd*r, j*r:jEnd*r])
            # print(sum)
            if sum / (r * r) > rho:
                blockMask[i, j] = 1

    return blockMask
