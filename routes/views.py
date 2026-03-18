from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return render_template('index.html')