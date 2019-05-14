import sys

CONST_FNAME = 'first'
CONST_LNAME = 'last'
CONST_GENRELIST = {'history':0, 'biography':0, 'musical':0, 'music':0, 'documentary':0, 'fantasy':0, 'animation':0, 'adventure':0, 'mystery':0, 'drama':0, 'crime':0, 'thriller':0, 'action':0, 'romance':0, 'horror':0, 'sci-fi':0, 'comedy':0}

def FilterRead(ptr):
    line = ptr.readline()
    return line

def mainFunc(args):
    print("**User accounts faker script running...\n")
    if not args.get('-tf'):
        print('No target file set. Please set the -tf flag')
        return -1
    args['-tf'] = args['-tf'].split(',')
    filePtr = open(args['-tf'][0].strip(), 'rb')
    genres = CONST_GENRELIST
    l = []
    line = FilterRead(filePtr)
    while len(line) > 1:
        data = line.decode().strip().split(",")
        #print("line:", line)
        #print("data:", data)
        index = int(args['-tf'][1].strip())
        index = len(data) - 1
        temp = data[index].strip().replace("'", '')
        #print("t:", temp)
        if temp.lower() not in genres:
            genres.update({temp.lower():0})
            pass
        line = FilterRead(filePtr)
        pass
    print("genres:\n", genres)
    print("length: %d" % len(genres))
    return 0
    if not args.get('-urs'):
        print('No limitation set to the amount of users. Please set the -urs flag')
        return -1
    userLimit = args['-urs']
    for i in range(userLimit):
        pass
    return 0

def ParseArgs():
    args = {}
    if len(sys.argv) > 1:
        curKey = ''
        for i in range(len(sys.argv)):
            if '-' in sys.argv[i]:
                curKey = sys.argv[i]
                args.update({curKey: ''})
                pass
            else:
                if curKey != '':
                    args[curKey] += sys.argv[i]+' '
                    pass
                pass
            pass
        pass
    return args

if "__main__" == __name__:
    args = ParseArgs()
    res = mainFunc(args)
    print(res)