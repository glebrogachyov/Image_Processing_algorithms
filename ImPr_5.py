from sys import argv


def read_pic(pbmf):
    tp = pbmf.readline()
    (w, h) = [int(n) for n in pbmf.readline().split()]
    clr = False
    if tp == b'P6\n':
        rng = w*h*3
        clr = True
    elif tp == b'P5\n':
        rng = w*h
    else:
        print("Wrong picture format. Exit.")
        exit(1)
    depth = int(pbmf.readline())
    if depth != 255:
        print("Image depth error. Exit")
        pbmf.close()
        exit(1)
    try:
        pic = [-1 for _ in range(rng)]
    except MemoryError:
        print("Memory Error. Exit.")
        pbmf.close()
        exit(1)
    except Exception:
        print("Error of memory allocation. Exit.")
        pbmf.close()
        exit(1)
    for p in range(rng):
        pic[p] = int(ord(pbmf.read(1)))
    return pic, w, h, clr


def write_pic(arr, name, clr, w, h):
    ln = b'P6\n' if clr else b'P5\n'
    line = str(w) + chr(32) + str(h) + chr(10) + "255" + chr(10)
    try:
        with open(name, "wb") as f:
            f.write(ln)
            f.write(bytes(line.encode('utf8')))
            # print("Заголовок записан.")
            f.write(bytes(arr))
    except IOError:
        print("Error opening out-file. Exit.")
        exit(1)


def sharp(pic, clr, w, h, k, res_pic):
    if clr:
        # print("clr wth")
        sharp = -1 / (8 * (1 - k) + 5 * k)
        for x in range(h - 2):
            for y in range(w - 2):
                xx = x * 3
                yy = y * 3
                for j in range(3):
                    a = pic[xx * w + yy + j] / 255
                    b = pic[xx * w + yy + 3 + j] / 255
                    c = pic[xx * w + yy + 6 + j] / 255
                    d = pic[(xx + 3) * w + yy + j] / 255
                    e = pic[(xx + 3) * w + yy + 3 + j] / 255  # main pixel
                    f = pic[(xx + 3) * w + yy + 6 + j] / 255
                    g = pic[(xx + 6) * w + yy + j] / 255
                    h = pic[(xx + 6) * w + yy + 3 + j] / 255
                    i = pic[(xx + 6) * w + yy + 6 + j] / 255

                    mn = min(d, e, f, b, h)
                    mn2 = min(mn, a, c, g, i)
                    mn += mn2
                    mx = max(d, e, f, b, h)
                    mx2 = max(mx, a, c, g, i)
                    mx += mx2
                    if mx == 0:
                        mx = 0.0000000000000000000000000000001
                    amp = min(1, max(0, min(mn, 2 - mx) / mx))
                    if amp == 0:
                        amp = 0.0000000000000000000000000000001

                    amp = amp ** (1 / 2)
                    wght = amp * sharp
                    rwght = 1 / (1 + 4 * wght)
                    window = b + d + f + h
                    out = (window * wght + e) * rwght
                    res = min(255, max(0, round(out * 255)))
                    res_pic[(xx + 3) * w + yy + 3 + j] = res
    else:
        # print("!clr")
        sharp = -1 / (8 * (1 - k) + 5 * k)
        for x in range(h-2):
            for y in range(w-2):
                a = pic[x * w + y] / 255
                b = pic[x * w + y + 1] / 255
                c = pic[x * w + y + 2] / 255
                d = pic[(x + 1) * w + y] / 255
                e = pic[(x + 1) * w + y + 1] / 255           # main pixel
                f = pic[(x + 1) * w + y + 2] / 255
                g = pic[(x + 2) * w + y] / 255
                h = pic[(x + 2) * w + y + 1] / 255
                i = pic[(x + 2) * w + y + 2] / 255

                mn = min(d, e, f, b, h)
                mn2 = min(mn, a, c, g, i)
                mn += mn2
                mx = max(d, e, f, b, h)
                mx2 = max(mx, a, c, g, i)
                mx += mx2
                if mx == 0:
                    mx = 0.0000000000000000000000000000001
                amp = min(1, max(0, min(mn, 2 - mx) / mx))
                if amp == 0:
                    amp = 0.0000000000000000000000000000001

                amp = amp ** (1 / 2)
                # peak = 8 - 3 * k
                # wght = -1/(amp * peak)
                wght = amp * sharp
                rwght = 1 / (1 + 4 * wght)
                window = b + d + f + h
                out = (window * wght + e) * rwght
                res = min(255, max(0, round(out * 255)))
                res_pic[(x + 1) * w + y + 1] = res


def menu(inp, outp, sharpen):
    # if inp.endswith(".pgm") or inp.endswith(".ppm"):
        # clr = False
    # elif inp.endswith(".ppm"):
    #    clr = True
    # else:
    #     print("Unsupported file extension. Exit.")
    #     exit(1)
    if not 0 <= sharpen <= 1:
        print("Unsupported sharpen value. Exit.")
        exit(1)
    try:
        fl = open(inp, "rb")
    except IOError:
        print("Cannot open file. Exit.")
        exit(1)
    pic, w, h, clr = read_pic(fl)
    res_pic = []
    for px in pic:
        res_pic.append(px)
    fl.close()
    sharp(pic, clr, w, h, sharpen, res_pic)
    # clr = False
    write_pic(res_pic, outp, clr, w, h)


params = argv[1:]
# print(params)
inp, outp, sharpen = params[0], params[1], float(params[2])
menu(inp, outp, sharpen)
