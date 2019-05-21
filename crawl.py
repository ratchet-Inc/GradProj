import urllib2

def func(title):
    try:
        contents = urllib2.urlopen("https://www.imdb.com/title/"+title+"/mediaviewer/").read()
    except:
        return ""
    #print(contents)
    r1 = contents.rfind('"msrc":"')
    print("position0:", r1)
    r1 = contents.find('"src":"', r1)
    print("position1:", r1)
    r2 = contents.find('",', r1)
    print("position2:", r2)
    s = contents[r1+7:r2]
    print("substring:", s)

    return s

if "__main__" == __name__:
    func()
    print("done.")