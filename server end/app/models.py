from . import db
from werkzeug.security import  generate_password_hash

class UserProfile(db.Model):
    
    __tablename__ = 'user_profiles'
    
    username = db.Column(db.String(80), primary_key=True)
    firstname = db.Column(db.String(80))
    lastname = db.Column(db.String(80))
    password = db.Column(db.String(255))
    profpic = db.Column(db.String(80))
    signdate= db.Column(db.String(80))
    
    def __init__(self, firstname, lastname, username, password, signdate, profpic):
        self.username=username
        self.firstname=firstname
        self.lastname=lastname
        self.password=generate_password_hash(password, method='pbkdf2:sha256')
        self.signdate=signdate
        self.profpic=profpic
        
        
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def __repr__(self):
        return '<User %r>' % (self.username)

# class UserMovies(db.Model):
    
#     __tablename__ = 'user_movies'
    
#     username = db.Column(db.String(80), primary_key=True)
#     movie = db.Column(db.String(80))
#     rank = db.Column(db.int)
#     rankdate= db.Column(db.String(10))
    
#     def __init__(self, username, movie, rank, rankdate):
#         self.username=username
#         self.movie=movie
#         self.rank=rank
#         self.rankdate=rankdate