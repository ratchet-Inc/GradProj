import mysql.connector
import datetime
import random
import math

def ConnectToDatabase(dbuser, dbpass):
    db = mysql.connector.MySQLConnection(host="localhost", user=dbuser, passwd=dbpass, database="moviesdb")
    cursor = db.cursor()
    return db, cursor

def CloseDatabase(conn):
    conn.commit()
    conn.close()
    return 0

def GetUserProfileData(cur, userid):
    result = {}
    cur.execute("SELECT * FROM maincategories where userid = " + str(userid))
    result.update({"main":cur.fetchall()})
    cur.execute("SELECT * FROM subgenresratings where userid = " + str(userid))
    result.update({"genres":cur.fetchall()})
    cur.execute("SELECT * FROM ageratings where userid = " + str(userid))
    result.update({"ratings":cur.fetchall()})
    cur.execute("SELECT * FROM maincast where userid = " + str(userid))
    result.update({"cast":cur.fetchall()})
    cur.execute("SELECT scoresum, scoredenom FROM users_ where userid = " + str(userid))
    result.update({"score":cur.fetchall()[0]})
    return result

def GetTitleData(cur, titleid):
    result = {}
    cur.execute("select * from titles where tconst_ = '" + titleid + "';")
    result.update({"title":cur.fetchall()})
    #cur.execute("select * from principals where tconst_ = '" + titleid + "';")
    #result.update({"principals":cur.fetchall()})
    result.update({"principals":[]})
    cur.execute("select * from titlecrew where tconst_ = '" + titleid + "';")
    result.update({"crew":cur.fetchall()})
    return result

def GetTitleYear(cur, tid):
    q = "SELECT * FROM titles WHERE tconst_ = '{}';"
    cur.execute(q.format(tid))
    r = cur.fetchall()
    return r[0][5]

def GetWatchedYears(cur, userid):
    q = "SELECT * FROM watched WHERE userid={};"
    cur.execute(q.format(userid))
    res = cur.fetchall()
    if len(res) == 0:
        res = datetime.datetime.now().year
        res = [res-10, res]
        pass
    elif len(res) == 1:
        res = datetime.datetime.now().year
        res = [res-5, res+5]
        pass
    else:
        mov1 = GetTitleYear(cur, res[len(res)-1][2])
        mov2 = GetTitleYear(cur, res[len(res)-2][2])
        x = (mov1+mov2)//2
        res = [x-5, x+5]
        pass
    return res

def GetTitlesForCF(cur, years):
    tres = []
    for i in range(years[0], years[1] + 1):
        q = "SELECT tconst_ FROM titles WHERE startyear_ = '{}';"
        cur.execute(q.format(i))
        tres.append(cur.fetchall())
        pass
    found = []
    c = 0
    for year in tres:
        found.append([])
        for i in range(10):
            x = random.randint(0, len(year)-1)
            if x not in found[c]:
                found[c].append(x)
                pass
            pass
        c += 1
        pass
    res = []
    for j in range(len(found)):
        for t in found[j]:
            #print("[%s][%s]" % (j, t))
            res.append(tres[j][t][0].strip())
            pass
        pass
    return res

def CreateFilterData(movieData):
    r = {'g':None, 'a':None, 'c':None}
    castL = []
    for i in movieData['principals']:
        if i[2] not in castL:
            castL.append(i[2])
            pass
        pass
    if len(movieData['crew']) > 0:
        temp = movieData['crew'][0][1].split(',')
        for i in temp:
            if i not in castL:
                castL.append(i)
                pass
            pass
        temp = movieData['crew'][0][2].split(',')
        for i in temp:
            if i not in castL:
                castL.append(i)
                pass
            pass
        pass
    r['c'] = castL
    r['a'] = movieData['title'][0][4]
    r['g'] = movieData['title'][0][8].split(',')
    return r

def LookupGenre(cur, data):
    res = []
    if '-1' in data:
        return res
    for i in data:
        q = "SELECT referenceid FROM subgenreslookup WHERE subgenre='{}';"
        cur.execute(q.format(i.strip()))
        r = cur.fetchall()
        if len(r) == 0:
            continue
        res.append(r[0][0])
        pass
    return res

