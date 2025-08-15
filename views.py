from flask import Blueprint, render_template, flash, request, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Page, Session, Comment, FanContent, User
from datetime import datetime
from . import db


views = Blueprint('views', __name__)

SHOWN_SESSIONS=4



@views.route('/')
@login_required
def home():
    now = datetime.now()
    # Query upcoming sessions (future or today), sorted ascending by date
    upcoming_sessions = Session.query.filter(Session.session_date >= now).order_by(Session.session_date.asc()).limit(1).all()
    # Query past sessions, sorted descending by date
    past_sessions = Session.query.filter(Session.session_date < now).order_by(Session.session_date.desc()).limit(SHOWN_SESSIONS).all()
    fan_content_for_previous=None
    session_with_winners= []
    winner=None
    if past_sessions:
        previous_session = past_sessions[0]
        fan_content_for_previous = (
            FanContent.query
            .filter_by(session_id=previous_session.id)
            .all()
        )
        for session in past_sessions:
            top_content = FanContent.query.filter(FanContent.session_id == session.id,FanContent.vote_count > 0).order_by(FanContent.vote_count.desc()).first()
            if top_content:
                winner = User.query.get(top_content.user_id)
            else:
                winner=None
            session_with_winners.append({"session": session,"winner": winner})
    return render_template('home.html', user=current_user, upcoming_sessions=upcoming_sessions, session_w=session_with_winners, fan_content=fan_content_for_previous)

@views.route("/vote/<int:content_user_id>/<int:content_id>", methods=["POST", "GET"])
@login_required
def vote(content_user_id, content_id):
    content = FanContent.query.get_or_404(content_id)
    if current_user.votes_remaining <= 0:
        flash(message="You have no votes left!", category="error")
        return redirect(url_for("views.home"))
    if content_user_id == current_user.id:
        flash(message="You cannot vote for your own content!", category="error")
        return redirect(url_for("views.home"))
    current_user.votes_remaining -= 1
    content.vote_count += 1
    db.session.commit()
    flash("Your vote has been recorded!", "success")
    return redirect(url_for("views.home"))

""" @views.route('/character')
@login_required
def character():
    
    return render_template('character.html', user=current_user)
 """
@views.route('/wiki')
@login_required
def wiki_index():
    root_pages = Page.query.filter_by(parent_id=None).order_by(Page.title).all()
    return render_template("wiki/index.html",page=None, pages=root_pages, user=current_user)

@views.route('/wiki/<slug>', methods=['GET', 'POST'])
@login_required
def view_page(slug):
    page = Page.query.filter_by(slug=slug).first_or_404()
    root_pages = Page.query.filter_by(parent_id=None).order_by(Page.title).all()
    if request.method == 'POST':
        text = request.form.get('text')
        parent_id = request.form.get('parent_id') or None

        if not text.strip():
            flash(message="Comment cannot be empty.", category="error")
            return redirect(url_for('views.view_page', slug=slug))

        new_comment = Comment(
            page_id=page.id,
            parent_id=parent_id,
            user_id=current_user.id,
            comment_text=text
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('views.view_page', slug=slug))

    comments = Comment.query.filter_by(page_id=page.id, parent_id=None) \
                            .order_by(Comment.created_at.asc()) \
                            .all()
    

    return render_template('wiki/view_page.html', page=page, slug=slug, pages=root_pages, user=current_user, comments=comments)

@views.route('/comment/delete/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    slug=comment.page.slug
    # Only allow deletion if current user is comment owner or admin
    if comment.user_id != current_user.id and not current_user.is_admin:
        flash(message="Comment cannot be deleted by the current user.", category="error")
        return redirect(url_for('views.view_page', slug=slug))

    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted successfully.', 'success')

    # Redirect back to the page the comment belonged to
    return redirect(url_for('views.view_page', slug=slug))



@views.route('/user-settings', methods=['GET'])
@login_required
def user_settings():
    return render_template('user_settings.html',user=current_user)

@views.route('/change-password', methods=['POST'])
@login_required
def change_password():
    current = request.form['current_password']
    new = request.form['new_password']
    confirm = request.form['confirm_password']
    if not current or not new or not confirm:
        flash(message="Please fill all fields.", category='error')
    elif not check_password_hash(current_user.password,current):
        flash(message="Current password is incorrect.", category='error')
    elif new != confirm:
        flash(message="New passwords do not match.", category='error')
    else:
        current_user.password= generate_password_hash(new)
        db.session.commit()
        flash(message="Password updated successfully!", category='success')
    return redirect(url_for('views.user_settings'))

@views.route('/change-profile-pic', methods=['POST'])
@login_required
def change_profile_pic():
    new = request.form['new_image']
    current_user.image=new
    db.session.commit()
    return redirect(url_for('views.user_settings'))

    

