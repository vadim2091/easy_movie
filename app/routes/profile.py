from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import User, UserTask, Transaction
from app.forms import ProfileForm
from datetime import datetime

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.phone = form.phone.data
        current_user.birth_date = form.birth_date.data
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        flash('Профиль обновлен!', 'success')
        return redirect(url_for('profile.profile'))
    
    # Статистика
    user_tasks = UserTask.query.filter_by(user_id=current_user.id).all()
    tasks_done = UserTask.query.filter_by(user_id=current_user.id, status='approved').count()
    total_earned = sum([t.task.reward for t in user_tasks if t.status == 'approved'])
    pending_earned = UserTask.query.filter_by(user_id=current_user.id, status='pending').count()
    referral_count = User.query.filter_by(referrer_id=current_user.id).count()
    
    # Транзакции
    transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.created_at.desc())\
        .limit(10)\
        .all()
    
    stats = {
        'tasks_done': tasks_done,
        'total_earned': total_earned,
        'pending_earned': pending_earned,
        'referral_count': referral_count
    }
    
    return render_template('profile.html', 
                         form=form, 
                         user_tasks=user_tasks,
                         transactions=transactions,
                         stats=stats)