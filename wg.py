#coding:UTF-8
import itertools, operator, time, sys, threading,os
import ctypes, win32con, ctypes.wintypes, win32gui
import autopy, Image, ImageGrab
import random

L, T = 5, 28
fx, fy = L+11, T+155
EXIT = False
START = False
standard = {}
matches = {}
finishgrab = 0
startclick = False
notmatch = True
lastnumb = -1
sleepnumb = 0.8
dingwei = []

class Hotkey(threading.Thread):
 
    def run(self):
        global EXIT
        global START
        user32 = ctypes.windll.user32
        if not user32.RegisterHotKey(None, 99, win32con.MOD_WIN, win32con.VK_F7):
            raise RuntimeError
        if not user32.RegisterHotKey(None, 98, win32con.MOD_WIN, win32con.VK_F3):
            raise RuntimeError
        try:
            msg = ctypes.wintypes.MSG()
            while user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
                if msg.message == win32con.WM_HOTKEY:
                    if msg.wParam == 99:
                        START = False
                        print 
                        print "================================"
                        print "          stop grab"
                        print "================================"
                    if msg.wParam == 98:
                        START = True
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageA(ctypes.byref(msg))
        finally:
            user32.UnregisterHotKey(None, 1)
	
def get_hash(img):
    image = img.resize((13, 15), Image.ANTIALIAS).convert("L")
    pixels = list(image.getdata())
    avg = sum(pixels) / len(pixels)
    return "".join(map(lambda p : "1" if p > avg else "0", pixels))
	
def hamming_dist(hash1, hash2):
    return sum(itertools.imap(operator.ne, hash1, hash2))
    
def clickit(point):
    autopy.mouse.move(fx+point[1]*31+15,fy+point[0]*35+13)
    autopy.mouse.click()
    
def weathergamestart():
    global dingwei
    img=ImageGrab.grab((8,0,26,31))
    if hamming_dist(get_hash(img),dingwei)>2:
        return 0
    else:
        return 1
    
def init():
    global dingwei
  #  curpath = sys.path[0][0:-12]
    curpath = sys.path[0]
    standardpath = os.path.join(curpath,'standard/')
    dingwei = get_hash(Image.open(os.path.join(standardpath,"dingwei.png")))
    for files in os.listdir(standardpath):
        standard[files[:-4]] = get_hash(Image.open(os.path.join(standardpath,files)))
        matches[files[:-4]] = []

def run():
    print 
    print "================================"
    print "  click your game window"
    print "      then :"
    print "      press win+F3 to start"
    print "      press win+F7 to pause"
    print "================================"
    global finishgrab,standard,notmatch,startclick,START,EXIT,matches,L,T,fx,fy,lastnumb,sleepnumb
    init()
    hotkey = Hotkey()
    hotkey.start()
    while True:
        if START and notmatch:
            sleepnumb = 1.2
            try:
                hwnd = win32gui.GetForegroundWindow()
                (left, top, right, bottom) = win32gui.GetWindowRect(hwnd)
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, right-left, bottom-top, 0)
            except:
                pass
            if weathergamestart() == 0:
                continue
            notmatch = True
            print "start grab"
            img=ImageGrab.grab((fx,fy,fx+585,fy+381))
            for i in range(11):
                for j in range(19):
                    img1=img.crop((j*31,i*35,j*31+13,i*35+15))
                    max1 = 500
                    now = 0.0
                    hashimg1 = get_hash(img1)
                    for comp in standard.keys():
                        now = hamming_dist(hashimg1,standard[comp])
                        if now<max1:
                            max1 = now
                            maxnow = comp
                    if max1<50:
                        notmatch = False
                        matches[maxnow].append((i,j))
                        print "find a %s "%(maxnow)+"in %s-%s"%(i,j)
            print "finish grab"
            finishgrab = True
            startclick = True
        if finishgrab<8 and not notmatch:
            (pointx,pointy) = win32gui.GetCursorPos()
            print "start click"
            for tempi in range(4):
                for finishgrab in range(0,20):
                    for i in matches.keys():
                        if matches[i] != []:
                            for j in range(0,len(matches[i])):
                                clickit(matches[i][j])
                            if finishgrab%2 == 0:
                                temp = matches[i].pop(0)
                                matches[i].append(temp)
                            else:
                                matches[i].reverse()   
            print "finish click"
            autopy.mouse.move(pointx,pointy)
            time.sleep(sleepnumb)
            finishgrab = 0
            notmatch = True
            for tempi in matches.keys():
                matches[tempi] = []
            startclick = False
       
if __name__ == "__main__":
    try:
        hwnd = win32gui.GetForegroundWindow()
        (left, top, right, bottom) = win32gui.GetWindowRect(hwnd)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 800, 0, right-left, bottom-top, 0)
        if len(sys.argv) == 1:
            run()
        else:
            L = int(sys.argv[1])
            T = int(sys.argv[2])
            fx = L+11
            fy = T+155
            run()
    except IOError,e:
        print e
        xx = input("there is something wrong...")