import sys
import mysql.connector
import numpy
import math

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
    ratingsData = {'g':[], "c":[], 'a':[updated['ratings'][1], updated['ratings'][2]]}
    skip = 0
    for i in updated['genres']:
        if skip == 0:
            skip += 1
            continue
        ratingsData['g'].append(i)
        pass
    temp = old['cast']
    for i in updated['cast']:
        for j in range(len(temp)):
            if i[0] == temp[j][0]:
                temp[j][3] += i[1]
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

def WriteToDB(conn, cur, data, uid):
    query = "UPDATE maincategories SET genrerating={}, agerating={}, maincast={} where userid={};"
    query = query.format(data['main'][0], data['main'][1], data['main'][2], uid)
    cur.execute(query)
    query = "UPDATE subgenresratings SET subgenre1={},subgenre2={},subgenre3={},subgenre4={},subgenre5={},subgenre6={},subgenre7={},subgenre8={},subgenre9={},subgenre10={},subgenre11={} where userid={};"
    query = query.format(data['genres'][1],data['genres'][2],data['genres'][3],data['genres'][4],data['genres'][5],data['genres'][6],data['genres'][7],data['genres'][8],data['genres'][9],data['genres'][10],data['genres'][11],uid)
    cur.execute(query)
    query = "UPDATE ageratings SET adultrating={},childrating={} where userid={};"
    query = query.format(data['ratings'][1], data['ratings'][2], uid)
    cur.execute(query)
    for i in data['cast']:
        if i[0] != -1:
            query = "UPDATE maincast SET freq={} where entry={};"
            query = query.format(i[2], i[0])
            pass
        else:
            query = "INSERT INTO maincast(userid, crewname, freq) values({}, '{}', {});"
            query = query.format(uid, i[1], i[2])
            pass
        print("query:", query)
        cur.execute(query)
        pass
    cur.execute(query)
    conn.commit()
    q = cur.rowcount
    print("query:", q)
    return 0

# Performs update calculations for recommendations
def UpdatePrefs(cur, userData, movieData, rating):
    # config for movie information
    genre = movieData['title'][0][8].split(',')
    age = movieData['title'][0][4]
    cast = movieData['crew'][0][1].split(',')
    cast += movieData['crew'][0][2].split(',')
    for i in movieData['principals']:
        if i[2] not in cast:
            cast.append(i[2])
            pass
        pass

    # adjusting genre data
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
        updated['genres'][genre] += rating
        pass

    # adjusting age rating data
    updated.update({'ratings':list(userData['ratings'][0])})
    if age == 0:
        updated['ratings'][2] += rating
        pass
    else:
        updated['ratings'][1] += rating
        pass

    # adjusting cast data
    updated.update({'cast':list()})
    for p in cast:
        if  len(userData['cast']) == 0:
            updated['cast'].append([-1, p, 1])
            pass
        for l in userData['cast']:
            if p in l:
                i = i.index(p)
                updated['cast'].append[l[0], l[3] + 1]
                pass
            else:
                updated['cast'].append([-1, p, 1])
                pass
            pass
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
    print(res1)
    tid = args['-tid'].strip()
    res2 = GetTitleData(cur, tid)
    update = UpdatePrefs(cur, res1, res2, 8)
    print("%s\n" % update)
    WriteToDB(conn, cur, update, uid)
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