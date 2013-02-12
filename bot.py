import itertools, operator, time, sys, threading
import ctypes, win32con, ctypes.wintypes, win32gui
import autopy, Image, ImageGrab

L, T = 234, 167
EXIT = False

class Menu:
    def __init__(self):
        self.stuff_pos = []
        self.recipes = [None] * 8
        self.init_stuff()
        self.init_recipe()
        pass

    def init_stuff(self):
        for i in range(9):
            self.stuff_pos.append( (L + 102 + (i % 3) * 42, T + 303 + (i / 3) * 42) )

    def init_recipe(self):
        self.recipes[0] = (1, 2)
        self.recipes[1] = (0, 1, 2)
        self.recipes[2] = (5, 1, 2)
        self.recipes[3] = (3, 0, 1, 2)
        self.recipes[4] = (4, 1, 2)
        self.recipes[5] = (7, 1, 2)
        self.recipes[6] = (6, 1, 2)
        self.recipes[7] = (8, 1, 2)
        

    def click(self, i):
        autopy.mouse.move(self.stuff_pos[i][0] + 20, self.stuff_pos[i][1] + 20)
        autopy.mouse.click()

    def make(self, i):
        for x in self.recipes[i]:
            self.click(x)
        autopy.mouse.move(L + 315, T + 363)
        autopy.mouse.click()

class Custom:
    def __init__(self):
        self.menu = Menu()
        self.left = L + 47
        self.top = T + 53
        self.width = 53;
        self.height = 39
        self.step = 126
        self.bottom = T + 243
        self.maps = [None] * 12
        for i in xrange(12):
            try:
                self.maps[i] = self.get_hash(Image.open(str(i) + ".png"))
            except IOError:
                pass
            #print "Inited", i, "as", self.maps[i]

    def order(self, i):
        l, t = self.left + i * self.step, self.top
        r, b = l + self.width, t + self.height
        hash2 = self.get_hash(ImageGrab.grab((l, t, r, b)))
        (mi, dist) = None, 50
        for i, hash1 in enumerate(self.maps):
            if hash1 is None:
                continue
            this_dist = self.hamming_dist(hash1, hash2)
            if this_dist < dist:
                mi = i
                dist = this_dist
        return mi

    def serve1(self, i, mi):
        self.menu.make(mi)
        time.sleep(0.5)
        autopy.mouse.move(L + 315, T + 363)
        autopy.mouse.toggle(True)
        time.sleep(0.2)
        autopy.mouse.smooth_move(self.left + self.step * i + 40, self.bottom)
        time.sleep(0.2)
        autopy.mouse.toggle(False)

    def serve2(self, i, mi):
        if mi == 10:
            autopy.mouse.move(L + 488, T + 410)
        elif mi == 9:
            autopy.mouse.move(L + 488, T + 360)
        elif mi == 8:
            autopy.mouse.move(L + 488, T + 320)
        else:
            autopy.mouse.move(L + 563, T + 320)
        autopy.mouse.toggle(True)
        time.sleep(0.2)
        autopy.mouse.smooth_move(self.left + self.step * i + 30, self.bottom)
        time.sleep(0.2)
        autopy.mouse.toggle(False)

    def get_hash(self, img):
        image = img.resize((18, 13), Image.ANTIALIAS).convert("L")
        pixels = list(image.getdata())
        avg = sum(pixels) / len(pixels)
        return "".join(map(lambda p : "1" if p > avg else "0", pixels))

    def hamming_dist(self, hash1, hash2):
        return sum(itertools.imap(operator.ne, hash1, hash2))

class Hotkey(threading.Thread):

    def run(self):
        global EXIT
        user32 = ctypes.windll.user32
        print "Register exit hotkey"
        if not user32.RegisterHotKey(None, 99, win32con.MOD_WIN, win32con.VK_F3):
            raise RuntimeError
        try:
            msg = ctypes.wintypes.MSG()
            print msg
            while user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
                if msg.message == win32con.WM_HOTKEY:
                    if msg.wParam == 99:
                        EXIT = True
                        return
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageA(ctypes.byref(msg))
        finally:
            user32.UnregisterHotKey(None, 1)

def TopmostMe():
    hwnd = win32gui.GetForegroundWindow()
    (left, top, right, bottom) = win32gui.GetWindowRect(hwnd)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, left, top, right-left, bottom-top, 0)

def run():
    TopmostMe()
    hotkey = Hotkey()
    hotkey.start()

    custom = Custom()
    while True:
        for i in xrange(4):
            if EXIT:
                sys.exit()
            m = custom.order(i)
            if m is not None:
                if m < 8:
                    custom.serve1(i, m)
                else:
                    custom.serve2(i, m)
        time.sleep(1)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        run()
    else:
        custom = Custom()
        hash2 = custom.get_hash(Image.open(sys.argv[1]))
        print "***", hash2
        for i, h in enumerate(custom.maps):
            if h is None: continue
            print "%2d: %s" % (i, h)
            print "==>", custom.hamming_dist(h, hash2)


