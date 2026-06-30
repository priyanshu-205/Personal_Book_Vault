from core.extensions import db,  login_manager
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, login_user, current_user
from auth.models_user import User

books_bp=Blueprint('books',__name__,template_folder='templates')

@books_bp.route('/home',methods=['GET','POST'])
@login_required
def home():
    