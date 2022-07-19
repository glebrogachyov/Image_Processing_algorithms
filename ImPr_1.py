from sys import argv


def read_pgm(pgmf):
    tp = pgmf.readline()
    (width, height) = [int(i) for i in pgmf.readline().split()]
    depth = int(pgmf.readline())
    if depth > 255:
        print("Depth error. >255")
        pgmf.close()
        exit(1)
    raster = []
    color = False
    if tp == b'P5\n':
        for _ in range(height):
            row = []
            for _ in range(width):
                row.append(ord(pgmf.read(1)))
            raster.append(row)
    elif tp == b'P6\n':
        color = True
        for _ in range(height):
            row = []
            for _ in range(width):
                pix = []
                for _ in range(3):
                    pix.append(ord(pgmf.read(1)))
                row.append(pix)
            raster.append(row)
    else:
        print("Format error. Exit.")
        pgmf.close()
        exit(1)
    return raster, depth, color


def write_pgm(arr, name, depth, color):
    line = str(len(arr[0])) + chr(32) + str(len(arr)) + chr(10) + str(depth) + chr(10)
    try:
        with open(name, "wb") as f:
            if not color:
                f.write(b'P5\n')
                f.write(bytes(line.encode('utf8')))
                for i in arr:
                    f.write(bytes(i))
            else:
                f.write(b'P6\n')
                f.write(bytes(line.encode('utf8')))
                for i in arr:
                    for j in i:
                        f.write(bytes(j))
    except IOError:
        print("Error opening out-file. Exit.")
        exit(1)


def invert(arr, depth, color):
    res = []
    if not color:
        for i in arr:
            tmp = [depth - pix for pix in i]
            res.append(tmp)
    else:
        for i in arr:
            tmp = []
            for j in i:
                pix = [depth - c for c in j]
                tmp.append(pix)
            res.append(tmp)
    return res


def hor(arr):
    width = len(arr[0])
    for a in arr:
        for i in range(width//2):
            a[i], a[width-1-i] = a[width-1-i], a[i]
    return arr


def ver(arr):
    cnt = len(arr)
    for i in range(cnt//2):
        arr[i], arr[cnt-1-i] = arr[cnt-1-i], arr[i]
    return arr


def right(arr):
    h, w = len(arr[0]), len(arr)
    res = [[0 for _ in range(w)] for _ in range(h)]
    for i in range(h):
        for j in range(w):
            res[i][j] = arr[w - j - 1][i]
    return res


def left(arr):
    h, w = len(arr[0]), len(arr)
    res = [[0 for _ in range(w)] for _ in range(h)]
    for i in range(h):
        for j in range(w):
            res[i][j] = arr[j][h - i - 1]
    return res


def menu(name_in, name_out, ch):
    """
        fl      - файл изображения
        pic     - массив пикселей
        val     - максимальное значение пикселя
        clr     - цветное ли изображение, булева переменная
    """
    try:
        fl = open(name_in, "rb")
    except IOError:
        print("Cannot open file. Exit.")
        exit(1)
    pic, val, clr = read_pgm(fl)
    if ch == "0":
        pic = invert(pic, val, clr)
    elif ch == "1":
        pic = hor(pic)
    elif ch == "2":
        pic = ver(pic)
    elif ch == "3":
        pic = right(pic)
    elif ch == "4":
        pic = left(pic)
    else:
        print("Wrong action number. Exit.")
        fl.close()
        exit(1)
    write_pgm(pic, name_out, val, clr)
    fl.close()


for i in range(5):
    print(i)
    menu("ff.pgm", "out"+str(i)+".pgm", str(i))
