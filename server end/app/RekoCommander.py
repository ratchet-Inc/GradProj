import subprocess

def RunCommand(cmd, uid, tid='', rt=0):
    cmds = {'1':'cf1', '2':'cf2', '3':'cf3', '4':'mf1', '5':'add'}
    s = "py -3 ./app/Engine/RekoAPI.py -crds reko, comp3901 -reko {}, {}"
    s = s.format(cmds[cmd], uid)
    if cmd == '5':
        s1 = ", {}, {}"
        s1 = s1.format(tid, rt)
        s += s1
        pass
    print "running cmd:", s
    r = subprocess.call(s, shell=True)
    return r