import numpy as np

def getCenterMass(blockMask, r):
    m = {}
    x_c = {}
    y_c = {}

    hBM, wBM = blockMask.shape
    for i in range(hBM):
        for j in range(wBM):
            if blockMask[i, j] > 1:
                color = blockMask[i, j]
                if color in m:
                    m[color] += 1
                    x_c[color] += j
                    y_c[color] += i
                else:
                    m[color] = 1
                    x_c[color] = j
                    y_c[color] = i

    centers_mass = np.zeros((len(x_c), 2), int)
    k = 0
    for color in m:
        centers_mass[k, 0] = x_c[color]/m[color] * r - r / 2
        centers_mass[k, 1] = y_c[color]/m[color] * r - r / 2
        k += 1

    return centers_mass