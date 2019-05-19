import mysql.connector
import datetime
import random

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
    cur.execute("SELECT * FROM maincategories where userid = " + userid)
    result.update({"main":cur.fetchall()})
    cur.execute("SELECT * FROM subgenresratings where userid = " + userid)
    result.update({"genres":cur.fetchall()})
    cur.execute("SELECT * FROM ageratings where userid = " + userid)
    result.update({"ratings":cur.fetchall()})
    cur.execute("SELECT * FROM maincast where userid = " + userid)
    result.update({"cast":cur.fetchall()})
    cur.execute("SELECT * FROM users_ where userid = " + userid)
    result.update({"score":cur.fetchall()[0][7]})
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
            x = random.randint(0, len(year))
            if x not in found[c]:
                found[c].append(x)
                pass
            pass
        c += 1
        pass
    res = []
    for j in range(len(found)):
        for t in found[j]:
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