from sys import argv


def read_pic(pbmf):
    tp = pbmf.readline()
    (w, h) = [int(n) for n in pbmf.readline().split()]
    if tp == b'P6\n':
        rng = w*h*3
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
    return pic, w, h


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


def ycbcr(arr, reverse=False):
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


def set_rgb(pic, mv, mlp):					# 0 - ргб с заданными значениями
    # print("Set RGB called, move: {}, mltplr: {}".format(mv, mlp))
    for i in range(len(pic)):
        pic[i] = min(255, max(0, round((pic[i] - mv) * mlp)))


def set_ycbcr(pic, mv, mlp):				# 1 - усбср с заданными значениями
    # print("Set YCbCr called, move: {}, mltplr: {}".format(mv, mlp))
    ycbcr(pic)
    for i in range(len(pic) // 3):
        pic[i*3] = min(255, max(0, round((pic[i*3] - mv) * mlp)))
    ycbcr(pic, True)


def auto_rgb(pic):							# 2 -авто ргб
    mn, mx = min(pic), max(pic)
    if mn == mx:
        return
    mv = mn
    mlp = 255/(mx-mn)
    # print("\n\nAuto RGB, in:", mn, mx, "move:", mv, "mltplr:", mlp)
    set_rgb(pic, mv, mlp)


def auto_ycbcr(pic):						# 3 - авто усбср
    mn, mx = min(pic[::3]), max(pic[::3])
    if mn == mx:
        return
    mv = mn
    mlp = 255 / (mx - mn)
    # print("\n\nAuto YCbCr, in:", mn, mx, "move:", mv, "mltplr:", mlp)
    set_ycbcr(pic, mv, mlp)


def a_s_rgb(pic, pos):						# 4 - авто ргб с обрезанием крайних значений
    # print("[pos:", pos)
    tmp = sorted(pic)
    # print(tmp[:100])
    # print(tmp[-100:])
    mn, mx = tmp[pos], tmp[-pos]
    if mn == mx:
        return
    mv = mn
    mlp = 255 / (mx - mn)
    # print("\n\nAuto RGB, in:", mn, mx, "move:", mv, "mltplr:", mlp)
    set_rgb(pic, mv, mlp)


def auto_ycbcr_cut(pic, pos):				# 5 - авто усбср с обрезанием крайних значений
    tmp = sorted(pic[::3])
    mn, mx = tmp[pos], tmp[-pos]
    if mn == mx:
        return
    mv = mn
    mlp = 255 / (mx - mn)
    # print("\n\nAuto YCbCr, in:", mn, mx, "move:", mv, "mltplr:", mlp)
    set_ycbcr(pic, mv, mlp)


def menu(inp, outp, alg, mv=None, mlp=None):
    if inp.endswith(".pgm"):
        clr = False
    elif inp.endswith(".ppm"):
        clr = True
    else:
        print("Unsupported file extension. Exit.")
        exit(1)
    if alg not in (0, 1, 2, 3, 4, 5):
        print("Unsupported algorithm number. Exit.")
        exit(1)
    if alg in (0, 1):
        if not -255 <= mv <= 255:
            # Добавить проверку на наличие этих параметров и их числовой тип
            print("Unsupported bias parameter (out of range (-255, 255). Exit.")
            exit(1)
        if not 1/255 <= mlp <= 255:
            print("Unsupported multiplier parameter (out of range (1/255, 255). Exit.")
            exit(1)
    try:
        fl = open(inp, "rb")
    except IOError:
        print("Cannot open file. Exit.")
        exit(1)
    pic, w, h = read_pic(fl)
    fl.close()
    if alg == 0:
        set_rgb(pic, mv, mlp)
    elif alg == 1 and clr:
        set_ycbcr(pic, mv, mlp)
    elif alg == 2:
        auto_rgb(pic)
    elif alg == 3 and clr:
        auto_ycbcr(pic)
    elif alg == 4:
        a_s_rgb(pic, round(0.0039 * w * h * 3))
    elif alg == 5 and clr:
        auto_ycbcr_cut(pic, round(0.0039 * w * h))
    # print("res:", min(pic), max(pic))
    write_pic(pic, outp, clr, w, h)


params = argv[1:]
print(params)
inp, outp, alg = params[0], params[1], int(params[2])
print(inp, outp, alg)
if alg == 0 or alg == 1:
    mv, mlp = int(params[3]), float(params[4])
    print(mv, mlp)
else:
    mv, mlp = None, None
menu(inp, outp, alg, mv, mlp)

