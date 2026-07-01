from operator import add

from books import models_books
from core.extensions import db,  login_manager
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, login_user, current_user
from books.models_books import Books, UserBook
from auth.models_user import User 

books_bp=Blueprint('books',__name__,template_folder='templates')

@books_bp.route('/home',methods=['GET','POST'])
@login_required
def home():
    if request.method=='GET':
        books = UserBook.query.filter_by(user_id=current_user.id).all()
        return render_template('home_page.html',books=books)
    if request.method=='POST':
        book_title=request.form.get('title')
        book_author=request.form.get('author')
        book_genre=request.form.get('genre')
        existing_book=Books.query.filter_by(title=book_title).first()#check if book is in the books table
        if existing_book:
            addbook=UserBook(user_id=current_user.id,book_id=existing_book.book_id)
            db.session.add(addbook)
            db.session.commit()
            return redirect(url_for('books.home'))
        else:
            # if book does not exist,then add book to books tabel and the add to userbook
            newbook=Books(author=book_author,title=book_title,genre=book_genre)
            db.session.add(newbook)
            db.session.commit()
            existing_book=Books.query.filter_by(title=book_title).first()
            addbook=UserBook(user_id=current_user.id,book_id=existing_book.book_id)
            db.session.add(addbook)
            db.session.commit()
            return redirect(url_for('books.home'))
            
@books_bp.route('/detail/<int:book_id>',methods=['GET','POST'])
@login_required
def book_detail(book_id):
    if request.method=='GET':
        current_book=Books.query.filter_by(book_id=book_id).first()
        return render_template('book_page.html',book=current_book)
    