def LookupAgeRatings(cur, data):
    if data.strip() == '1':
        return 3
    q = "SELECT ratingid FROM ratingslookup WHERE rating='{}';"
    cur.execute(q.format(data.strip()))
    r = cur.fetchall()
    return r[0][0]

def GetTotalUserScores(data):
    g = 0
    a = 0
    c = 0
    t = 0
    for i in range(1, len(data['genres'][0])):
        g += data['genres'][0][i]
        pass
    for i in range(1, len(data['ratings'][0])):
        a += data['ratings'][0][i]
        pass
    for i in range(1, len(data['main'][0])):
        t += data['main'][0][i]
        pass
    for i in data['cast']:
        c += i[3]
        pass
    return g, a, c, t

def GetUserRecentWatchedList(cur, uid, lim):
    q = "SELECT * FROM watched WHERE userid={} ORDER BY entry DESC LIMIT {};"
    q = q.format(uid, lim)
    cur.execute(q)
    r = cur.fetchall()
    return r

def FilterID_Key(users, baseScore):
    for i in range(len(users)-1):
        for j in range(i+1, len(users)):
            s1 = users[i][1]+users[i][2]
            diff1 = baseScore - s1
            diff1 = diff1 * diff1
            s2 = users[j][1]+users[j][2]
            diff2 = baseScore - s2
            diff2 = diff2 * diff2
            if diff1 < diff2:
                users[j], users[i] = users[i], users[j]
                pass
            pass
        pass
    return users

def FilterID_Key2(users, baseScore):
    for i in range(len(users)-1):
        for j in range(i+1, len(users)):
            s1 = users[i][1]
            diff1 = baseScore - s1
            diff1 = diff1 * diff1
            s2 = users[j][1]
            diff2 = baseScore - s2
            diff2 = diff2 * diff2
            if diff1 < diff2:
                users[j], users[i] = users[i], users[j]
                pass
            pass
        pass
    return users

def GetUsersForCF(cur, userData):
    bestg = [-1, 0]
    for i in range(len(userData['genres'][0])):
        if bestg[1] <= userData['genres'][0][i]:
            bestg = [i, userData['genres'][0][i]]
            pass
        pass
    besta = [-1, 0]
    for i in range(len(userData['ratings'][0])):
        if besta[1] <= userData['ratings'][0][i]:
            besta = [i, userData['ratings'][0][i]]
            pass
        pass
    diff1 = math.ceil((bestg[1]/100) * 12.5)
    diff2 = math.ceil((besta[1]/100) * 12.5)
    offset = random.randint(0, 989)
    q = "SELECT userid, {} FROM subgenresratings WHERE {} >= {} AND {} <= {} LIMIT {},10;"
    q = q.format("subgenre"+str(bestg[0]), "subgenre"+str(bestg[0]), bestg[1]-diff1, "subgenre"+str(bestg[0]), bestg[1]+diff1, offset)
    #print(q)
    cur.execute(q)
    res1 = cur.fetchall()
    #res1.sort(key = FilterID_Key, reverse = True)
    res1 = FilterID_Key2(res1, bestg[1])
    #print(res1)
    q = "SELECT userid, {} FROM ageratings WHERE {} >= {} AND {} <= {} LIMIT {},10;"
    q = q.format("rating"+str(besta[0]), "rating"+str(besta[0]), besta[1]-diff2, "rating"+str(besta[0]), besta[1]+diff2, offset)
    #print(q)
    cur.execute(q)
    res2 = cur.fetchall()
    #res2.sort(key = FilterID_Key, reverse = True)
    res2 = FilterID_Key2(res2, besta[1])
    #print(res2)
    res = []
    for i in range(len(res1)):
        if len(res) != 0 and len(res) % 5 == 0:
            break
        if res1[i][0] not in res:
            res.append(res1[i][0])
            pass
        pass
    for i in range(len(res2)):
        if len(res) != 0 and len(res) % 10 == 0:
            break
        if res2[i][0] not in res:
            res.append(res2[i][0])
            pass
        pass
    return res

