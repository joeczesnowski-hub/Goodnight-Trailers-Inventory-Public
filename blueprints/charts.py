from flask import Blueprint, render_template, session
from flask_login import login_required, current_user
from functools import wraps

# Create blueprint
charts_bp = Blueprint('charts', __name__)

def financial_required(f):
    """Decorator to check financial permissions for charts"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.has_financial_permission():
            from flask import flash, redirect, url_for
            flash('Financial permission required to view charts')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@charts_bp.route('/charts/react')
@login_required
@financial_required
def react_charts():
    category = session.get('category', 'inventory')
    return render_template('react_charts.html', current_category=category)