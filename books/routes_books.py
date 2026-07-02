import os
import uuid

from flask import Blueprint, request, render_template, redirect,url_for, flash, current_app
from flask_login import login_required, current_user, logout_user
from werkzeug.utils import secure_filename

from core.extensions import db
from books.models_books import Books, UserBook


books_bp = Blueprint("books", __name__, template_folder="templates")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
ALLOWED_STATUSES = {"To Read", "Reading", "Completed"}



def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def save_cover(cover_file):
    """Saves an uploaded cover image with a collision-safe filename.
    Returns the stored filename, or None if no file was provided."""
    if not cover_file or cover_file.filename == "":
        return None

    if not allowed_file(cover_file.filename):
        return False  # sentinel for "invalid file type"

    ext = cover_file.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"

    covers_dir = os.path.join(current_app.static_folder, "covers")
    os.makedirs(covers_dir, exist_ok=True)

    cover_file.save(os.path.join(covers_dir, filename))
    return filename


@books_bp.route("/home", methods=["GET", "POST"])
@login_required
def home():

    if request.method == "GET":
        status_filter = request.args.get("status")

        query = UserBook.query.filter_by(user_id=current_user.id)
        if status_filter in ALLOWED_STATUSES:
            query = query.filter_by(status=status_filter)

        books = query.all()

        return render_template(
            "home_page.html",
            books=books,
            active_status=status_filter,
            statuses=sorted(ALLOWED_STATUSES),
        )

    elif request.method == "POST":
        book_title = (request.form.get("title") or "").strip()
        book_author = (request.form.get("author") or "").strip()
        book_genre = (request.form.get("genre") or "").strip()
        book_status = request.form.get("status")

        if not book_title or not book_author:
            flash("Title and author are required.", "error")
            return redirect(url_for("books.home"))

        if book_status not in ALLOWED_STATUSES:
            flash("Invalid reading status.", "error")
            return redirect(url_for("books.home"))

        # Resolve or create the catalog-level Books row first,
        # matching on title + author (not title alone).
        existing_book = Books.query.filter_by(
            title=book_title, author=book_author
        ).first()

        if existing_book:
            already_added = UserBook.query.filter_by(
                user_id=current_user.id,
                book_id=existing_book.book_id,
            ).first()

            if already_added:
                flash("Book already exists in your library.", "warning")
                return redirect(url_for("books.home"))

            cover = request.files.get("cover_image")
            if not existing_book.cover_image and cover and cover.filename != "":
                filename = save_cover(cover)
                if filename is False:
                    flash("Only jpg, jpeg, png and webp files are allowed.", "error")
                    return redirect(url_for("books.home"))
                existing_book.cover_image = filename
                db.session.commit()
            addbook = UserBook(
                user_id=current_user.id,
                book_id=existing_book.book_id,
                status=book_status,
            )
            db.session.add(addbook)
            db.session.commit()

            flash("Book added successfully.", "success")
            return redirect(url_for("books.home"))

        # New book: only now do we touch the filesystem.
        cover = request.files.get("cover_image")
        print(cover)
        filename = save_cover(cover)

        if filename is False:
            flash("Only jpg, jpeg, png and webp files are allowed.", "error")
            return redirect(url_for("books.home"))

        newbook = Books(
            title=book_title,
            author=book_author,
            genre=book_genre,
            cover_image=filename,
        )
        db.session.add(newbook)
        db.session.commit()

        addbook = UserBook(
            user_id=current_user.id,
            book_id=newbook.book_id,
            status=book_status,
        )
        db.session.add(addbook)
        db.session.commit()

        flash("Book added successfully.", "success")
        return redirect(url_for("books.home"))


@books_bp.route("/detail/<int:book_id>", methods=["GET"])
@login_required
def book_detail(book_id):
    current_book = Books.query.filter_by(book_id=book_id).first()

    if current_book is None:
        flash("Book not found.", "error")
        return redirect(url_for("books.home"))

    user_book = UserBook.query.filter_by(
        user_id=current_user.id, book_id=book_id
    ).first()

    if user_book is None:
        flash("Book not found in your library.", "error")
        return redirect(url_for("books.home"))

    return render_template(
        "book_page.html",
        book=current_book,
        user_book=user_book,
        statuses=sorted(ALLOWED_STATUSES),
    )


@books_bp.route("/update_status/<int:book_id>", methods=["POST"])
@login_required
def update_status(book_id):
    status = request.form.get("status")

    if status not in ALLOWED_STATUSES:
        flash("Invalid reading status.", "error")
        return redirect(url_for("books.book_detail", book_id=book_id))

    user_book = UserBook.query.filter_by(
        book_id=book_id, user_id=current_user.id
    ).first()

    if user_book:
        user_book.status = status
        db.session.commit()
        flash("Reading status updated.", "success")
    else:
        flash("Book not found.", "error")

    return redirect(url_for("books.book_detail", book_id=book_id))


@books_bp.route("/detail/<int:book_id>/review", methods=["POST"])
@login_required
def add_review(book_id):
    user_book = UserBook.query.filter_by(
        user_id=current_user.id, book_id=book_id
    ).first()

    if not user_book:
        flash("Book not found.", "error")
        return redirect(url_for("books.book_detail", book_id=book_id))

    rating_raw = request.form.get("rating")
    rating = None
    if rating_raw:
        try:
            rating = int(rating_raw)
            if not (1 <= rating <= 5):
                raise ValueError
        except ValueError:
            flash("Rating must be a number between 1 and 5.", "error")
            return redirect(url_for("books.book_detail", book_id=book_id))

    user_book.review = request.form.get("review")
    user_book.rating = rating

    db.session.commit()
    flash("Review saved.", "success")

    return redirect(url_for("books.book_detail", book_id=book_id))


@books_bp.route("/detail/<int:book_id>/remove", methods=["POST"])
@login_required
def remove_book(book_id):
    user_book = UserBook.query.filter_by(
        user_id=current_user.id, book_id=book_id
    ).first()

    if user_book:
        db.session.delete(user_book)
        db.session.commit()
        flash("Book removed.", "success")
    else:
        flash("Book not found.", "error")

    return redirect(url_for("books.home"))


@books_bp.route("/home/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth.user_login"))