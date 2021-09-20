import numpy  as np

def getBoxes(blockMask, r):
    imgH, imgW = blockMask.shape

    leftEdge = {}
    rightEdge = {}
    topEdge = {}
    downEdge = {}

    for i in range(imgH):
        for j in range(imgW):
            color = blockMask[i, j]
            if color > 1:
                if color in leftEdge:
                    if j < leftEdge[color]:
                        leftEdge[color] = j
                else:
                    leftEdge[color] = j

                if color in rightEdge:
                    if j > rightEdge[color]:
                        rightEdge[color] = j
                else:
                    rightEdge[color] = j

                if color in topEdge:
                    if i < topEdge[color]:
                        topEdge[color] = i
                else:
                    topEdge[color] = i

                if color in downEdge:
                    if i > downEdge[color]:
                        downEdge[color] = i
                else:
                    downEdge[color] = i

    boxes = np.zeros((len(leftEdge), 4), int)
    k = 0
    for color in leftEdge:
        boxes[k, 0] = (leftEdge[color] ) * r
        boxes[k, 1] = (topEdge[color]) * r
        boxes[k, 2] = rightEdge[color] * r
        boxes[k, 3] = downEdge[color] * r
        k += 1

    def intersect(x, y):
        return x[1] >= y[0] and y[1] >= x[0]

    for i in range(boxes.shape[0]):
        for j in range(boxes.shape[0]):
            if i != j:
                a_x = [boxes[i, 0], boxes[i, 2]]
                b_x = [boxes[j, 0], boxes[j, 2]]

                a_y = [boxes[i, 1], boxes[i, 3]]
                b_y = [boxes[j, 1], boxes[j, 3]]

                if intersect(a_x, b_x) and intersect(a_y, b_y):
                    min_left = min(boxes[i, 0], boxes[j, 0])
                    max_right = max(boxes[i, 2], boxes[j, 2])
                    max_down = max(boxes[i, 3], boxes[j, 3])
                    min_up = min(boxes[i, 1], boxes[j, 1])
                    boxes[i] = np.array([min_left, min_up, max_right, max_down])
                    boxes[j] = np.zeros(4)

    return boxes