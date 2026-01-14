from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from email_service import init_mail, send_new_item_alert, send_item_sold_alert
import sqlite3
import pandas as pd
from io import BytesIO
import re
from datetime import date, datetime
import json
import os
import ssl
import locale
from dotenv import load_dotenv
import logging
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from functools import wraps


# Import blueprints
from blueprints.import_data import import_bp
from blueprints.export_routes import export_bp
from blueprints.admin import admin_bp
from blueprints.category import category_bp
from blueprints.charts import charts_bp
from blueprints.inventory_api import inventory_api_bp
from blueprints.forms_api import forms_api_bp
from blueprints.google_drive_routes import google_drive_bp
from blueprints.photo_upload_routes import photo_upload_bp

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-secret-key')

# Initialize Flask-Mail
mail = init_mail(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Register blueprints
app.register_blueprint(import_bp)
app.register_blueprint(export_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(category_bp)
app.register_blueprint(charts_bp)
app.register_blueprint(inventory_api_bp)
app.register_blueprint(forms_api_bp)
app.register_blueprint(google_drive_bp)
app.register_blueprint(photo_upload_bp)

@app.before_request
def set_default_category():
    if 'category' not in session:
        session['category'] = 'trailers'

# Set up logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

# Set locale for currency formatting
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'en_US')
    except locale.Error:
        logger.warning("Could not set locale")

# Color definitions
READABLE_COLORS = [
    '#1E90FF', '#FFFF00', '#87CEEB', '#00FFFF', '#FFA500',
    '#800080', '#228B22', '#FF4500', '#00CED1', '#FFD700',
    '#9932CC', '#32CD32', '#000080', '#4682B4', '#8B4513',
    '#B0C4DE', '#20B2AA', '#FF6347', '#9370DB',
]

def assign_colors(makes):
    color_map = {}
    if 'TOP HAT' in makes:
        color_map['TOP HAT'] = '#FFFF00'
    color_index = 0
    for make in makes:
        if make not in color_map:
            color_map[make] = READABLE_COLORS[color_index % len(READABLE_COLORS)]
            color_index += 1
    return color_map

def format_currency(value):
    if value is None or (isinstance(value, float) and value != value):
        return ''
    try:
        return locale.currency(value, grouping=True)
    except (ValueError, TypeError):
        return f"${value:.2f}" if value else ''

app.jinja_env.filters['format_currency'] = format_currency

def init_db():
    try:
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                length REAL,
                year INTEGER,
                make TEXT,
                type TEXT,
                dimensions TEXT,
                capacity TEXT,
                description TEXT,
                condition TEXT,
                vin TEXT,
                color TEXT,
                hitch_type TEXT,
                sell_price REAL,
                sold TEXT,
                purchase_price REAL,
                profit REAL,
                sold_date TEXT
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

def init_users_db():
    try:
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                can_view INTEGER DEFAULT 0,
                can_edit INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] == 0:
            default_password = generate_password_hash('admin123', method='pbkdf2:sha256')
            cursor.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                         ('admin', default_password, 'admin'))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error initializing users database: {e}")
        raise

def add_delete_permission():
    """Add can_delete column to users table if it doesn't exist"""
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN can_delete INTEGER DEFAULT 0')
        # Grant delete permission to all admins
        cursor.execute('UPDATE users SET can_delete = 1 WHERE role = "admin"')
        conn.commit()
        print("Delete permission column added successfully!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column already exists")
        else:
            raise
    finally:
        conn.close()

def init_trucks_db():
    try:
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trucks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER,
                make TEXT,
                model TEXT,
                boom_height REAL,
                weight_capacity REAL,
                engine_type TEXT,
                hours INTEGER,
                vin TEXT,
                condition TEXT,
                description TEXT,
                sell_price REAL,
                sold TEXT DEFAULT 'No',
                purchase_price REAL,
                profit REAL,
                sold_date TEXT
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error initializing bucket trucks database: {e}")
        raise

def init_classic_cars_db():
    try:
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS classic_cars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER,
                make TEXT,
                model TEXT,
                mileage INTEGER,
                engine_specs TEXT,
                transmission TEXT,
                vin TEXT,
                restoration_status TEXT,
                condition TEXT,
                color TEXT,
                description TEXT,
                sell_price REAL,
                sold TEXT DEFAULT 'No',
                purchase_price REAL,
                profit REAL,
                sold_date TEXT
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error initializing classic cars database: {e}")
        raise

