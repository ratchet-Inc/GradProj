import sys
import mysql.connector
import numpy
import math
import RekoBase

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

# Creates a list of numbers for standard deviation calculation
def CreateValueList(updated, old):
    ratingsData = {'g':[], "c":[], 'a':[updated['ratings'][1], updated['ratings'][2], updated['ratings'][3]]}
    skip = 0
    for i in updated['genres']:
        if skip == 0:
            skip += 1
            continue
        ratingsData['g'].append(i)
        pass
    temp = []
    for i in old['cast']:
        temp.append(list(i))
        pass
    for i in updated['cast']:
        for j in range(len(old['cast'])):
            if i[0] == old['cast'][j][0]:
                temp[j][3] += i[len(i) - 1]
                pass
            pass
        pass
    for i in temp:
        ratingsData['c'].append(i[len(i)-1])
        pass
    for i in updated['cast']:
        if i[0] == -1:
            ratingsData['c'].append(i[2])
            pass
        pass
    for k in ratingsData.keys():
        if len(ratingsData[k]) == 0:
            ratingsData[k] = [0]
            pass
        pass

    return ratingsData

def CheckRekoStatus(cur, uid, tid):
    q = "SELECT * FROM rekomovies WHERE userid = {};"
    cur.execute(q.format(uid))
    res = cur.fetchall()
    if len(res) == 0:
        return False
    for i in range(1, len(res[0]) + 1):
        if tid in res[i].split('||'):
            return True
        pass
    return False

def WriteToDB(conn, cur, data, uid, tid, rating):
    query = "UPDATE maincategories SET genrerating={}, agerating={}, maincast={} where userid={};"
    query = query.format(data['main'][0], data['main'][1], data['main'][2], uid)
    cur.execute(query)
    query = "UPDATE subgenresratings SET subgenre1={},subgenre2={},subgenre3={},subgenre4={},subgenre5={},subgenre6={},subgenre7={},subgenre8={},subgenre9={},subgenre10={},subgenre11={} where userid={};"
    query = query.format(data['genres'][1],data['genres'][2],data['genres'][3],data['genres'][4],data['genres'][5],data['genres'][6],data['genres'][7],data['genres'][8],data['genres'][9],data['genres'][10],data['genres'][11],uid)
    cur.execute(query)
    query = "UPDATE ageratings SET rating1={},rating2={}, rating3={} where userid={};"
    query = query.format(data['ratings'][1], data['ratings'][2], data['ratings'][3], uid)
    cur.execute(query)
    for i in data['cast']:
        if i[0] != -1:
            query = "UPDATE maincast SET freq={} where entry={};"
            query = query.format(i[1], i[0])
            pass
        else:
            query = "INSERT INTO maincast(userid, crewname, freq) values({}, '{}', {});"
            query = query.format(uid, i[1], i[2])
            pass
        cur.execute(query)
        pass
    cur.execute(query)

    # updating watched list
    query = "SELECT * FROM watched WHERE userid = {};"
    cur.execute(query.format(uid))
    r = cur.fetchall()
    id = -1
    for i in r:
        if i[2] == tid:
            id = i[0]
            break
        pass
    if id == -1:
        query = "INSERT INTO watched(userid, title, rating) values({}, '{}', {});"
        query = query.format(uid, tid, rating)
    else:
        query = "UPDATE watched SET rating={} WHERE entry={};"
        query = query.format(rating, id)
        pass
    cur.execute(query)

    # updating reko score info
    if CheckRekoStatus(cur, uid, tid):
        q = "SELECT scoresum, scoredenom FROM users_ WHERE userid={};"
        cur.execute(q.format(uid))
        r = cur.fetchall()
        sum_ = [int(r[0][0])+rating, int(r[0][1])+1]
        q = "UPDATE users_ SET scoresum={}, scoredenom={} WHERE userid={};"
        cur.execute(q.format(sum_[0], sum_[1], uid))
        pass
    conn.commit()
    return 0

# Performs update calculations for recommendations
def UpdatePrefs(cur, userData, movieData, rating):
    # config for movie information
    genre = movieData['title'][0][8]
    if genre == '-1':
        genre = []
    else:
        genre = genre.split(',')
        pass
    age = RekoBase.LookupAgeRatings(cur, movieData['title'][0][4])
    cast = []
    if len(movieData['crew']) != 0:
        cast = movieData['crew'][0][1].split(',')
        pass
    t = []
    if len(movieData['crew']) != 0:
        t = movieData['crew'][0][2].split(',')
        pass
    for i in t:
        if i not in cast:
            cast.append(i)
        pass

    # adjusting genre data
    l = []
    l = RekoBase.LookupGenre(cur, genre)
    updated = {'genres':list(userData['genres'][0])}
    for genre in l:
        updated['genres'][genre] += rating
        pass

    # adjusting age rating data
    updated.update({'ratings':list(userData['ratings'][0])})
    updated['ratings'][age] += rating

    # adjusting cast data
    updated.update({'cast':list()})
    for p in cast:
        if len(userData['cast']) == 0:
            updated['cast'].append([-1, p, 1])
            pass
        f = [-1, p, 1]
        for i in range(len(userData['cast'])):
            if p == userData['cast'][i][2]:
                f = [userData['cast'][i][0], userData['cast'][i][3] + 1]
                break
            pass
        updated['cast'].append(f)
        pass

    # updating the primary recommendation category values
    updated.update({'main':list()})
    dataDict = CreateValueList(updated, userData)
    res = math.floor(numpy.std(dataDict['g']))
    updated['main'].append(userData['main'][0][1] + res)
    res = math.floor(numpy.std(dataDict['a']))
    updated['main'].append(userData['main'][0][2] + res)
    res = math.floor(numpy.std(dataDict['c']))
    updated['main'].append(userData['main'][0][3] + res)
    return updated

def mainF(args):
    conn, cur = CreateConnection(args)
    uid = args['-uid'].strip()
    res1 = GetUserProfileData(cur, uid)
    #print(res1)
    tid = args['-tid'].strip()
    res2 = GetTitleData(cur, tid)
    #print("\n", res2)
    rating = int(args['-rtng'])
    update = UpdatePrefs(cur, res1, res2, rating)
    #print("%s\n" % update)
    WriteToDB(conn, cur, update, uid, tid, rating)
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