def GenerateCF_Table(cur, users, lim=10):
    watchedData = {}
    for i in range(len(users)):
        movies = GetUserRecentWatchedList(cur, users[i], lim)
        watchedData.update({users[i]:movies})
        pass
    uniqMovies = []
    moviesKey = {}
    for k, v in watchedData.items():
        for entry in v:
            if entry[2] not in uniqMovies:
                uniqMovies.append(entry[2])
                moviesKey.update({entry[2]:len(uniqMovies)-1})
                pass
            else:
                print("not unique")
            pass
        pass
    #print("unique:", uniqMovies)
    table = [[0 for j in range(len(uniqMovies))] for i in range(len(users))]
    for i in range(len(users)):
        for entry in watchedData[users[i]]:
            table[i][moviesKey[entry[2]]] += entry[3]
            pass
        pass
    #print(table)
    return table, uniqMovies

def CF_FilterKey(data):
    return data[0]

def MF_FilterKey1(data):
    return data[0]

def CFUserSort(users, base):
    baseScore = base
    for i in range(len(users)-1):
        for j in range(i+1, len(users)):
            s1 = users[i][1]+users[i][2]
            diff1 = baseScore - s1
            diff1 = diff1 * diff1
            s2 = users[j][1]+users[j][2]
            diff2 = baseScore - s2
            diff2 = diff2 * diff2
            if diff1 < diff2:
                users[j], users[i] = users[i], users[j]
                pass
            pass
        pass
    return users

def GetUsersForMF(cur, userData):
    bestm = list(userData['main'][0])
    uid = userData['main'][0][0]
    l = ['', 'genrerating', 'agerating', 'maincast']
    for i in range(len(bestm)):
        bestm[i] = [bestm[i], i, l[i]]
        pass
    bestm.sort(key = MF_FilterKey1, reverse = True)
    #print(bestm)
    diff1 = math.ceil((bestm[0][0]/100) * 5)
    diff2 = math.ceil((bestm[1][0]/100) * 5)
    offset = random.randint(0, 990)
    offset = 0
    prefUsers = GetUsersForMF_Helper(cur, uid)
    res1 = []
    for u in prefUsers:
        q = "SELECT * FROM maincategories WHERE userid = {};"
        q = q.format(u)
        cur.execute(q)
        res1 += cur.fetchall()
        pass
    #print(res1)
    res1 = CFUserSort(res1, userData['main'][0][bestm[0][1]] + userData['main'][0][bestm[1][1]])
    #print(res1)
    res = []
    for i in range(len(res1)):
        if len(res) != 0 and len(res) % 5 == 0:
            break
        if res1[i][0] not in res:
            res.append(res1[i][0])
            pass
        pass
    #print(res)
    return res

def GetUsersForMF_Helper(cur, uid):
    watchedL = GetUserRecentWatchedList(cur, uid, 10)
    userids = []
    for m in watchedL:
        q = "select * from watched where title = '{}';"
        cur.execute(q.format(m[2]))
        r = cur.fetchall()
        for i in range(1, len(r)):
            if r[i][1] not in userids:
                userids.append(r[i][1])
                pass
            pass
        pass
    return userids

def WriteToDB(conn, cur, uid, data, col):
    s = ""
    for m in range(len(data)):
        s += str(data[m])
        if m != len(data) - 1:
            s += "||"
            pass
        pass
    s = s.replace(" ", '')
    #print(s)
    q = "select * from rekomovies where userid = {};"
    q = q.format(uid)
    cur.execute(q)
    r = cur.fetchall()
    print()
    if len(r) == 0:
        q = 'insert into rekomovies(userid, {}) values({}, "{}");'
        q = q.format(col, uid, s)
    else:
        q = 'update rekomovies set {}="{}" where userid={};'
        q = q.format(col, s, uid)
        pass
    print(q)
    cur.execute(q)
    conn.commit()
    return 0