init_db()
init_users_db()
add_delete_permission()
init_trucks_db()
init_classic_cars_db()

class User(UserMixin):
    def __init__(self, id, username, role='user', group_id=None, group_name=None,
                 can_view=0, can_edit=0, can_view_financial=0, 
                 can_view_summary=0, can_view_sold=0, can_delete=0, 
                 receive_new_item_emails=0, receive_sold_item_emails=0, email=None):
        self.id = id
        self.username = username
        self.role = role
        self.group_id = group_id
        self.group_name = group_name
        self.can_view = can_view
        self.can_edit = can_edit
        self.can_view_financial = can_view_financial
        self.can_view_summary = can_view_summary
        self.can_view_sold = can_view_sold
        self.can_delete = can_delete
        self.receive_new_item_emails = receive_new_item_emails
        self.receive_sold_item_emails = receive_sold_item_emails
        self.email = email

    def is_admin(self):
        return self.group_name == 'Admin'
    
    def is_marketing(self):
        return self.group_name == 'Marketing'

    def has_view_permission(self):
        return self.can_view == 1
    
    def has_edit_permission(self):
        return self.can_edit == 1
    
    def has_financial_permission(self):
        return self.can_view_financial == 1
    
    def has_summary_permission(self):
        return self.can_view_summary == 1
    
    def has_sold_permission(self):
        return self.can_view_sold == 1
    
    def has_delete_permission(self):
        return self.can_delete == 1


