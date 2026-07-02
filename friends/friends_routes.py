from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_, and_

from core.extensions import db
from friends.models import Friendship
from auth.models_user import User
from books.models_books import UserBook


friends_bp = Blueprint("friends", __name__, template_folder="templates")


def get_friends(user_id):
    """Returns a list of User objects the given user is friends with
    (status == 'accepted', in either direction)."""
    sent = Friendship.query.filter_by(user_id=user_id, status="accepted").all()
    received = Friendship.query.filter_by(friend_id=user_id, status="accepted").all()

    friends = [f.friend for f in sent] + [f.user for f in received]
    return friends


@friends_bp.context_processor
def inject_pending_count():
    """Makes the incoming-request count available to every template
    rendered from this blueprint (used for the Requests tab badge)."""
    if current_user.is_authenticated:
        count = Friendship.query.filter_by(
            friend_id=current_user.id, status="pending"
        ).count()
    else:
        count = 0

    return dict(pending_count=count)


@friends_bp.route("/friends", methods=["GET"])
@login_required
def friends_list():
    friends = get_friends(current_user.id)

    return render_template(
        "friends_list.html",
        friends=friends,
        active_tab="friends",
    )


@friends_bp.route("/friends/requests", methods=["GET"])
@login_required
def requests_view():
    incoming = Friendship.query.filter_by(
        friend_id=current_user.id, status="pending"
    ).order_by(Friendship.created_at.desc()).all()

    return render_template(
        "requests.html",
        incoming=incoming,
        active_tab="requests",
    )


@friends_bp.route("/friends/search", methods=["GET"])
@login_required
def search():
    query = (request.args.get("q") or "").strip()
    results = []

    if query:
        matches = User.query.filter(
            User.username.ilike(f"%{query}%"),
            User.id != current_user.id,
        ).order_by(User.username.asc()).limit(20).all()

        friend_ids = {u.id for u in get_friends(current_user.id)}

        outgoing_pending_ids = {
            f.friend_id for f in Friendship.query.filter_by(
                user_id=current_user.id, status="pending"
            ).all()
        }

        incoming_pending_ids = {
            f.user_id for f in Friendship.query.filter_by(
                friend_id=current_user.id, status="pending"
            ).all()
        }

        for user in matches:
            if user.id in friend_ids:
                relation = "friends"
            elif user.id in outgoing_pending_ids:
                relation = "requested"
            elif user.id in incoming_pending_ids:
                relation = "incoming"
            else:
                relation = "none"

            results.append({"user": user, "relation": relation})

    return render_template(
        "search.html",
        query=query,
        results=results,
        active_tab="search",
    )


@friends_bp.route("/friends/request/<int:user_id>", methods=["POST"])
@login_required
def send_request(user_id):
    if user_id == current_user.id:
        flash("You can't send a friend request to yourself.", "error")
        return redirect(url_for("friends.search"))

    target = User.query.get(user_id)

    if not target:
        flash("User not found.", "error")
        return redirect(url_for("friends.search"))

    existing = Friendship.query.filter(
        or_(
            and_(Friendship.user_id == current_user.id, Friendship.friend_id == user_id),
            and_(Friendship.user_id == user_id, Friendship.friend_id == current_user.id),
        )
    ).first()

    if existing:
        if existing.status == "accepted":
            flash("You are already friends.", "warning")
        else:
            flash("A friend request already exists between you two.", "warning")
        return redirect(url_for("friends.search"))

    new_request = Friendship(
        user_id=current_user.id,
        friend_id=user_id,
        status="pending",
    )
    db.session.add(new_request)
    db.session.commit()

    flash(f"Friend request sent to {target.username}.", "success")
    return redirect(url_for("friends.search"))


@friends_bp.route("/friends/requests/<int:request_id>/accept", methods=["POST"])
@login_required
def accept_request(request_id):
    friend_request = Friendship.query.filter_by(
        id=request_id, friend_id=current_user.id, status="pending"
    ).first()

    if not friend_request:
        flash("Request not found.", "error")
        return redirect(url_for("friends.requests_view"))

    friend_request.status = "accepted"
    db.session.commit()

    flash(f"You are now friends with {friend_request.user.username}.", "success")
    return redirect(url_for("friends.requests_view"))


@friends_bp.route("/friends/requests/<int:request_id>/decline", methods=["POST"])
@login_required
def decline_request(request_id):
    friend_request = Friendship.query.filter_by(
        id=request_id, friend_id=current_user.id, status="pending"
    ).first()

    if not friend_request:
        flash("Request not found.", "error")
        return redirect(url_for("friends.requests_view"))

    db.session.delete(friend_request)
    db.session.commit()

    flash("Friend request declined.", "message")
    return redirect(url_for("friends.requests_view"))


@friends_bp.route("/friends/remove/<int:friend_id>", methods=["POST"])
@login_required
def remove_friend(friend_id):
    friendship = Friendship.query.filter(
        or_(
            and_(Friendship.user_id == current_user.id, Friendship.friend_id == friend_id),
            and_(Friendship.user_id == friend_id, Friendship.friend_id == current_user.id),
        ),
        Friendship.status == "accepted",
    ).first()

    if friendship:
        db.session.delete(friendship)
        db.session.commit()
        flash("Friend removed.", "success")
    else:
        flash("Friendship not found.", "error")

    return redirect(url_for("friends.friends_list"))


@friends_bp.route("/friends/activity", methods=["GET"])
@login_required
def activity():
    friend_ids = [u.id for u in get_friends(current_user.id)]

    entries = []
    if friend_ids:
        entries = (
            UserBook.query
            .filter(
                UserBook.user_id.in_(friend_ids),
                UserBook.status == "Completed",
            )
            .order_by(UserBook.added_at.desc())
            .limit(50)
            .all()
        )

    return render_template(
        "activity.html",
        entries=entries,
        active_tab="activity",
    )