import sys
import mysql.connector
import random
import time

def GetRating():
    ratings = ['PG', 'PG-13', 'R']
    i = random.randint(0, 2)
    return ratings[i]

def main():
    conn = mysql.connector.MySQLConnection(host="localhost", user='reko', passwd='comp3901', database="moviesdb")
    cur = conn.cursor()
    fptr = open("filtered(titles).txt", "rb")
    start = time.time()
    for line in reversed(list(fptr.readlines())):
        line = line.decode().split('||')
        if int(line[4]) == 0:
            r = GetRating()
            q = "UPDATE titles SET isadult_='{}' WHERE tconst_='{}';"
            #print(q.format(r, line[0]))
            cur.execute(q.format(r, line[0].strip()))
            pass
        pass
    conn.commit()
    end = time.time()
    conn.close()
    print("time taken: %s seconds.", (end - start))
    pass

if "__main__" == __name__:
    print("running...")
    main()
    print("completed.")