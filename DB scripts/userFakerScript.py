import sys

CONST_FNAME = 'first'
CONST_LNAME = 'last'
CONST_PASSC = 'pass123'
CONST_GENRELIST = {'musical':3, 'documentary':10, 'animation':7, 'adventure':1, 'drama':2, 'thriller':5, 'action':0, 'romance':6, 'horror':4, 'sci-fi':9, 'comedy':8}

CONST_COMEDY = ['comedy', 'short', 'game-show', 'talk-show', 'family']
CONST_ACTION = ['action', 'crime', 'western']
CONST_DRAMA = ['drama', 'reality-tv']
CONST_MUSICAL = ['musical', 'music']
CONST_THRILLER = ['thriller', 'war', 'sport']
CONST_HORROR = ['horror', 'mystery']
CONST_ROMANCE = ['romance', 'adult', 'romantic']
CONST_DOCUMENTARY = ['documentary', 'biography', 'history']
CONST_SCIFI= ['sci-fi', 'fantasy']
CONST_ANIMATION = ['animation', 'cartoon']
CONST_ADVENTURE = ['adventure', 'film-noir']
CONST_GENREREFLIST = [CONST_ACTION, CONST_ADVENTURE, CONST_DRAMA, CONST_MUSICAL, CONST_HORROR, CONST_THRILLER, CONST_ROMANCE, CONST_ANIMATION, CONST_COMEDY, CONST_SCIFI, CONST_DOCUMENTARY]

def FilterRead(ptr):
    line = ptr.readline()
    return line

def CreateUserTable():
    table = "DROP TABLE IF EXISTS users_;\nCREATE TABLE users_("
    table += "userid int(4) PRIMARY KEY, fname varchar(16) NOT NULL, lname varchar(16) NOT NULL,"
    table += "passcode varchar(32) NOT NULL"
    return table + ');'

def CreateMainCategoriesTable():
    table = "DROP TABLE IF EXISTS mainCategories;\nCREATE TABLE mainCategories("
    table += "user_ int(4) REFERENCES users_.userid,"
    table += "GenreRating Decimal(9,2) not null, AgeRating Decimal(9,2) not null, MainCast Decimal(9,2) not null"
    return table + ');'

def CreateSubGenresTable(genres):
    tableData = "DROP TABLE IF EXISTS subGenresRatings;\nCREATE TABLE subGenresRatings("
    for v in range(11):
        tableData += "subgenre" + str(v) + " Decimal(9,2) not null"
        if v != 10:
            tableData += ", "
            pass
        pass
    tableData += ");\n"
    tableData += "DROP TABLE IF EXISTS subGenres;\nCREATE TABLE subGenres("
    tableData += "genreid int(2) not null auto increment, genre varchar(32) not null);\n"
    for l in CONST_GENREREFLIST:
        tableData += 'insert into subGenres(genre) values('
        tableData += '"' + l[0] + '");\n'
        pass
    tableData += "DROP TABLE IF EXISTS subGenresLookup;\nCREATE TABLE subGenresLookup("
    tableData += "genreid int(2) not null auto increment, subgenre varchar(32) not null, referenceid int(2) not null);\n"
    for k,v in genres.items():
        #print("key: %s | value: %s\n" % (k, v))
        for i in range(len(CONST_GENREREFLIST)):
            for sub in CONST_GENREREFLIST[i]:
                #print("comparing %s and %s" % (k, sub))
                if str(k) in sub:
                    #print('%s found' % k)
                    tableData += "insert into subGenresLookup(subgenre, referenceid) values("
                    tableData += '"' + str(k) + '", ' + str(genres[CONST_GENREREFLIST[i][0]]) + ');\n'
                    break
                pass
            pass
        pass
    return tableData

def CreateAgeRatingTable():
    table = "DROP TABLE IF EXISTS ageRatings;\nCREATE TABLE ageRatings("
    table += "ratingid int(2) not null auto increment, adultRating Decimal(9,2) not null, childRating Decimal(9,7) not null"
    return table + ");"

def CreateWatchedTable():
    table = "DROP TABLE IF EXISTS watched;\nCREATE TABLE watched("
    table += "entry int(4) not null auto increment primary key, userid int(4) not null, title varchar(64) not null, rating Decimal(4,2)"
    return table + ");"

def CreateMainCastTable():
    table = "DROP TABLE IF EXISTS mainCast;\nCREATE TABLE mainCast("
    table += "userid"
    return table + ");"

def mainFunc(args):
    print("**User accounts faker script running...\n")
    if not args.get('-tf'):
        print('No target file set. Please set the -tf flag')
        return -1
    args['-tf'] = args['-tf'].split(',')
    filePtr = open(args['-tf'][0].strip(), 'rb')
    genres = CONST_GENRELIST
    l = []
    line = FilterRead(filePtr)
    while len(line) > 1:
        data = line.decode().strip().split(",")
        #print("line:", line)
        #print("data:", data)
        index = int(args['-tf'][1].strip())
        index = len(data) - 1
        temp = data[index].strip().replace("'", '')
        #print("t:", temp)
        if '\\n' not in temp.lower() and temp.lower() not in genres:
            genres.update({temp.lower():0})
            pass
        line = FilterRead(filePtr)
        pass
    print("genres:\n", genres)
    print("length: %d\n" % len(genres))
    #res = CreateSubGenres(genres)
    res = CreateWatchedTable()
    print("returned:", res)
    return 0
    if not args.get('-urs'):
        print('No limitation set to the amount of users. Please set the -urs flag')
        return -1
    userLimit = args['-urs']
    for i in range(userLimit):
        pass
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
    args = ParseArgs()
    res = mainFunc(args)
    print(res)