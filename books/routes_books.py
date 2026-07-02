import os

from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for,
    flash,
    current_app,
)

from flask_login import (
    login_required,
    current_user,
    logout_user,
)

from werkzeug.utils import secure_filename

from core.extensions import db
from books.models_books import Books, UserBook


books_bp = Blueprint(
    "books",
    __name__,
    template_folder="templates"
)


ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}


def allowed_file(filename):

    return (
        "." in filename
        and
        filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


@books_bp.route("/home", methods=["GET", "POST"])
@login_required
def home():

    if request.method == "GET":

        books = UserBook.query.filter_by(
            user_id=current_user.id
        ).all()

        return render_template(
            "home_page.html",
            books=books
        )

    elif request.method == "POST":

        book_title = request.form.get("title")
        book_author = request.form.get("author")
        book_genre = request.form.get("genre")
        book_status = request.form.get("status")

        cover = request.files.get("cover_image")

        filename = None

        if cover and cover.filename != "":

            if not allowed_file(cover.filename):

                flash(
                    "Only jpg, jpeg, png and webp files are allowed.",
                    "error"
                )

                return redirect(url_for("books.home"))

            filename = secure_filename(cover.filename)

            cover.save(
                os.path.join(
                    current_app.static_folder,
                    "covers",
                    filename,
                )
            )

        existing_book = Books.query.filter_by(
            title=book_title
        ).first()

        if existing_book:

            already_added = UserBook.query.filter_by(
                user_id=current_user.id,
                book_id=existing_book.book_id,
            ).first()

            if already_added:

                flash(
                    "Book already exists in your library.",
                    "warning",
                )

                return redirect(url_for("books.home"))

            addbook = UserBook(
                user_id=current_user.id,
                book_id=existing_book.book_id,
                status=book_status,
            )

            db.session.add(addbook)
            db.session.commit()

            flash(
                "Book added successfully.",
                "success",
            )

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

        flash(
            "Book added successfully.",
            "success",
        )

        return redirect(url_for("books.home"))


@books_bp.route("/detail/<int:book_id>", methods=["GET"])
@login_required
def book_detail(book_id):

    current_book = Books.query.filter_by(
        book_id=book_id
    ).first()

    if current_book is None:

        flash(
            "Book not found.",
            "error",
        )

        return redirect(url_for("books.home"))

    user_book = UserBook.query.filter_by(
        user_id=current_user.id,
        book_id=book_id,
    ).first()

    if user_book is None:

        flash(
            "Book not found in your library.",
            "error",
        )

        return redirect(url_for("books.home"))

    return render_template(
        "book_page.html",
        book=current_book,
        user_book=user_book,
    )


@books_bp.route("/update_status/<int:book_id>", methods=["POST"])
@login_required
def update_status(book_id):

    status = request.form.get("status")

    id = UserBook.query.filter_by(
        book_id=book_id,
        user_id=current_user.id,
    ).first()

    if id:

        id.status = status

        db.session.commit()

        flash(
            "Reading status updated.",
            "success",
        )

    else:

        flash(
            "Book not found.",
            "error",
        )

    return redirect(
        url_for(
            "books.book_detail",
            book_id=book_id,
        )
    )


@books_bp.route("/detail/<int:book_id>/review", methods=["POST"])
@login_required
def add_review(book_id):

    id = UserBook.query.filter_by(
        user_id=current_user.id,
        book_id=book_id,
    ).first()

    if id:

        id.review = request.form.get("review")
        id.rating = request.form.get("rating")

        db.session.commit()

        flash(
            "Review saved.",
            "success",
        )

    else:

        flash(
            "Book not found.",
            "error",
        )

    return redirect(
        url_for(
            "books.book_detail",
            book_id=book_id,
        )
    )


@books_bp.route("/detail/<int:book_id>/remove", methods=["POST"])
@login_required
def remove_book(book_id):

    id = UserBook.query.filter_by(
        user_id=current_user.id,
        book_id=book_id,
    ).first()

    if id:

        db.session.delete(id)
        db.session.commit()

        flash(
            "Book removed.",
            "success",
        )

    else:

        flash(
            "Book not found.",
            "error",
        )

    return redirect(url_for("books.home"))


@books_bp.route("/home/logout", methods=["GET"])
@login_required
def logout():

    logout_user()

    flash(
        "Logged out successfully.",
        "success",
    )

    return redirect(
        url_for("auth.user_login")
    )

