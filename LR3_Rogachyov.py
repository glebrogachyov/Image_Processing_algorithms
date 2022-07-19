from sys import argv


def read_clr(pbmf):
    tp = pbmf.readline()
    if tp != b'P6\n':
        print("Not P6. Exit.")
        pbmf.close()
        exit(1)
    (w, h) = [int(n) for n in pbmf.readline().split()]
    depth = int(pbmf.readline())
    if depth != 255:
        print("Image depth error. Exit")
        pbmf.close()
        exit(1)
    try:
        pic = [-1 for _ in range(w*h*3)]
    except MemoryError:
        print("Memory Error. Exit.")
        pbmf.close()
        exit(1)
    except Exception:
        print("Error of memory allocation. Exit.")
        pbmf.close()
        exit(1)
    for p in range(w*h*3):
        pic[p] = int(ord(pbmf.read(1)))
    return pic, w, h


def read_bw(r_ch, g_ch, b_ch):
    tp_r, tp_g, tp_b = r_ch.readline(),g_ch.readline(), b_ch.readline()
    if (tp_r or tp_g or tp_b) != b'P5\n':
        print("Some channel(s) are not P5. Exit")
        r_ch.close()
        g_ch.close()
        b_ch.close()
        exit(1)
    (w_r, h_r), (w_g, h_g), (w_b, h_b) = [int(n) for n in r_ch.readline().split()],\
                                [int(n) for n in g_ch.readline().split()], [int(n) for n in b_ch.readline().split()]
    if not (w_r, h_r) == (w_g, h_g) == (w_b, h_b):
        print("Picture channels have different w/h parameters. Exit.")
        r_ch.close()
        g_ch.close()
        b_ch.close()
        exit(1)
    d_r, d_g, d_b = int(r_ch.readline()), int(g_ch.readline()), int(b_ch.readline())
    if (d_r or d_g or d_g) != 255:
        print("Depth of some channel(s) is not 255. Exit.")
        r_ch.close()
        g_ch.close()
        b_ch.close()
        exit(1)
    try:
        pic = [0 for _ in range(w_r*h_r*3)]
    except MemoryError:
        print("Memory Error. Exit.")
        r_ch.close()
        g_ch.close()
        b_ch.close()
        exit(1)
    except Exception:
        print("Error while allocating memory. Exit.")
        r_ch.close()
        g_ch.close()
        b_ch.close()
        exit(1)
    for p in range(w_r*h_r):
        pic[p * 3] = int(ord(r_ch.read(1)))
        pic[p*3+1] = int(ord(g_ch.read(1)))
        pic[p*3+2] = int(ord(b_ch.read(1)))
    return pic, w_r, h_r


def write_clr(arr, name, w, h):
    line = str(w) + chr(32) + str(h) + chr(10) + "255" + chr(10)
    try:
        with open(name, "wb") as f:
            f.write(b'P6\n')
            f.write(bytes(line.encode('utf8')))
            # print("Заголовок записан.")
            f.write(bytes(arr))
    except IOError:
        print("Error opening out-file. Exit.")
        exit(1)


def write_bw(arr, names, w, h):
    line = str(w) + chr(32) + str(h) + chr(10) + "255" + chr(10)
    try:
        r_ch = open(names[0], "wb"); r_ch.write(b'P5\n'); r_ch.write(bytes(line.encode('utf8')))
        g_ch = open(names[1], "wb"); g_ch.write(b'P5\n'); g_ch.write(bytes(line.encode('utf8')))
        b_ch = open(names[2], "wb"); b_ch.write(b'P5\n'); b_ch.write(bytes(line.encode('utf8')))
        r_ch.write(bytes(arr[::3])); g_ch.write(bytes(arr[1::3])); b_ch.write(bytes(arr[2::3]))
        r_ch.close(); g_ch.close(); b_ch.close()
    except IOError:
        print("Error opening the output file. Exit.")
        r_ch.close(); g_ch.close(); b_ch.close()
        exit(1)


