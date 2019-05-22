from app import app, db
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, session, g
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import SignupForm, LoginForm
from app.models import UserProfile
from werkzeug.security import check_password_hash
import random
import urllib2
import json
import RekoCommander
from functools import wraps


import mysql.connector

def DB_Conn():
    #print("here")
    conn = mysql.connector.connect(host='localhost', user='reko', passwd='comp3901', database='moviesdb')
    cursor = conn.cursor()
    return conn, cursor

def GetTitleImage(title='tt4154796'):
    try:
        contents = urllib2.urlopen("https://www.imdb.com/title/"+title.decode()+"/mediaviewer/").read().decode("utf-8", "replace")
    except Exception as e:
        print e
        return "https://www.auro-3d.com/wp-content/uploads/2016/08/no-poster-available.jpg"
    #print(contents)
    r1 = contents.rfind('"msrc":"')
    #print("position0:", r1)
    r1 = contents.find('"src":"', r1)
    #print("position1:", r1)
    r2 = contents.find('",', r1)
    #print("position2:", r2)
    s = contents[r1+7:r2]
    #print("substring:", s)

    return s

@app.route('/home')
#@login_required
def home():
    """Render website's home page."""
    if 'logged_in' in session:
        s = request.args.get('rekoPhase')
        print("here2:", s)
        conn, cur = DB_Conn()
        if s != None:
            r = RekoCommander.RunCommand(s, session['user_id'])
            print "RekoAPI response:", r
            pass
        q = "select * from rekomovies where userid = {};"
        cur.execute(q.format(session['user_id']))
        res = cur.fetchall()
        indexes = [0, 0, 0, 0]
        if len(res) == 0:
            res = []
        else:
            res = list(res[0])
            res.pop(0)
            #print res
            pass
            for j in range(len(res)):
                print res[j]
                res[j] = res[j].split('||')
                if len(res[j]) <= 1:
                    continue
                titles = []
                for i in range(len(res[j])):
                    res[j][i] = json.loads(res[j][i])
                    #print "index:", res[j][i]
                    q = "select * from titles where tconst_='{}';"
                    q = q.format(res[j][i]['t'])
                    cur.execute(q)
                    r = list(cur.fetchall()[0])
                    r.append("https://www.auro-3d.com/wp-content/uploads/2016/08/no-poster-available.jpg")
                    r.append(res[j][i]['m'])
                    titles.append(r)
                    indexes[j] = len(titles)
                    pass
                res[j] = titles
                pass
            pass
        #print "res:", res
        print "ind:", indexes
        conn.close()
        return render_template("home.html", rekos=res, lens=indexes)
    else:
        flash("Please log in first", "danger")
        return redirect(url_for("login"))


@app.route('/', methods=['POST', 'GET'])
def login():
    """Render website's home page."""
    # print("This is the session in login:", session["logged_in"])
    if 'logged_in' in session:
        return redirect(url_for('home'))

    loginform = LoginForm()

    if request.method == "POST" and loginform.validate_on_submit():
        username= loginform.username.data
        password= loginform.password.data
        db, cur = DB_Conn()
        q= 'select * from users_ where uname="{}" and passcode="{}";'
        q = q.format(username, password)
        cur.execute(q)
        r = cur.fetchall()
        cur.close
        print("this:", r)
        db.close()
        if r == []:
            flash("Incorrect username or password", "danger")
            redirect("login.html")
        else:
            session['logged_in'] = True
            session['user_id'] = r[0][0]
            flash('You were logged in')
            print("This is the session before home:", session["logged_in"])
            return redirect(url_for('home'))
    flash_errors(loginform)
    return render_template('login.html', loginform=loginform)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    
    # if current_user.is_authenticated:
    if 'logged_in' in session:
        return redirect(url_for('home'))

    
    signupform = SignupForm()
    
    if request.method == "POST" and signupform.validate_on_submit():
        
        first=signupform.firstname.data
        last=signupform.lastname.data
        username=signupform.username.data
        password=signupform.password.data
        now = datetime.now()
        signdate=  now.strftime("%B")+" "+str(now.day)+", "+str(now.year)
        profpic=signupform.profpic.data
        genre_rate=signupform.genre_rate.data
        cast_rate=signupform.cast_rate.data
        age_rate=signupform.age_rate.data
        genre1=signupform.genre1.data
        genre2=signupform.genre2.data
        
        # user= UserProfile(first, last, username, password, signdate, profpic)
        # db.session.add(user)
        # db.session.commit()

        db, cur = DB_Conn()
        q1 = 'insert into users_ (fname, lname, passcode, uname, profpic, scoresum, scoredenom)values("{}", "{}", "{}", "{}", "{}", {}, {});'
        q1 = q1.format(first, last, password, username, profpic, 5, 1)
        cur.execute(q1)
        db.commit()
        q1 = "select userid from users_ where uname='" + username+"';"
        cur.execute(q1)
        r = cur.fetchall()
        q2 = "insert into maincategories(userid, genrerating, agerating, maincast) values({}, {}, {}, {});"
        q2 = q2.format(r[0][0], genre_rate, age_rate, cast_rate)
        q3 = "insert into subgenresratings(userid, subgenre1, subgenre2, subgenre3, subgenre4, subgenre5, subgenre6, subgenre7, subgenre8, subgenre9, subgenre10, subgenre11) values("
        q3 += str(r[0][0])+","
        s1 = "subgenre"+str(genre1)
        s2 = "subgenre"+str(genre2)
        for i in range(1, 12):
            loc = "subgenre"+str(i)
            if s1 == loc:
                q3 += str(50)
                pass
            elif s2 == loc:
                q3 += str(50)
                pass
            else:
                q3 += str(5)
                pass
            if i != 11:
                q3 += ","
                pass
            pass
        q3 += ");"
        q4 = "insert into ageratings(userid, rating1, rating2, rating3)values({}, 10, 10, 10);"
        q4 = q4.format(r[0][0])

        #print("q3:", q3)
        cur.execute(q3)
        cur.execute(q2)
        cur.execute(q4)
        db.commit() 
        db.close()
        flash("Profile Successfully Created", "success")
        return redirect("/signup",)
        
    flash_errors(signupform)
    return render_template('signup.html',  signupform=signupform)

