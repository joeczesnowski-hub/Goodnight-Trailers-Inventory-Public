from flask import Blueprint, redirect, url_for, session, request

# Create blueprint
category_bp = Blueprint('category', __name__)

@category_bp.route('/switch_category/<category>')
def switch_category(category):
    if category in ['trailers', 'trucks', 'classic_cars']:
        session['category'] = category
    
    # Check if coming from React page
    if request.referrer and 'react-inventory' in request.referrer:
        return redirect(url_for('react_inventory'))
    
    return redirect(url_for('index'))