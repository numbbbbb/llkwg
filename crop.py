def init():
    #curpath = sys.path[0][0:-12]
    curpath = sys.path[0]
    standardpath = os.path.join(curpath,'standard/')
    for files in os.listdir(standardpath):
        tempxx = Image.open(os.path.join(standardpath,files)).crop((0,0,27,15))
        tempxx.save(standardpath+'half'+files,"JPEG")