@app.route('/movie/<title>', methods=['POST', 'GET'])
def Movie(title):
    """Render website's home page."""
    if 'logged_in' in session:
        s = request.args.get('feedback')
        print("here2:", s)
        db, cur = DB_Conn()
        if s != None:
            #print "t: %s || s: %s" % (title, s)
            r = RekoCommander.RunCommand('5', session['user_id'], title, int(s)*2)
            print "RekoAPI response:", r
            pass
        q = "SELECT * FROM {} WHERE tconst_='{}';"
        q = q.format("titles", title)
        cur.execute(q)
        res = cur.fetchall()
        #print("query result: %s" % res) # here is the error now
        img = GetTitleImage(title.strip())
        db.close()
        return render_template('movie.html', themovie=res[0], imgurl=img, title=title)
    else:
        flash("Please log in first", "danger")
        return redirect(url_for("login"))

@app.route('/search', methods=['POST', 'GET'])
def Search():
    """Render website's home page."""
    if 'logged_in' in session:
        default_name=0
        s = request.args.get('search')
        print("here2:", s)
        db, cur = DB_Conn()
        if s == None:
            curYear = datetime.now().year
            curYear -= 10
            q = "SELECT * FROM titles WHERE startyear_ >= " + str(curYear) + " LIMIT {},20;"
            cur.execute(q.format(random.randint(0, 50000)))
            res = cur.fetchall()
            for i in range(len(res)):
                #r = GetTitleImage(res[i][0].strip())
                r = "https://www.auro-3d.com/wp-content/uploads/2016/08/no-poster-available.jpg"
                res[i] = list(res[i])
                res[i].append(r)
                pass
        else:
            q = "SELECT * FROM titles WHERE primarytitle_ like '%{}%';"
            cur.execute(q.format(s.strip()))
            res = cur.fetchall()
            for i in range(len(res)):
                #r = GetTitleImage(res[i][0].strip())
                r = "https://www.auro-3d.com/wp-content/uploads/2016/08/no-poster-available.jpg"
                res[i] = list(res[i])
                res[i].append(r)
                pass
            pass
        db.close()
        return render_template('search.html', movieL=res, x=-1, len=len(res))
    else:
        flash("Please log in first", "danger")
        return redirect(url_for("login"))

@app.route('/mylist')
def myList():
    """Render website's home page."""
    if 'logged_in' in session:
        conn, cur = DB_Conn()
        q = "SELECT * FROM titles JOIN watched ON titles.tconst_=watched.title WHERE watched.userid={};"
        q = q.format(session['user_id'])
        cur.execute(q)
        res = cur.fetchall()
        conn.close()
        return render_template('mylist.html')
    else:
        flash("Please log in first", "danger")
        return redirect(url_for("login"))

@app.route('/edit')
def Edit():
    """Render website's home page."""
    if 'logged_in' in session:
        user=mycurrent_user()
        conn, cur = DB_Conn()
        uid = session['user_id']
        q = "select * from maincategories where userid={}"
        cur.execute(q.format(uid))
        r = list(cur.fetchall()[0])
        conn.close()
        return render_template('edit.html', user=user, info=r)
    else:
        flash("Please log in first", "danger")
        return redirect(url_for("login"))

def mycurrent_user():

    db, cur = DB_Conn()
    q= 'select * from users_ where userid="{}";'
    q= q.format(session['user_id'])
    cur.execute(q)
    r = cur.fetchall()
    cur.close
    return r


def login_required(f):
    @wraps(f)

    def wrap(*args, **kwargs):
        print("This is the session in decorator before the if:", session["logged_in"])
        if 'logged_in' in session:
            print("This is the session in decorator 1:", session["logged_in"])
            if session["logged_in"]==True:
                print("This is the session in decorator 2:", session["logged_in"])
                return f(*args, **kwargs)
        else:
            flash("Unauthorized, please log in", "danger")
            print("This is the session in decorator after redirect to login", session["logged_in"])
            return redirect(url_for('login'))
    print("This is the session in decorator after if:", session["logged_in"])
    #return wrap


@app.route('/logout')
def logout():
    if 'logged_in' in session:
        session.clear()
        flash("You are now logged out", "success")
        return render_template("logout.html")
    else:
        flash("Please log in first", "danger")
        return redirect(url_for("login"))

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (getattr(form, field).label.text, error), 'danger')