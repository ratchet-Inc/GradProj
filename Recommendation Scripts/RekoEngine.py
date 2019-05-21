import RekoBase
import datetime
import decimal

def FilterKey(data):
    return data['m']

def ContentFiltering(dbuser, dbpass, uid):
    conn, cur = RekoBase.ConnectToDatabase(dbuser, dbpass)
    userData = RekoBase.GetUserProfileData(cur, uid)
    print(userData)
    targetYears = RekoBase.GetWatchedYears(cur, uid)
    print(targetYears)
    movies = RekoBase.GetTitlesForCF(cur, targetYears)
    scores = []
    for m in movies:
        data = RekoBase.GetTitleData(cur, m)
        print(data)
        data = RekoBase.CreateFilterData(data)
        #print(data)
        genreInfo = RekoBase.LookupGenre(cur, data['g'])
        #print(genreInfo)
        ratingInfo = RekoBase.LookupAgeRatings(cur, data['a'])
        #print(ratingInfo)
        gscore = decimal.Decimal(0)
        cscore = decimal.Decimal(0)
        ascore = decimal.Decimal(0)
        for g in genreInfo:
            gscore += userData['genres'][0][g]
            pass
        ascore += userData['ratings'][0][ratingInfo]
        for c in userData['cast']:
            if c[2] in data['c']:
                cscore += c[3]
                pass
            pass
        #print("genre score:", gscore)
        #print("rating score:", ascore)
        #print("cast score:", cscore)
        genreT, ratingT, castT, catT = RekoBase.GetTotalUserScores(userData)
        #print("gt = %s | rt = %s | ct = %s" % (genreT, ratingT, castT))
        if castT != 0 and cscore != 0:
            gscore = (gscore / genreT) * 100
            pass
        #print("genre perc:", gscore)
        if castT != 0 and cscore != 0:
            ascore = (ascore / ratingT) * 100
            pass
        #print("rating perc:", ascore)
        if castT != 0 and cscore != 0:
            cscore = (cscore / castT) * 100
            pass
        #print("cast perc:", cscore)

        # calculating total rating value
        sum_ = 0
        if gscore != 0:
            sum_ += (decimal.Decimal(userData['main'][0][1]) / 100) * gscore
            pass
        if ascore != 0:
            sum_ += (decimal.Decimal(userData['main'][0][2]) / 100) * ascore
            pass
        if cscore != 0:
            sum_ += (decimal.Decimal(userData['main'][0][3]) / 100) * cscore
            pass
        totalScore = 0
        if sum_ != 0:
            totalScore = round((sum_/catT) * 100, 2)
            pass
        #print("perc:", totalScore)
        scores.append({'m':totalScore, 'g':gscore, 'a':ascore, 'c':cscore, 't':m})
        pass
    # sorting and choosing the top 10 to recommend
    scores.sort(key = FilterKey, reverse = True)
    rekos = scores[0:10]
    print(rekos)
    RekoBase.CloseDatabase(conn)
    return 0

def ContentFilteringScore(dbuser, dbpass, uid):
    conn, cur = RekoBase.ConnectToDatabase(dbuser, dbpass)
    userData = RekoBase.GetUserProfileData(cur, uid)
    print(userData)
    targetYears = RekoBase.GetWatchedYears(cur, uid)
    print(targetYears)
    movies = RekoBase.GetTitlesForCF(cur, targetYears)
    scores = []
    for m in movies:
        data = RekoBase.GetTitleData(cur, m)
        print(data)
        data = RekoBase.CreateFilterData(data)
        #print(data)
        genreInfo = RekoBase.LookupGenre(cur, data['g'])
        #print(genreInfo)
        ratingInfo = RekoBase.LookupAgeRatings(cur, data['a'])
        #print(ratingInfo)
        gscore = decimal.Decimal(0)
        cscore = decimal.Decimal(0)
        ascore = decimal.Decimal(0)
        for g in genreInfo:
            gscore += userData['genres'][0][g]
            pass
        ascore += userData['ratings'][0][ratingInfo]
        for c in userData['cast']:
            if c[2] in data['c']:
                cscore += c[3]
                pass
            pass
        totalScore = gscore + cscore + ascore
        scores.append({'m':totalScore, 'g':gscore, 'a':ascore, 'c':cscore, 't':m})
        pass
    # sorting and choosing the top 10 to recommend
    scores.sort(key = FilterKey, reverse = True)
    rekos = scores[0:10]
    print(rekos)
    RekoBase.CloseDatabase(conn)
    return 0

def CollaborativeSimple(dbuser, dbpass, uid):
    conn, cur = RekoBase.ConnectToDatabase(dbuser, dbpass)
    userData = RekoBase.GetUserProfileData(cur, uid)
    users = RekoBase.GetUsersForCF(cur, userData)
    table, movies = RekoBase.GenerateCF_Table(cur, users)
    scores = [[0,-1]] * len(movies)
    for m in range(len(movies)):
        for u in range(len(users)):
            scores[m] = [scores[m][0] + table[u][m], m]
            pass
        pass
    #print(scores)
    scores.sort(reverse = True)
    scoreL = []
    for s in scores:
        scoreL.append({'m':s, 't':movies[m]})
        pass
    rekos = scoreL[0:10]
    print(rekos)
    return 0