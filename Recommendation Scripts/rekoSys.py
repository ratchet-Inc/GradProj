import sys
import mysql.connector

def CreateConnection(args):
    args['-crds'] = args['-crds'].split(',')
    db = mysql.connector.MySQLConnection(host="localhost", user=args['-crds'][0].strip(), passwd=args['-crds'][1].strip(), database="moviesdb")
    cursor = db.cursor()
    return db, cursor

def GetUserProfileData(cur, userid):
    result = {}
    cur.execute("SELECT * FROM maincategories where userid = " + userid)
    result.update({"main":cur.fetchall()})
    cur.execute("SELECT * FROM subgenresratings where userid = " + userid)
    result.update({"genres":cur.fetchall()})
    cur.execute("SELECT * FROM ageratings where userid = " + userid)
    result.update({"ratings":cur.fetchall()})
    cur.execute("SELECT * FROM maincast where userid = " + userid)
    result.update({"cast":cur.fetchall()})
    return result

def GetTitleData(cur, titleid):
    result = {}
    cur.execute("select * from titles where tconst_ = '" + titleid + "';")
    result.update({"title":cur.fetchall()})
    cur.execute("select * from principals where tconst_ = '" + titleid + "';")
    result.update({"principals":cur.fetchall()})
    cur.execute("select * from titlecrew where tconst_ = '" + titleid + "';")
    result.update({"crew":cur.fetchall()})
    return result

def LookupGenre(cur, genre):
    cur.execute("select * from subgenreslookup where subgenre = '" + genre + "';")
    res = cur.fetchall()
    return res[0][2]

def UpdatePrefs(cur, userData, movieData, rating):
    genre = movieData['title'][0][8].split(',')
    age = movieData['title'][0][4]
    cast = movieData['crew'][0][1].split(',')
    cast += movieData['crew'][0][2].split(',')
    for i in movieData['principals']:
        if i[2] not in cast:
            cast.append(i[2])
            pass
        pass
    l = []
    for g in genre:
        if '\\n' in genre:
            continue
        r = LookupGenre(cur, g)
        if r in l:
            continue
        l.append(r)
        pass
    updated = {'genres':list(userData['genres'][0])}
    for genre in l:
        print("genre:", genre)
        updated['genres'][genre] += rating
        pass
    updated.update({'ratings':list(userData['ratings'][0])})
    if age.strip() == 0:
        updated['ratings'][2] += rating
        pass
    else:
        updated['ratings'][1] += rating
        pass
    updated.update({'cast':list()})
    for p in cast:
        for l in userData['cast']:
            if p in l:
                i = i.index(p)
                updated['cast'].append[l[0], l[3] + 1]
                pass
            else:
                updated['cast'].append([-1, 1])
                pass
            pass
        pass
    updated.update({'main':list()})
    return updated

def mainF(args):
    conn, cur = CreateConnection(args)
    uid = args['-uid'].strip()
    res1 = GetUserProfileData(cur, uid)
    print(res1)
    tid = args['-tid'].strip()
    res2 = GetTitleData(cur, tid)
    update = UpdatePrefs(cur, res1, res2, 8)
    print(update)
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
    p = ParseArgs()
    r = mainF(p)
    print(r)