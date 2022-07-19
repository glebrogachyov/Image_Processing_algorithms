from sys import argv
from random import randint


ord_map = [[  0, 192,   48,  240,   12,  204,   60,  252],
           [128, 64,   176,  112,  140,   76,  188,  124],
           [ 32, 224,   16,  208,   44,  236,   28,  220],
           [160, 96,   144,   80,  172,  108,  156,   92],
           [  8, 200,   56,  248,    4,  196,   52,  244],
           [136, 72,   184,  120,  132,   68,  180,  116],
           [ 40, 232,   24,  216,   36,  228,   20,  212],
           [168, 104,  152,   88,  164,  100,  148,  84]]


def read_pgm(pgmf, grad):
    tp = pgmf.readline()
    if tp != b'P5\n':
        print("File format error. Exit")
        pgmf.close()
        exit(1)
    (width, height) = [int(n) for n in pgmf.readline().split()]
    depth = int(pgmf.readline())
    if depth > 255:
        print("Depth error. Exit")
        pgmf.close()
        exit(1)
    raster = []
    step = 256/width
    if grad:
        raster = [[0 for _ in range(width)] for _ in range(height)]
        for i in range(height):
            for j in range(width):
                raster[i][j] = int(j*step)
    else:
        for _ in range(height):
            row = []
            for _ in range(width):
                row.append(ord(pgmf.read(1)))
            raster.append(row)
    return raster, depth


def write_pgm(arr, name, depth):
    line = str(len(arr[0])) + chr(32) + str(len(arr)) + chr(10) + str(depth) + chr(10)
    try:
        with open(name, "wb") as f:
            f.write(b'P5\n')
            f.write(bytes(line.encode('utf8')))
            for i in arr:
                f.write(bytes(i))
    except IOError:
        print("Error opening out-file. Exit.")
        exit(1)


def find_nearest(pix, u_d, step):
    return min(255, int((pix // step) * step + u_d * step))


def ord_dith(arr, step):
    res = []
    ii = 0
    for i in arr:
        tmp = []
        i_it = ii % 8
        j_it = 0
        for j in i:
            if (ord_map[i_it][j_it % 8]) % step < j % step:
                tmp.append(find_nearest(j, 1, step))
            else:
                tmp.append(find_nearest(j, 0, step))
            j_it += 1
        res.append(tmp)
        ii += 1
    return res


def rand_dith(arr, step):
    res = []
    for i in arr:
        tmp = []
        for j in i:
            tmp.append(find_nearest(j, 1, step) if randint(0, int(step)) < j % step else find_nearest(j, 0, step))
        res.append(tmp)
    return res


def f_s_dith(arr, step):
    h_step = step/2
    w, h = len(arr[0]), len(arr)
    for i in range(h):
        for j in range(w):
            if arr[i][j] % step > h_step:
                tmp = find_nearest(arr[i][j], 1, step)
                err = arr[i][j] - tmp
                arr[i][j] = tmp
            else:
                tmp = find_nearest(arr[i][j], 0, step)
                err = arr[i][j] - tmp
                arr[i][j] = tmp
            if j+1 < w:
                arr[i][j+1] = min(255, max(0, (arr[i][j+1] + 7 * err // 16)))
            if i+1 < h:
                arr[i+1][j] = min(255, max(0, (arr[i+1][j] + 3 * err // 16)))
                if j-1 >= 0:
                    arr[i+1][j-1] = min(255, max(0, (arr[i+1][j-1] + 5 * err // 16)))
                if j+1 < w:
                    arr[i+1][j+1] = min(255, max(0, (arr[i+1][j+1] + 1 * err // 16)))
    return arr


def menu(name_in, name_out, grad, alg, bit, gamma=1):
    try:
        fl = open(name_in, "rb")
    except IOError:
        print("Cannot open file. Exit.")
        exit(1)
    pic, val = read_pgm(fl, bool(int(grad)))
    fl.close()
    bit = int(bit)
    if not 0 < bit <= 8:
        print("Error of bitrate!")
        exit(1)
    step = round(256 / (2**bit - 1), 8)
    if alg == "0":
        pass
    elif alg == "1":
        pic = ord_dith(pic, step)
    elif alg == "2":
        pic = rand_dith(pic, step)
    elif alg == "3":
        pic = f_s_dith(pic, step)
    else:
        print("Error choosing algorithm. Exit.")
        exit(1)
    write_pgm(pic, name_out, val)


params = argv
menu(*params[1:])
