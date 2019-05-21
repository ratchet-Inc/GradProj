import sys
import RekoBase
import RekoEngine

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

def main(args):
    result = "no response."
    args['-crds'] = args['-crds'].split(',')
    args['-reko'] = args['-reko'].split(',')
    if 'cf1' == args['-reko'][0].strip():
        uid = args['-reko'][1]
        result = RekoEngine.ContentFiltering(args['-crds'][0].strip(), args['-crds'][1].strip(), args['-reko'][1].strip())
    elif 'cf2' == args['-reko'][0].strip():
        uid = args['-reko'][1]
        result = RekoEngine.ContentFilteringScore(args['-crds'][0].strip(), args['-crds'][1].strip(), args['-reko'][1].strip())
        pass
    elif 'cf3' == args['-reko'][0].strip():
        uid = args['-reko'][1]
        result = RekoEngine.CollaborativeSimple(args['-crds'][0].strip(), args['-crds'][1].strip(), args['-reko'][1].strip())
        pass
    return result

if "__main__" == __name__:
    args = ParseArgs()
    res = main(args)
    print("\n\n*returned:", res)