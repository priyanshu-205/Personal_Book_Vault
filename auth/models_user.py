from core.extensions import db
from flask_login import UserMixin
class User(db.Model,UserMixin):    
    __tablename__='user'
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(80),unique=True,nullable=False)
    password=db.Column(db.String(200),unique=True,nullable=False)
    email=db.Column(db.String(200),unique=True)
    # User's library
    user_books = db.relationship(
        "UserBook",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # Reading sessions created
    created_sessions = db.relationship(
        "ReadingSession",
        foreign_keys="ReadingSession.creator_id",
        back_populates="creator_user"
    )

    # Sessions the user joined
    joined_sessions = db.relationship(
        "SessionParticipant",
        back_populates="participant_user",
        cascade="all, delete-orphan"
    )

    # Friendships initiated by this user
    friendships = db.relationship(
        "Friendship",
        foreign_keys="Friendship.user_id",
        back_populates="user"
    )

    # Friendships where this user is the friend
    friend_of = db.relationship(
        "Friendship",
        foreign_keys="Friendship.friend_id",
        back_populates="friend"
    )
