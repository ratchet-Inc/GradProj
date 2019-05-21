import sys
import random
import rekoSys

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

def func(args):
    fn = args['-tf'].strip()
    fptr = open(fn, "rb")
    lines = fptr.readlines()
    loop = int(args['-lim'].strip())
    users = int(args['-usrs'].strip())
    for i in range(1, users+1):
        for j in range(loop):
            index = random.randint(0, len(lines) - 1)
            tid = lines[index].decode().split("||")[0]
            rt = random.randint(6, 10)
            print("injecting:", tid)
            a = {'-crds':"reko, comp3901", '-uid':str(i), '-tid':tid, '-rtng':rt}
            rekoSys.mainF(a)
            pass
        pass
    return 0

if "__main__" == __name__:
    a = ParseArgs()
    res = func(a)
    print("returned:", res)