def hsl(arr, reverse=False):
    # print("hsl called, rev =", reverse)
    if not reverse:
        for i in range(len(arr)//3):
            r, g, b = arr[i * 3]/255, arr[i * 3 + 1]/255, arr[i * 3 + 2]/255
            maxv = max(r, g, b)
            minv = min(r, g, b)
            delta = maxv - minv
            l = (maxv + minv) / 2
            if delta == 0:
                arr[i * 3] = 0
                arr[i * 3 + 1] = 0
            else:
                if maxv == r:
                    arr[i * 3] = max(0, min(255, round(42.618384401114 * (((g-b) / delta) % 6))))
                elif maxv == g:
                    arr[i * 3] = max(0, min(255, round(42.618384401114 * (((b-r) / delta) + 2))))
                elif maxv == b:
                    arr[i * 3] = max(0, min(255, round(42.618384401114 * (((r-g) / delta) + 4))))
                arr[i * 3 + 1] = max(0, min(255, round(255 * delta / (1 - abs(2*l - 1)))))
            arr[i * 3 + 2] = max(0, min(255, round(l * 255)))
    else:
        for i in range(len(arr) // 3):
            h, s, l = arr[i * 3]*359/255, arr[i * 3 + 1]/255, arr[i * 3 + 2]/255
            c = (1 - abs(2*l - 1)) * s
            x = c * (1 - abs((h / 60) % 2 - 1))
            m = l - c/2
            c = min(255, (max(0, round((c + m) * 255))))
            x = min(255, (max(0, round((x + m) * 255))))
            nol = min(255, (max(0, round(m * 255))))
            if 0 <= h < 60:
                arr[i * 3] = c
                arr[i * 3 + 1] = x
                arr[i * 3 + 2] = nol
            elif 60 <= h < 120:
                arr[i * 3] = x
                arr[i * 3 + 1] = c
                arr[i * 3 + 2] = nol
            elif 120 <= h < 180:
                arr[i * 3] = nol
                arr[i * 3 + 1] = c
                arr[i * 3 + 2] = x
            elif 180 <= h < 240:
                arr[i * 3] = nol
                arr[i * 3 + 1] = x
                arr[i * 3 + 2] = c
            elif 240 <= h < 300:
                arr[i * 3] = x
                arr[i * 3 + 1] = nol
                arr[i * 3 + 2] = c
            elif 300 <= h < 360:
                arr[i * 3] = c
                arr[i * 3 + 1] = nol
                arr[i * 3 + 2] = x


def hsv(arr, reverse=False):
    # print("hsv called, rev =", reverse)
    if not reverse:
        for i in range(len(arr) // 3):
            r, g, b = arr[i * 3]/255, arr[i * 3 + 1]/255, arr[i * 3 + 2]/255
            maxv = max(r, g, b)
            minv = min(r, g, b)
            delta = maxv - minv
            arr[i * 3 + 2] = int(maxv * 255)
            if delta == 0:
                arr[i * 3] = 0
            else:
                if maxv == r:
                    arr[i * 3] = max(0, min(255, round(42.618384401114 * (((g - b) / delta) % 6))))
                elif maxv == g:
                    arr[i * 3] = max(0, min(255, round(42.618384401114 * (((b - r) / delta) + 2))))
                elif maxv == b:
                    arr[i * 3] = max(0, min(255, round(42.618384401114 * (((r - g) / delta) + 4))))
            if maxv == 0:
                arr[i * 3 + 1] = 0
            else:
                arr[i * 3 + 1] = round(delta * 255 / maxv)
    else:
        for i in range(len(arr) // 3):
            h, s, v = arr[i * 3]/255*359, arr[i * 3 + 1]/255, arr[i * 3 + 2]/255
            c = v * s
            x = c * (1 - abs(((h / 60) % 2) - 1))
            m = v - c
            c = min(255, (max(0, round((c + m) * 255))))
            x = min(255, (max(0, round((x + m) * 255))))
            nol = min(255, (max(0, round(m * 255))))
            if 0 <= h < 60:
                arr[i * 3] = c
                arr[i * 3 + 1] = x
                arr[i * 3 + 2] = nol
            elif 60 <= h < 120:
                arr[i * 3] = x
                arr[i * 3 + 1] = c
                arr[i * 3 + 2] = nol
            elif 120 <= h < 180:
                arr[i * 3] = nol
                arr[i * 3 + 1] = c
                arr[i * 3 + 2] = x
            elif 180 <= h < 240:
                arr[i * 3] = nol
                arr[i * 3 + 1] = x
                arr[i * 3 + 2] = c
            elif 240 <= h < 300:
                arr[i * 3] = x
                arr[i * 3 + 1] = nol
                arr[i * 3 + 2] = c
            elif 300 <= h < 360:
                arr[i * 3] = c
                arr[i * 3 + 1] = nol
                arr[i * 3 + 2] = x


def ycbcr_six(arr, reverse=False):
    # print("ycbcr6 called, rev =", reverse)
    rc, gc, bc = 0.299, 0.587, 0.114
    if not reverse:
        cb_o, cb_t = rc / (1 - bc), gc / (1 - bc)
        cr_o, cr_t = gc / (1 - rc), bc / (1 - rc)
        for i in range(len(arr) // 3):
            r, g, b = arr[i * 3]/255, arr[i * 3 + 1]/255, arr[i * 3 + 2]/255
            arr[i * 3] = min(255, max(0, round(255 * ((rc * r) + (gc * g) + (bc * b)))))
            arr[i * 3 + 1] = min(255, max(0, round(255 * (0.5 + (-0.5) * (cb_o * r + cb_t * g - b)))))
            arr[i * 3 + 2] = min(255, max(0, round(255 * (0.5 + 0.5 * (r - (g * cr_o) - (b * cr_t))))))
    else:
        r_o = 2 - 2*rc
        g_o, g_t = (bc/gc) * (2-2*bc),  (rc/gc) * (2-2*rc)
        b_o = (2-2*bc)
        for i in range(len(arr) // 3):
            y, cb, cr = arr[i * 3]/255, arr[i * 3 + 1]/255-0.5, arr[i * 3 + 2]/255-0.5
            arr[i * 3] = int(255 * min(1, max(0, (y + r_o*cr))))
            arr[i * 3 + 1] = int(255 * min(1, max(0, (y - g_o*cb - g_t*cr))))
            arr[i * 3 + 2] = int(255 * min(1, max(0, (y + b_o*cb))))


def ycbcr_svn(arr, reverse=False):
    # print("ycbcr7 called, rev =", reverse)
    rc, gc, bc = 0.2126, 0.7152, 0.0722
    if not reverse:
        cb_o, cb_t = rc / (1 - bc), gc / (1 - bc)
        cr_o, cr_t = gc / (1 - rc), bc / (1 - rc)
        for i in range(len(arr) // 3):
            r, g, b = arr[i * 3] / 255, arr[i * 3 + 1] / 255, arr[i * 3 + 2] / 255
            arr[i * 3] = min(255, max(0, round(255 * ((rc * r) + (gc * g) + (bc * b)))))
            arr[i * 3 + 1] = min(255, max(0, round(255 * (0.5 + (-0.5) * (cb_o * r + cb_t * g - b)))))
            arr[i * 3 + 2] = min(255, max(0, round(255 * (0.5 + 0.5 * (r - (g * cr_o) - (b * cr_t))))))
    else:
        r_o = 2 - 2 * rc
        g_o, g_t = (bc / gc) * (2 - 2 * bc), (rc / gc) * (2 - 2 * rc)
        b_o = (2 - 2 * bc)
        for i in range(len(arr) // 3):
            y, cb, cr = arr[i * 3] / 255, arr[i * 3 + 1] / 255 - 0.5, arr[i * 3 + 2] / 255 - 0.5
            arr[i * 3] = min(255, max(0, round(255 * (y + r_o * cr))))
            arr[i * 3 + 1] = min(255, max(0, round(255 * (y - g_o * cb - g_t * cr))))
            arr[i * 3 + 2] = min(255, max(0, round(255 * (y + b_o * cb))))


def ycocg(arr, reverse=False):
    if not reverse:
        for i in range(len(arr) // 3):
            r, g, b = arr[i * 3] / 255, arr[i * 3 + 1] / 255, arr[i * 3 + 2] / 255
            y = 0.25 * r + 0.5 * g + 0.25 * b
            co = 0.5 * r - 0.5 * b
            cg = -0.25 * r + 0.5 * g - 0.25 * b
            y = min(255, max(0, round(y * 255)))
            co = min(255, max(0, round((co + 0.5) * 255)))
            cg = min(255, max(0, round((cg + 0.5) * 255)))
            arr[i * 3], arr[i * 3 + 1], arr[i * 3 + 2] = y, co, cg
    else:
        for i in range(len(arr) // 3):
            y, co, cg = arr[i * 3] / 255, arr[i * 3 + 1] / 255 - 0.5, arr[i * 3 + 2] / 255 - 0.5
            r = min(255, max(0, round((y + co - cg) * 255)))
            g = min(255, max(0, round((y + cg) * 255)))
            b = min(255, max(0, round((y - co - cg) * 255)))
            arr[i * 3], arr[i * 3 + 1], arr[i * 3 + 2] = r, g, b


def cmy(arr, reverse=False):
    for i in range(len(arr)):
        arr[i] = 255 - arr[i]


def menu(fr, to, inp, outp):
    # print("\nfrom:", fr, "\nto:", to, "\ninput pic:", inp, "\nouter pic:", outp)
    fncs = {"RGB": 228, "HSL": hsl, "HSV": hsv, "YCbCr.601": ycbcr_six,
            "YCbCr.709": ycbcr_svn, "YCoCg": ycocg, "CMY": cmy}
    if not (fr and to) in fncs.keys():
        print("Wrong color spaces. Exit.")
        exit(1)
    if not ((inp[0] == "1" and inp[1].endswith(".ppm")) or (inp[0] == "3" and inp[1].endswith(".pgm"))):
        print("Wrong extension of the input file. Exit.")
        exit(1)
    if not ((outp[0] == "1" and outp[1].endswith(".ppm")) or (outp[0] == "3" and outp[1].endswith(".pgm"))):
        print("Wrong extension of the output file. Exit.")
        exit(1)
    if inp[0] == "3":
        try:
            r_ch = open(inp[1][:-4] + "_1.pgm", "rb")
            g_ch = open(inp[1][:-4] + "_2.pgm", "rb")
            b_ch = open(inp[1][:-4] + "_3.pgm", "rb")
        except IOError:
            print("Cannot open file. Exit.")
            exit(1)
        pic, w, h = read_bw(r_ch, g_ch, b_ch)
        r_ch.close()
        g_ch.close()
        b_ch.close()

    elif inp[0] == "1":
        try:
            fl = open(inp[1], "rb")
        except IOError:
            print("Cannot open file. Exit.")
            exit(1)
        pic, w, h = read_clr(fl)
        fl.close()
    else:
        print("Wrong \"count\" value. Exit.")
        exit(1)

    if fr != "RGB":
        fncs[fr](pic, True)
    if to != "RGB":
        fncs[to](pic)

    if outp[0] == "1":
        write_clr(pic, outp[1], w, h)
    else:
        write_bw(pic, (outp[1][:-4] + "_1.pgm", outp[1][:-4] + "_2.pgm", outp[1][:-4] + "_3.pgm"), w, h)


params = ""
for k in argv:
    params = params + " " + k
# print("Программа запущена строкой:", params)
intest, outtest, fr_clr, to_clr = False, False, False, False
for i in params.split("-")[1:]:
    if i[0] == "f":
        fr_clr = i.split()[1]
    elif i[0] == "t":
        to_clr = i.split()[1]
    elif i[0] == "i":
        intest = i.split()[1:]
    elif i[0] == "o":
        outtest = i.split()[1:]
if intest and outtest and fr_clr and to_clr:
    menu(fr_clr, to_clr, intest, outtest)
else:
    print("Wrong input. Exit.")
    exit(1)

# menu("RGB", "HSV", "1 leaf.ppm", "1 out.ppm")
