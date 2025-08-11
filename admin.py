from flask import Blueprint, render_template, redirect, url_for, flash
from website.models import User, db
from website.decorators import admin_required
from flask_login import current_user, login_required


admin = Blueprint('admin', __name__)

@admin.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.all()
    return render_template('admin_dashboard.html', user=current_user, users=users)

@admin.route('/admin/delete/<int:user_id>', methods=['POST'])
@admin_required
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.is_admin:
        flash("You can't delete another admin.", "danger")
        return redirect(url_for('admin.admin_dashboard'))

    db.session.delete(user)
    db.session.commit()
    flash("User deleted.", "success")
    return redirect(url_for('admin.admin_dashboard'))
