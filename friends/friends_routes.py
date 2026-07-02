from flask import Blueprint
from flask import (Blueprint,request,render_template,redirect,url_for,flash,current_app,)

from flask_login import (login_required,current_user,logout_user,)

from werkzeug.utils import secure_filename

from core.extensions import db
from auth.models_user import User
from books.models_books import Books, UserBook
from friends.models import Friendship,ReadingSession,SessionParticipant

friends_bp=Blueprint('friends',__name__,template_folder='templates')

@friends_bp.route('/friends',methods=['GET','POST'])
@login_required
def show_friends():
    if request.method.get=='GET':
        user_friends=Friendship.query.filter_by(user_id=current_user.id).all()
        return(render_template('friends_page.html',friends=user_friends))
    
