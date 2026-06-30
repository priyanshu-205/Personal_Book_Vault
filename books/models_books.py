from core.extensions import db
from datetime import datetime,timezone
class Books(db.Model):
    __tablename__='books'
    book_id=db.Column(db.Integer,primary_key=True)
    author=db.Column(db.String(200),nullable=False)
    title=db.Column(db.String(200),nullable=False)
    genre=db.Column(db.String(200))
    
    
class UserBook(db.Model):
    __tablename__='userbook'
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    book_id=db.Column(db.Integer,db.ForeignKey('books.id'),nullable=False)
    status=db.Column(db.String(200),nullable=False)
    added_at=db.Column(db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False)
    