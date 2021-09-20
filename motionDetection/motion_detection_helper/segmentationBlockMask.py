def segmentationBlockMask(blockMask):
    imgH, imgW = blockMask.shape
    color = 2
    for m in range(0, imgH - 1):
        for n in range(imgW - 1):
            if blockMask[m, n] != 0:
                if blockMask[m, n] == 1:
                    blockMask[m, n] = color
                    color += 1
                for i in range(m, m + 2):
                    for j in range(n, n + 2):
                        if blockMask[i, j] == 1:
                            blockMask[i, j] = blockMask[m, n]
                for i in range(m, m + 2):
                    if n - 1 >= 0:
                        for j in range(n, n - 2, -1):
                            if blockMask[i, j] == 1:
                                #     if blockMask[i, j] != 0:
                                blockMask[i, j] = blockMask[m, n]

    return blockMask
