from core.extensions import db
from datetime import datetime,timezone

class Friendship:
    __tablename__='friendship'
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    friend_id=db.Column(db.Integer,db.ForeignKey('user.id'))#self referential integrity

class Reading_Session:
    __tablename__='reading_session'
    id=db.Column(db.Integer,primary_key=True)
    creator=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    book_id=db.Column(db.Integer,db.ForeignKey('books.id'),nullable=False)
    
class Session_Participant:
    __tablename__='session_participant'
    id=db.Column(db.Integer,primary_key=True)
    session_id=db.Column(db.Integer,primary_key=True)
    participant=db.Column(db.Integer,db.ForeignKey('user.id'))
    


    
    