# AnonymousUser class
class AnonymousUser(AnonymousUserMixin):
    def __init__(self):
        # Load permissions from anonymous user's group
        try:
            conn = sqlite3.connect('inventory.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT g.can_view, g.can_view_financial, g.can_view_summary, g.can_view_sold
                FROM users u
                JOIN groups g ON u.group_id = g.id
                WHERE u.username = 'anonymous'
            ''')
            result = cursor.fetchone()
            conn.close()
            if result:
                self.can_view = result[0]
                self.can_view_financial = result[1]
                self.can_view_summary = result[2]
                self.can_view_sold = result[3]
            else:
                self.can_view = 1
                self.can_view_financial = 0
                self.can_view_summary = 0
                self.can_view_sold = 0
        except:
            self.can_view = 1
            self.can_view_financial = 0
            self.can_view_summary = 0
            self.can_view_sold = 0

    def has_view_permission(self):
        return self.can_view == 1

    def has_financial_permission(self):
        return self.can_view_financial == 1

    def has_summary_permission(self):
        return self.can_view_summary == 1

    def has_sold_permission(self):
        return self.can_view_sold == 1

    def is_admin(self):
        return False

    def has_delete_permission(self):
        return False

    def has_edit_permission(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.id, u.username, u.role, u.group_id, g.name as group_name,
               g.can_view, g.can_edit, g.can_view_financial, 
               g.can_view_summary, g.can_view_sold, g.can_delete, 
               g.receive_new_item_emails, g.receive_sold_item_emails, u.email
        FROM users u
        LEFT JOIN groups g ON u.group_id = g.id
        WHERE u.id = ?
    ''', (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    if user_data:
        return User(
            id=user_data[0],
            username=user_data[1],
            role=user_data[2],
            group_id=user_data[3],
            group_name=user_data[4],
            can_view=user_data[5] or 0,
            can_edit=user_data[6] or 0,
            can_view_financial=user_data[7] or 0,
            can_view_summary=user_data[8] or 0,
            can_view_sold=user_data[9] or 0,
            can_delete=user_data[10] or 0,
            receive_new_item_emails=user_data[11] or 0,
            receive_sold_item_emails=user_data[12] or 0,
            email=user_data[13]
        )
    return None


def view_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not current_user.has_view_permission():
            flash('You do not have permission to view inventory')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def edit_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not current_user.has_edit_permission():
            flash('You do not have permission to edit inventory')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def delete_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.has_delete_permission():
            flash('Delete permission required')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def financial_required(f):
    """Decorator to check financial permissions for charts"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.has_financial_permission():
            flash('Financial permission required to view financial data')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, password_hash, is_active FROM users WHERE username = ?', (username,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data and user_data[3] == 1 and check_password_hash(user_data[2], password):
            # Update last login
            conn = sqlite3.connect('inventory.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', 
                         (datetime.now().isoformat(), user_data[0]))
            conn.commit()
            conn.close()

            # Load full user object
            user = load_user(user_data[0])
            login_user(user)
            
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('index'))
        else:
            # Return 401 for invalid credentials (React will handle the error)
            return '', 401

    # GET request - render React login page
    return render_template('react_login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/react-inventory')
def react_inventory():
    """React-based inventory page"""
    current_category = session.get('category', 'trailers')
    return render_template('react_index.html', current_category=current_category)

@app.route('/')
def index():
    """Main inventory page - React version"""
    current_category = session.get('category', 'trailers')
    view = request.args.get('view', 'unsold')
    
    # Restrict sold items view to users with sold permission
    if view == 'sold':
        if not current_user.is_authenticated or not current_user.has_sold_permission():
            flash('You do not have permission to view sold items')
            return redirect(url_for('index'))
    
    return render_template('react_index.html', current_category=current_category)

@app.route('/api/dropdown-options')
@login_required
def form_options():
    try:
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()

        cursor.execute('SELECT DISTINCT length FROM inventory WHERE length IS NOT NULL ORDER BY length ASC')
        lengths = [float(row[0]) for row in cursor.fetchall()]

        cursor.execute('SELECT DISTINCT make FROM inventory WHERE make IS NOT NULL AND make != "" ORDER BY make ASC')
        makes = [row[0] for row in cursor.fetchall()]

        cursor.execute('SELECT DISTINCT type FROM inventory WHERE type IS NOT NULL AND type != "" ORDER BY type ASC')
        types = [row[0] for row in cursor.fetchall()]

        cursor.execute('SELECT DISTINCT dimensions FROM inventory WHERE dimensions IS NOT NULL AND dimensions != "" ORDER BY dimensions ASC')
        dimensions = [row[0] for row in cursor.fetchall()]

        cursor.execute('SELECT DISTINCT capacity FROM inventory WHERE capacity IS NOT NULL AND capacity != "" ORDER BY capacity ASC')
        capacities = [row[0] for row in cursor.fetchall()]

        cursor.execute('SELECT DISTINCT condition FROM inventory WHERE condition IS NOT NULL AND condition != "" ORDER BY condition ASC')
        conditions = [row[0] for row in cursor.fetchall()]

        cursor.execute('SELECT DISTINCT color FROM inventory WHERE color IS NOT NULL AND color != "" ORDER BY color ASC')
        colors = [row[0] for row in cursor.fetchall()]

        conn.close()

        years = list(range(2000, 2051))

        return jsonify({
            'years': years,
            'lengths': lengths,
            'makes': makes,
            'types': types,
            'dimensions': dimensions,
            'capacities': capacities,
            'conditions': conditions,
            'colors': colors
        })
    except Exception as e:
        logger.error(f"Error getting form options: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/<int:item_id>')
@login_required
def get_inventory_item(item_id):
    try:
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM inventory WHERE id=?', (item_id,))
        item = cursor.fetchone()
        conn.close()

        if not item:
            return jsonify({'error': 'Item not found'}), 404

        return jsonify({
            'id': item[0],
            'length': item[1],
            'year': item[2],
            'make': item[3],
            'type': item[4],
            'dimensions': item[5],
            'capacity': item[6],
            'description': item[7],
            'condition': item[8],
            'vin': item[9],
            'color': item[10],
            'hitch_type': item[11],
            'sell_price': item[12],
            'sold': item[13],
            'purchase_price': item[14],
            'profit': item[15],
            'sold_date': item[16] if len(item) > 16 else None
        })
    except Exception as e:
        logger.error(f"Error getting inventory item: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chart_data/<chart_type>/<period>')
@login_required
def get_chart_data(chart_type, period):
    """Get aggregated inventory data for charts

    Args:
        chart_type: 'sold' or 'unsold'
        period: 'weekly', 'monthly', or 'yearly'
    """
    if not current_user.has_financial_permission():
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()

        # Get the current category from session, default to 'trailers'
        category = session.get('category', 'trailers')
        table_name = 'inventory' if category == 'trailers' else category
        sold_status = 'YES' if chart_type == 'sold' else 'No'

        # Build the appropriate SQL query based on period
        if chart_type == 'sold':
            # For sold items, aggregate by sold_date
            if period == 'weekly':
                query = f'''
                    SELECT strftime('%Y-W%W', sold_date) as period,
                           SUM(purchase_price) as purchase_total,
                           SUM(sell_price) as sale_total,
                           SUM(profit) as profit_total
                    FROM {table_name}
                    WHERE sold = ? AND sold_date IS NOT NULL AND sold_date != ''
                    GROUP BY period
                    ORDER BY period DESC
                    LIMIT 12
                '''
            elif period == 'monthly':
                query = f'''
                    SELECT strftime('%Y-%m', sold_date) as period,
                           SUM(purchase_price) as purchase_total,
                           SUM(sell_price) as sale_total,
                           SUM(profit) as profit_total
                    FROM {table_name}
                    WHERE sold = ? AND sold_date IS NOT NULL AND sold_date != ''
                    GROUP BY period
                    ORDER BY period DESC
                    LIMIT 12
                '''
            else:  # yearly
                query = f'''
                    SELECT strftime('%Y', sold_date) as period,
                           SUM(purchase_price) as purchase_total,
                           SUM(sell_price) as sale_total,
                           SUM(profit) as profit_total
                    FROM {table_name}
                    WHERE sold = ? AND sold_date IS NOT NULL AND sold_date != ''
                    GROUP BY period
                    ORDER BY period DESC
                    LIMIT 5
                '''
        else:
            # For unsold items, show current totals as a single data point
            # Since there's no date_added field, we show the current snapshot
            query = f'''
                SELECT 'Current' as period,
                       SUM(purchase_price) as purchase_total,
                       SUM(sell_price) as sale_total,
                       SUM(profit) as profit_total
                FROM {table_name}
                WHERE sold = ? OR sold IS NULL
            '''

        cursor.execute(query, (sold_status,))
        rows = cursor.fetchall()
        conn.close()

        # Format data for frontend (reverse to show chronological order)
        data = []
        for row in reversed(rows) if chart_type == 'sold' else rows:
            data.append({
                'period': row[0] if row[0] else 'Unknown',
                'purchaseTotal': round(float(row[1]) if row[1] else 0, 2),
                'salePriceTotal': round(float(row[2]) if row[2] else 0, 2),
                'profitTotal': round(float(row[3]) if row[3] else 0, 2)
            })

        return jsonify(data)

    except Exception as e:
        logger.error(f"Error getting chart data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chart_data_range/<chart_type>')
@login_required
@financial_required
def get_chart_data_range(chart_type):
    """API endpoint for chart data with custom date range"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not start_date or not end_date:
            return jsonify({'error': 'start_date and end_date are required'}), 400

        category = session.get('category', 'inventory')
        table_name = category if category in ['inventory', 'trucks', 'classic_cars'] else 'inventory'

        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()

        if chart_type == 'sold':
            sold_status = 'YES'
            # Calculate date range in days to determine granularity
            from datetime import datetime
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
            days_diff = (end - start).days

            if days_diff <= 14:
                # Daily data
                query = f'''
                    SELECT DATE(sold_date) as period,
                           SUM(purchase_price) as purchase_total,
                           SUM(sell_price) as sale_total,
                           SUM(profit) as profit_total
                    FROM {table_name}
                    WHERE sold = ?
                    AND sold_date >= ?
                    AND sold_date <= ?
                    AND sold_date IS NOT NULL
                    AND sold_date != ''
                    GROUP BY DATE(sold_date)
                    ORDER BY DATE(sold_date)
                '''
            elif days_diff <= 90:
                # Weekly data
                query = f'''
                    SELECT strftime('%Y-W%W', sold_date) as period,
                           SUM(purchase_price) as purchase_total,
                           SUM(sell_price) as sale_total,
                           SUM(profit) as profit_total
                    FROM {table_name}
                    WHERE sold = ?
                    AND sold_date >= ?
                    AND sold_date <= ?
                    AND sold_date IS NOT NULL
                    AND sold_date != ''
                    GROUP BY strftime('%Y-W%W', sold_date)
                    ORDER BY strftime('%Y-W%W', sold_date)
                '''
            elif days_diff <= 365:
                # Monthly data
                query = f'''
                    SELECT strftime('%Y-%m', sold_date) as period,
                           SUM(purchase_price) as purchase_total,
                           SUM(sell_price) as sale_total,
                           SUM(profit) as profit_total
                    FROM {table_name}
                    WHERE sold = ?
                    AND sold_date >= ?
                    AND sold_date <= ?
                    AND sold_date IS NOT NULL
                    AND sold_date != ''
                    GROUP BY strftime('%Y-%m', sold_date)
                    ORDER BY strftime('%Y-%m', sold_date)
                '''
            else:
                # Yearly data
                query = f'''
                    SELECT strftime('%Y', sold_date) as period,
                           SUM(purchase_price) as purchase_total,
                           SUM(sell_price) as sale_total,
                           SUM(profit) as profit_total
                    FROM {table_name}
                    WHERE sold = ?
                    AND sold_date >= ?
                    AND sold_date <= ?
                    AND sold_date IS NOT NULL
                    AND sold_date != ''
                    GROUP BY strftime('%Y', sold_date)
                    ORDER BY strftime('%Y', sold_date)
                '''

            cursor.execute(query, (sold_status, start_date, end_date))
        else:
            # For unsold items, aggregate by date_added
            sold_status = 'No'

            # Calculate date range to determine granularity
            from datetime import datetime
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
            days_diff = (end - start).days

            if days_diff <= 14:
                # Daily data
                query = f'''
                    SELECT DATE(date_added) as period,
                           SUM(purchase_price) as purchase_total,
                           SUM(sell_price) as sale_total,
                           SUM(profit) as profit_total
                    FROM {table_name}
                    WHERE (sold = ? OR sold IS NULL)
                    AND date_added IS NOT NULL
                    AND date_added >= ?
                    AND date_added <= ?
                    GROUP BY DATE(date_added)
                    ORDER BY DATE(date_added)
                '''
                cursor.execute(query, (sold_status, start_date, end_date))
            elif days_diff <= 90:
                # Weekly data
                query = f'''
                    SELECT strftime('%Y-W%W', date_added) as period,
                           SUM(purchase_price) as purchase_total,
                           SUM(sell_price) as sale_total,
                           SUM(profit) as profit_total
                    FROM {table_name}
                    WHERE (sold = ? OR sold IS NULL)
                    AND date_added IS NOT NULL
                    AND date_added >= ?
                    AND date_added <= ?
                    GROUP BY strftime('%Y-W%W', date_added)
                    ORDER BY strftime('%Y-W%W', date_added)
                '''
                cursor.execute(query, (sold_status, start_date, end_date))
            elif days_diff <= 365:
                # Monthly data
                query = f'''
                    SELECT strftime('%Y-%m', date_added) as period,
                           SUM(purchase_price) as purchase_total,
                           SUM(sell_price) as sale_total,
                           SUM(profit) as profit_total
                    FROM {table_name}
                    WHERE (sold = ? OR sold IS NULL)
                    AND date_added IS NOT NULL
                    AND date_added >= ?
                    AND date_added <= ?
                    GROUP BY strftime('%Y-%m', date_added)
                    ORDER BY strftime('%Y-%m', date_added)
                '''
                cursor.execute(query, (sold_status, start_date, end_date))
            else:
                # Yearly data
                query = f'''
                    SELECT strftime('%Y', date_added) as period,
                           SUM(purchase_price) as purchase_total,
                           SUM(sell_price) as sale_total,
                           SUM(profit) as profit_total
                    FROM {table_name}
                    WHERE (sold = ? OR sold IS NULL)
                    AND date_added IS NOT NULL
                    AND date_added >= ?
                    AND date_added <= ?
                    GROUP BY strftime('%Y', date_added)
                    ORDER BY strftime('%Y', date_added)
                '''
                cursor.execute(query, (sold_status, start_date, end_date))

        rows = cursor.fetchall()
        conn.close()

        # Format data for frontend
        data = []
        for row in rows:
            data.append({
                'period': row[0] if row[0] else 'Unknown',
                'purchaseTotal': round(float(row[1]) if row[1] else 0, 2),
                'salePriceTotal': round(float(row[2]) if row[2] else 0, 2),
                'profitTotal': round(float(row[3]) if row[3] else 0, 2)
            })

        return jsonify(data)

    except Exception as e:
        logger.error(f"Error getting chart data range: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/add', methods=['GET'])
@login_required
@edit_required
def add():
    category = request.args.get('category', session.get('category', 'trailers'))
    return render_template('react_add_item.html', category=category)

@app.route('/edit/<int:item_id>', methods=['GET'])
@login_required
@edit_required
def edit(item_id):
    return render_template('react_edit_item.html', item_id=item_id)

@app.route('/delete_selected', methods=['POST'])
@login_required
@edit_required
@delete_required
def delete_selected():
    category = session.get('category', 'trailers')
    table_name = 'inventory' if category == 'trailers' else category

    try:
        selected_ids = request.form.getlist('selected_items')
        if selected_ids:
            conn = sqlite3.connect('inventory.db')
            cursor = conn.cursor()
            cursor.executemany(f'DELETE FROM {table_name} WHERE id=?', [(int(id),) for id in selected_ids])
            conn.commit()
            conn.close()
            flash(f'{len(selected_ids)} item(s) deleted successfully!')
        else:
            flash('No items selected')
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error deleting items: {e}")
        flash(f'Error deleting items: {str(e)}')
        return redirect(url_for('index'))

@app.route('/edit_selected', methods=['POST'])
@login_required
def edit_selected():
    try:
        selected_ids = request.form.getlist('selected_items')
        if len(selected_ids) == 1:
            return redirect(url_for('edit', item_id=int(selected_ids[0])))
        elif len(selected_ids) == 0:
            flash('Please select one item to edit.')
        else:
            flash('Please select exactly one item to edit.')
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error in edit_selected: {e}")
        flash(f'Error: {str(e)}')
        return redirect(url_for('index'))

@app.route('/mark_sold_selected', methods=['POST'])
@login_required
@edit_required
def mark_sold_selected():
    category = session.get('category', 'trailers')
    table_name = 'inventory' if category == 'trailers' else category

    try:
        selected_ids = request.form.getlist('selected_items')
        if selected_ids:
            conn = sqlite3.connect('inventory.db')
            cursor = conn.cursor()
            current_date = date.today().isoformat()
            cursor.executemany(f'UPDATE {table_name} SET sold=?, sold_date=? WHERE id=?', [('YES', current_date, int(id)) for id in selected_ids])
            conn.commit()
            
            # Send email alerts for sold items
            try:
                for item_id in selected_ids:
                    cursor.execute(f'SELECT * FROM {table_name} WHERE id = ?', (int(item_id),))
                    item = cursor.fetchone()
                    if item:
                        item_data = {
                            'year': item[2],
                            'make': item[3],
                            'type': item[4],
                            'description': item[7],
                            'vin': item[9],
                            'purchase_price': item[14],
                            'sell_price': item[12],
                            'sold_date': current_date
                        }
                        send_item_sold_alert(item_data)
            except Exception as e:
                logger.error(f"Failed to send sold item alert: {e}")
            
            conn.close()
            flash(f'{len(selected_ids)} item(s) marked as sold!')
        else:
            flash('No items selected')
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error marking items as sold: {e}")
        flash(f'Error marking items as sold: {str(e)}')
        return redirect(url_for('index'))

@app.route('/mark_unsold_selected', methods=['POST'])
@login_required
@edit_required
def mark_unsold_selected():
    category = session.get('category', 'trailers')
    table_name = 'inventory' if category == 'trailers' else category

    try:
        selected_ids = request.form.getlist('selected_items')
        if selected_ids:
            conn = sqlite3.connect('inventory.db')
            cursor = conn.cursor()
            cursor.executemany(f'UPDATE {table_name} SET sold=?, sold_date=? WHERE id=?', [('No', None, int(id)) for id in selected_ids])
            conn.commit()
            conn.close()
            flash(f'{len(selected_ids)} item(s) marked as unsold!')
        else:
            flash('No items selected')
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error marking items as unsold: {e}")
        flash(f'Error marking items as unsold: {str(e)}')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=7777)
