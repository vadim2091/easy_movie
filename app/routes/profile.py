from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import User, UserTask, Transaction, Withdrawal
from app.forms import ProfileForm
from datetime import datetime
import os
import secrets

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.username = form.username.data
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
    
    # Заявки на вывод
    withdrawals = Withdrawal.query.filter_by(user_id=current_user.id)\
        .order_by(Withdrawal.created_at.desc())\
        .limit(5)\
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
                         withdrawals=withdrawals,
                         stats=stats)

@profile_bp.route('/upload-avatar', methods=['POST'])
@login_required
def upload_avatar():
    if 'avatar' not in request.files:
        return {'success': False, 'error': 'Нет файла'}
    
    file = request.files['avatar']
    if file.filename == '':
        return {'success': False, 'error': 'Файл не выбран'}
    
    if file:
        filename = secure_filename(file.filename)
        ext = filename.split('.')[-1]
        new_filename = f"avatar_{current_user.id}_{secrets.token_hex(8)}.{ext}"
        
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        file.save(os.path.join(upload_folder, new_filename))
        
        if current_user.avatar != 'default.jpg':
            try:
                old_file = os.path.join(upload_folder, current_user.avatar)
                if os.path.exists(old_file):
                    os.remove(old_file)
            except:
                pass
        
        current_user.avatar = new_filename
        db.session.commit()
        return {'success': True, 'avatar': new_filename}
    
    return {'success': False, 'error': 'Ошибка загрузки'}

@profile_bp.route('/withdraw', methods=['POST'])
@login_required
def withdraw():
    amount = request.form.get('amount', type=int)
    if not amount or amount < 500:
        flash('Минимальная сумма вывода 500 мандаринов.', 'danger')
        return redirect(url_for('profile.profile'))
    if current_user.balance < amount:
        flash('Недостаточно средств.', 'danger')
        return redirect(url_for('profile.profile'))
    
    withdrawal = Withdrawal(
        user_id=current_user.id,
        amount=amount,
        status='pending'
    )
    db.session.add(withdrawal)
    # Замораживаем сумму
    current_user.balance -= amount
    current_user.hold_balance += amount
    db.session.commit()
    
    flash('Заявка на вывод создана. Ожидайте подтверждения.', 'success')
    return redirect(url_for('profile.profile'))