from flask_mail import Mail, Message
from flask import current_app, render_template_string
import os

mail = Mail()

def init_mail(app):
    """Initialize Flask-Mail with app configuration from database"""
    try:
        import sqlite3
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT setting_key, setting_value FROM smtp_settings')
        settings = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        
        app.config['MAIL_SERVER'] = settings.get('mail_server', 'smtp.gmail.com')
        app.config['MAIL_PORT'] = int(settings.get('mail_port', 587))
        app.config['MAIL_USE_TLS'] = settings.get('mail_use_tls', 'True') == 'True'
        app.config['MAIL_USERNAME'] = settings.get('mail_username', '')
        app.config['MAIL_PASSWORD'] = settings.get('mail_password', '')
        app.config['MAIL_DEFAULT_SENDER'] = settings.get('mail_default_sender', '')
    except Exception as e:
        # Fallback to environment variables if database fails
        app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
        app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
        app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
        app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
        app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
        app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
    
    mail.init_app(app)
    return mail

# REPLACE get_recipients() with these two functions:
def get_new_item_recipients():
    """Get list of users who should receive new item alerts"""
    try:
        import sqlite3
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT email 
            FROM users 
            WHERE email IS NOT NULL 
            AND email != '' 
            AND is_active = 1
            AND receive_new_item_emails = 1
        ''')
        
        emails = [row[0] for row in cursor.fetchall()]
        conn.close()
        return emails
        
    except Exception as e:
        current_app.logger.error(f"Error getting new item recipients: {e}")
        return []

def get_sold_item_recipients():
    """Get list of users who should receive sold item alerts"""
    try:
        import sqlite3
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT email 
            FROM users 
            WHERE email IS NOT NULL 
            AND email != '' 
            AND is_active = 1
            AND receive_sold_item_emails = 1
        ''')
        
        emails = [row[0] for row in cursor.fetchall()]
        conn.close()
        return emails
        
    except Exception as e:
        current_app.logger.error(f"Error getting sold item recipients: {e}")
        return []

def send_new_item_alert(item_data):
    """Send email alert when new inventory item is added"""
    recipients = get_new_item_recipients()  # CHANGED THIS LINE
    if not recipients:
        current_app.logger.warning("No alert recipients configured")
        return False
    
    # ... rest stays exactly the same ...
    try:
        subject = f"New Inventory Added: {item_data.get('year', '')} {item_data.get('make', '')} {item_data.get('type', '')}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f8f9fa; padding: 20px; border: 1px solid #dee2e6; border-radius: 0 0 8px 8px; }}
                .item-details {{ background: white; padding: 15px; border-radius: 8px; margin-top: 15px; }}
                .detail-row {{ display: flex; padding: 8px 0; border-bottom: 1px solid #f0f0f0; }}
                .detail-label {{ font-weight: bold; width: 150px; color: #555; }}
                .detail-value {{ flex: 1; color: #333; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2 style="margin: 0;">🚛 New Inventory Alert</h2>
                    <p style="margin: 5px 0 0 0;">A new item has been added to your inventory</p>
                </div>
                <div class="content">
                    <div class="item-details">
                        <div class="detail-row">
                            <span class="detail-label">Length:</span>
                            <span class="detail-value">{item_data.get('length', 'N/A')} FT</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Year:</span>
                            <span class="detail-value">{item_data.get('year', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Make:</span>
                            <span class="detail-value">{item_data.get('make', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Type:</span>
                            <span class="detail-value">{item_data.get('type', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Hitch Type:</span>
                            <span class="detail-value">{item_data.get('hitch_type', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Dimensions:</span>
                            <span class="detail-value">{item_data.get('dimensions', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Capacity:</span>
                            <span class="detail-value">{item_data.get('capacity', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Description:</span>
                            <span class="detail-value">{item_data.get('description', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Condition:</span>
                            <span class="detail-value">{item_data.get('condition', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">VIN:</span>
                            <span class="detail-value">{item_data.get('vin', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Color:</span>
                            <span class="detail-value">{item_data.get('color', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Purchase Price:</span>
                            <span class="detail-value">${item_data.get('purchase_price', '0')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Sell Price:</span>
                            <span class="detail-value">${item_data.get('sell_price', '0')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Expected Profit:</span>
                            <span class="detail-value">${item_data.get('profit', '0')}</span>
                        </div>
                    </div>
                </div>
                <div class="footer">
                    <p>Goodnight Trailers Inventory Management System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg = Message(
            subject=subject,
            recipients=recipients,
            html=html_body
        )
        
        mail.send(msg)
        current_app.logger.info(f"New item alert sent to {recipients}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send new item alert: {str(e)}")
        return False

def send_item_sold_alert(item_data):
    """Send email alert when item is marked as sold"""
    current_app.logger.info(f"=== SOLD ALERT CALLED === Item data: {item_data}")
    recipients = get_sold_item_recipients()
    current_app.logger.info(f"Sold item recipients found: {recipients}")
    if not recipients:
        current_app.logger.warning("No alert recipients configured")
        return False
    
    # ... rest stays exactly the same ...
    try:
        subject = f"Item SOLD: {item_data.get('year', '')} {item_data.get('make', '')} {item_data.get('type', '')}"
        
        purchase_price = float(item_data.get('purchase_price', 0) or 0)
        sell_price = float(item_data.get('sell_price', 0) or 0)
        profit = sell_price - purchase_price
        profit_color = 'green' if profit >= 0 else 'red'
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f8f9fa; padding: 20px; border: 1px solid #dee2e6; border-radius: 0 0 8px 8px; }}
                .item-details {{ background: white; padding: 15px; border-radius: 8px; margin-top: 15px; }}
                .detail-row {{ display: flex; padding: 8px 0; border-bottom: 1px solid #f0f0f0; }}
                .detail-label {{ font-weight: bold; width: 150px; color: #555; }}
                .detail-value {{ flex: 1; color: #333; }}
                .profit-highlight {{ background: {profit_color}; color: white; padding: 10px; border-radius: 8px; text-align: center; font-size: 18px; font-weight: bold; margin-top: 15px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2 style="margin: 0;">✅ Item Sold!</h2>
                    <p style="margin: 5px 0 0 0;">An item has been marked as sold</p>
                </div>
                <div class="content">
                    <div class="item-details">
                        <div class="detail-row">
                            <span class="detail-label">Year:</span>
                            <span class="detail-value">{item_data.get('year', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Make:</span>
                            <span class="detail-value">{item_data.get('make', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Type:</span>
                            <span class="detail-value">{item_data.get('type', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Description:</span>
                            <span class="detail-value">{item_data.get('description', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">VIN:</span>
                            <span class="detail-value">{item_data.get('vin', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Purchase Price:</span>
                            <span class="detail-value">${purchase_price:,.2f}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Sell Price:</span>
                            <span class="detail-value">${sell_price:,.2f}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Sold Date:</span>
                            <span class="detail-value">{item_data.get('sold_date', 'N/A')}</span>
                        </div>
                    </div>
                    <div class="profit-highlight">
                        Profit: ${profit:,.2f}
                    </div>
                </div>
                <div class="footer">
                    <p>Goodnight Trailers Inventory Management System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg = Message(
            subject=subject,
            recipients=recipients,
            html=html_body
        )
        
        mail.send(msg)
        current_app.logger.info(f"Item sold alert sent to {recipients}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send item sold alert: {str(e)}")
        return False