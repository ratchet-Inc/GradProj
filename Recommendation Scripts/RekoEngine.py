import RekoBase
import datetime

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
        print(data)
        genreInfo = RekoBase.LookupGenre(cur, data['g'])
        print(genreInfo)
        ratingInfo = RekoBase.LookupAgeRatings(cur, data['a'])
        print(ratingInfo)
        break
        pass
    RekoBase.CloseDatabase(conn)
    return 0

def ContentFilteringScore(dbuser, dbpass, uid):
    conn, cur = RekoBase.ConnectToDatabase(dbuser, dbpass)
    userData = RekoBase.GetUserProfileData(cur, uid)
    print(userData)
    RekoBase.CloseDatabase(conn)
    return 0
