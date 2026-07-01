from core.extensions import db
from datetime import datetime,timezone

class Friendship(db.Model):
    __tablename__='friendship'
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    friend_id=db.Column(db.Integer,db.ForeignKey('user.id'))#self referential integrity

    user = db.relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="friendships"
    )

    friend = db.relationship(
        "User",
        foreign_keys=[friend_id],
        back_populates="friend_of"
    )
    
class ReadingSession(db.Model):
    __tablename__='reading_session'
    id=db.Column(db.Integer,primary_key=True)
    creator_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    book_id=db.Column(db.Integer,db.ForeignKey('books.book_id'),nullable=False)
    
    creator_user = db.relationship(
    "User",
    foreign_keys=[creator_id],
    back_populates="created_sessions"
    )

    book = db.relationship(
        "Books",
        back_populates="reading_sessions"
    )

    participants = db.relationship(
        "SessionParticipant",
        back_populates="session",
    )
    
class SessionParticipant(db.Model):
    __tablename__='session_participant'
    id=db.Column(db.Integer,primary_key=True)
    session_id = db.Column(db.Integer,db.ForeignKey("reading_session.id"),nullable=False)
    participant=db.Column(db.Integer,db.ForeignKey('user.id'))
    
    session = db.relationship(
        "ReadingSession",
        back_populates="participants"
    )

    participant_user = db.relationship(
        "User",
        back_populates="joined_sessions"
    )
    
    