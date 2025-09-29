from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy.inspection import inspect
from .models import MODELS, Rarity, Pulls, User, Rarity, Item
from . import db
from datetime import datetime
import random

pull = Blueprint('pull', __name__)

BASE_RATES = {
    Rarity.legendary: 0.002,   # 0.2% - extremely rare, and without pity
    Rarity.epic: 0.018,        # 1,8% - still rare, no pity
    Rarity.rare: 0.02,         # 2% - balanced with 60-pull guarantee
    Rarity.uncommon: 0.06,     # 6% - plenty of filler pulls
    Rarity.common: 0.90        # 90% - rounds totals to 100%
}

def get_pulled_item(user, items, pity_threshold=90, small_pity_threshold=10):
    
    if not user.pity:
        user.pity=0
    if not user.small_pity:
        user.small_pity=0
    # Pity
    if user.pity + 1 >= pity_threshold:
        rarity = Rarity.rare
    elif user.small_pity + 1 >= small_pity_threshold:
        rarity = Rarity.uncommon
    else:
        rarity = random.choices(
            population=list(BASE_RATES.keys()),
            weights=list(BASE_RATES.values()),
            k=1
        )[0]

    pool = [i for i in items if i.rarity == rarity]

    if rarity==Rarity.epic or rarity==Rarity.legendary:
        user.pity = 0
        user.small_pity = 0
    elif rarity == Rarity.rare:
        user.pity = 0
        user.small_pity = 0
    elif rarity == Rarity.uncommon:
        user.small_pity = 0
    else:
        user.pity += 1
        user.small_pity += 1
    if not pool:
        flash(message="no items in category", category="error")
        return None
    # Choose random item from the pool
    pulled_item = random.choice(pool)
    return pulled_item

@pull.route('/pull-page', methods=['GET','POST'])
@login_required
def pull_page():
    logs = Pulls.query.filter_by(user_id=current_user.id).order_by(Pulls.pull_time.desc()).limit(20).all()
    return render_template('pull.html', user=current_user, logs=logs)

@pull.route('/pull/<int:amount>', methods=['POST'])
@login_required
def pulling_js(amount=1):
    if(current_user.tokens<=0):
        flash(message="You dont have enough tokens, but nice try!")
        return None
    items = Item.query.filter_by(pullable=True).all()
    pulled_items = []
    
    for i in range(amount):
        pulled_item = get_pulled_item(current_user, items, 60, 10)
        if not pulled_item:
            return jsonify({'error': 'No items available'}), 400
        log = Pulls(user_id=current_user.id, gatcha_id=pulled_item.id)
        db.session.add(log)
        pulled_items.append({
            'name': pulled_item.name,
            'rarity': pulled_item.rarity.name.lower(),
            'image': pulled_item.image,
            'pulled_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'description': pulled_item.description
        })
    
    current_user.tokens -= amount
    db.session.commit()
    
    return jsonify({'pulled_items': pulled_items, 'tokens': current_user.tokens,'pity': current_user.pity,'smallPity':current_user.small_pity})

@pull.route('/pull-history/<int:no>', methods=['GET'])
@login_required
def pull_hystory(no=20):
    logs = Pulls.query.filter_by(user_id=current_user.id).order_by(Pulls.pull_time.desc()).limit(no).all()
    history=[]
    for log in logs:
        history.append({
            'name': log.item.name,
            'rarity': log.item.rarity.name.lower(),
            'image': log.item.image,
            'pulled_at': log.pull_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(history)
