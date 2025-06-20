#!/usr/bin/env python3
"""
Ranch Fire Alert PWA - Complete Backend with Login System
Fixed SQLAlchemy 2.0+ compatibility and improved error handling
"""

import os
import json
import hashlib
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

# Database configuration - SQLite only
data_dir = os.path.join(os.getcwd(), 'data')
os.makedirs(data_dir, exist_ok=True)
sqlite_path = os.path.join(data_dir, 'fire_alerts.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{sqlite_path}'
logger.info(f"Using SQLite database at {sqlite_path}")
logger.info("SQLite database will persist if using Railway volumes")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# Initialize extensions
db = SQLAlchemy(app)

# Firebase initialization
firebase_initialized = False
try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    
    firebase_key_path = 'firebase-key.json'
    
    if os.path.exists(firebase_key_path):
        cred = credentials.Certificate(firebase_key_path)
        firebase_admin.initialize_app(cred)
        firebase_initialized = True
        logger.info("Firebase initialized successfully")
    else:
        logger.warning(f"Firebase key file not found at {firebase_key_path}")
        # Create dummy file for demo
        dummy_key = {
            "type": "service_account",
            "project_id": os.getenv('FIREBASE_PROJECT_ID', 'dmr-fns'),
            "private_key_id": "dummy",
            "private_key": "-----BEGIN PRIVATE KEY-----\\nDUMMY\\n-----END PRIVATE KEY-----\\n",
            "client_email": f"dummy@{os.getenv('FIREBASE_PROJECT_ID', 'dmr-fns')}.iam.gserviceaccount.com",
            "client_id": "dummy",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
        with open(firebase_key_path, 'w') as f:
            json.dump(dummy_key, f, indent=2)
        logger.info(f"Created dummy {firebase_key_path} - replace with real credentials")
        
except Exception as e:
    logger.error(f"Firebase initialization failed: {e}")

# Database Models
class Ranch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    radius_miles = db.Column(db.Float, default=5.0)
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(128), nullable=True)
    fcm_token = db.Column(db.String(500), nullable=True)
    ranch_id = db.Column(db.Integer, db.ForeignKey('ranch.id'), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FireAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    ranch_id = db.Column(db.Integer, db.ForeignKey('ranch.id'), nullable=False)
    severity = db.Column(db.String(20), default='medium')
    status = db.Column(db.String(20), default='active')
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class LivestockRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    animal_type = db.Column(db.String(50), nullable=False)
    animal_count = db.Column(db.Integer, nullable=False)
    urgency_level = db.Column(db.String(20), default='medium')
    details = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Helper functions for authentication
def simple_hash(password):
    """Simple password hashing for demo purposes"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify password against hash"""
    return simple_hash(password) == password_hash

# Error handlers
@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Not found'}), 404

# Main Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/firebase-messaging-sw.js')
def firebase_sw():
    """Serve the Firebase messaging service worker"""
    from flask import send_from_directory
    return send_from_directory('static', 'firebase-messaging-sw.js', mimetype='application/javascript')

@app.route('/favicon.ico')
def favicon():
    """Serve the favicon"""
    from flask import send_from_directory
    return send_from_directory('static/icons', 'icon-192.png', mimetype='image/png')

@app.route('/apple-touch-icon.png')
def apple_touch_icon():
    """Serve Apple touch icon"""
    from flask import send_from_directory
    return send_from_directory('static/icons', 'icon-192.png', mimetype='image/png')

@app.route('/apple-touch-icon-precomposed.png')
def apple_touch_icon_precomposed():
    """Serve Apple touch icon precomposed"""
    from flask import send_from_directory
    return send_from_directory('static/icons', 'icon-192.png', mimetype='image/png')

@app.route('/static/icons/icon-72.png')
def icon_72():
    """Serve the 72px icon (fallback to 192px)"""
    from flask import send_from_directory
    return send_from_directory('static/icons', 'icon-192.png', mimetype='image/png')

@app.route('/api/config', methods=['GET'])
def get_config():
    """Return frontend configuration from environment variables"""
    config = {
        'firebase': {
            'apiKey': os.getenv('FIREBASE_API_KEY', 'AIzaSyCWIvA2I6kzqokVpq5gjGlMj03Gp3Hwe3E'),
            'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN', 'dmr-fns.firebaseapp.com'),
            'projectId': os.getenv('FIREBASE_PROJECT_ID', 'dmr-fns'),
            'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET', 'dmr-fns.firebasestorage.app'),
            'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID', '668810466125'),
            'appId': os.getenv('FIREBASE_APP_ID', '1:668810466125:web:aeb977be6046bc45d3dd04')
        },
        'vapidKey': os.getenv('FIREBASE_VAPID_KEY', 'BMQhfotmIce_250TfjNABeg-l_OPWwe2ghk_BwKL0pmyPVVyEsCiaAHniErBw8pw7RJnMp9kD5oU3DDG1Tlod2k')
    }
    
    return jsonify(config)

@app.route('/api/status', methods=['GET'])
def status():
    # Get database info
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    db_path = db_uri.replace('sqlite:///', '')
    db_info = f"SQLite at {db_path}"
    
    return jsonify({
        'status': 'running',
        'firebase_enabled': firebase_initialized,
        'database_connected': True,
        'database_type': 'SQLite',
        'database_info': db_info,
        'database_url_set': False,  # Always false since we only use SQLite
        'use_sqlite': True,  # Always true since we only use SQLite
        'https_enabled': request.is_secure,
        'config_loaded': bool(os.getenv('FIREBASE_API_KEY')),
        'timestamp': datetime.utcnow().isoformat()
    })

# User Authentication Routes
@app.route('/api/check-user', methods=['POST'])
def check_user():
    """Check if a user exists by email or phone"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
            
        identifier = data.get('identifier', '').strip()
        
        if not identifier:
            return jsonify({'success': True, 'exists': False})
        
        user = None
        if '@' in identifier:
            user = User.query.filter_by(email=identifier.lower()).first()
        else:
            user = User.query.filter_by(phone=identifier).first()
        
        if user:
            # Use SQLAlchemy 2.0+ compatible syntax
            ranch = db.session.get(Ranch, user.ranch_id)
            return jsonify({
                'success': True,
                'exists': True,
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'phone': user.phone,
                    'ranch_name': ranch.name if ranch else 'Unknown Ranch',
                    'has_password': bool(user.password_hash),
                    'is_admin': user.is_admin
                }
            })
        else:
            return jsonify({'success': True, 'exists': False})
            
    except Exception as e:
        logger.error(f"Check user error: {e}")
        return jsonify({'success': False, 'error': f'Check user failed: {str(e)}'}), 500

@app.route('/api/login', methods=['POST'])
def login_user():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        identifier = data.get('identifier', '').strip()
        password = data.get('password', '')
        
        if not identifier:
            return jsonify({'success': False, 'error': 'Email or phone required'}), 400
        
        # Find user by email or phone
        user = None
        if '@' in identifier:
            user = User.query.filter_by(email=identifier.lower()).first()
        else:
            user = User.query.filter_by(phone=identifier).first()
        
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Check password if user has one
        if user.password_hash:
            if not password:
                return jsonify({'success': False, 'error': 'Password required'}), 400
            if not verify_password(password, user.password_hash):
                return jsonify({'success': False, 'error': 'Invalid password'}), 401
        
        # Update FCM token if provided
        if data.get('fcm_token'):
            user.fcm_token = data['fcm_token']
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Get ranch info using SQLAlchemy 2.0+ syntax
        ranch = db.session.get(Ranch, user.ranch_id)
        
        logger.info(f"User logged in: {user.name} (ID: {user.id})")
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'ranch_id': user.ranch_id,
                'ranch_name': ranch.name if ranch else 'Unknown Ranch',
                'is_admin': user.is_admin
            }
        })
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'success': False, 'error': f'Login failed: {str(e)}'}), 500

@app.route('/api/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip() if data.get('email') else None
        phone = data.get('phone', '').strip() if data.get('phone') else None
        password = data.get('password', '').strip() if data.get('password') else None
        ranch_id = data.get('ranch_id')
        
        # Validation
        if not name:
            return jsonify({'success': False, 'error': 'Name is required'}), 400
        
        if not email and not phone:
            return jsonify({'success': False, 'error': 'Email or phone number is required'}), 400
        
        if not ranch_id:
            return jsonify({'success': False, 'error': 'Ranch selection is required'}), 400
        
        # Check if user already exists
        existing_user = None
        if email:
            existing_user = User.query.filter_by(email=email.lower()).first()
        if not existing_user and phone:
            existing_user = User.query.filter_by(phone=phone).first()
        
        if existing_user:
            return jsonify({'success': False, 'error': 'User already exists with this email or phone'}), 400
        
        # Verify ranch exists using SQLAlchemy 2.0+ syntax
        ranch = db.session.get(Ranch, ranch_id)
        if not ranch:
            return jsonify({'success': False, 'error': 'Invalid ranch selection'}), 400
        
        # Create new user
        user = User(
            name=name,
            email=email.lower() if email else None,
            phone=phone,
            password_hash=simple_hash(password) if password else None,
            ranch_id=ranch_id,
            fcm_token=data.get('fcm_token'),
            is_admin=False
        )
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"New user registered: {user.name} (ID: {user.id})")
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'ranch_id': user.ranch_id,
                'ranch_name': ranch.name,
                'is_admin': user.is_admin
            }
        })
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Registration failed: {str(e)}'}), 500

@app.route('/api/ranches', methods=['GET'])
def get_ranches():
    try:
        ranches = Ranch.query.all()
        return jsonify({
            'success': True,
            'ranches': [{
                'id': ranch.id,
                'name': ranch.name,
                'latitude': ranch.latitude,
                'longitude': ranch.longitude,
                'radius_miles': ranch.radius_miles
            } for ranch in ranches]
        })
    except Exception as e:
        logger.error(f"Error getting ranches: {e}")
        return jsonify({'success': False, 'error': 'Failed to get ranches'}), 500

# Alert Management Routes
@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    try:
        user_id = request.args.get('user_id')
        
        if user_id:
            # Get alerts for user's ranch using SQLAlchemy 2.0+ syntax
            user = db.session.get(User, user_id)
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            alerts = FireAlert.query.filter_by(ranch_id=user.ranch_id).order_by(FireAlert.created_at.desc()).all()
        else:
            # Get all active alerts
            alerts = FireAlert.query.filter_by(status='active').order_by(FireAlert.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'alerts': [{
                'id': alert.id,
                'title': alert.title,
                'message': alert.message,
                'severity': alert.severity,
                'status': alert.status,
                'latitude': alert.latitude,
                'longitude': alert.longitude,
                'created_at': alert.created_at.isoformat(),
                'updated_at': alert.updated_at.isoformat()
            } for alert in alerts]
        })
        
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return jsonify({'success': False, 'error': 'Failed to get alerts'}), 500

@app.route('/api/alerts', methods=['POST'])
def create_alert():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        title = data.get('title', '').strip()
        message = data.get('message', '').strip()
        severity = data.get('severity', 'medium')
        ranch_id = data.get('ranch_id')
        user_id = data.get('user_id')
        
        if not title or not message:
            return jsonify({'success': False, 'error': 'Title and message are required'}), 400
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID required'}), 400
        
        # Verify user exists and get ranch_id if not provided
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Use user's ranch if ranch_id not specified
        if not ranch_id:
            ranch_id = user.ranch_id
        
        # Verify ranch exists
        ranch = db.session.get(Ranch, ranch_id)
        if not ranch:
            return jsonify({'success': False, 'error': 'Ranch not found'}), 404
        
        # Create alert
        alert = FireAlert(
            title=title,
            message=message,
            ranch_id=ranch_id,
            severity=severity,
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            created_by=user_id
        )
        
        db.session.add(alert)
        db.session.commit()
        
        # Send push notifications if Firebase is enabled
        if firebase_initialized:
            send_fire_alert_notification(alert)
        
        logger.info(f"Alert created: {alert.title} (ID: {alert.id})")
        return jsonify({
            'success': True,
            'alert': {
                'id': alert.id,
                'title': alert.title,
                'message': alert.message,
                'severity': alert.severity,
                'created_at': alert.created_at.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Failed to create alert: {str(e)}'}), 500

@app.route('/api/alerts/<int:alert_id>', methods=['GET'])
def get_alert(alert_id):
    """Get a single alert by ID"""
    try:
        alert = db.session.get(FireAlert, alert_id)
        if not alert:
            return jsonify({'success': False, 'error': 'Alert not found'}), 404
        
        creator = db.session.get(User, alert.created_by)
        ranch = db.session.get(Ranch, alert.ranch_id)
        
        return jsonify({
            'success': True,
            'alert': {
                'id': alert.id,
                'title': alert.title,
                'message': alert.message,
                'severity': alert.severity,
                'status': alert.status,
                'latitude': alert.latitude,
                'longitude': alert.longitude,
                'created_at': alert.created_at.isoformat(),
                'updated_at': alert.updated_at.isoformat(),
                'creator_name': creator.name if creator else 'Unknown User',
                'ranch_name': ranch.name if ranch else 'Unknown Ranch'
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting alert: {e}")
        return jsonify({'success': False, 'error': 'Failed to get alert'}), 500

@app.route('/api/alerts/<int:alert_id>', methods=['PUT'])
def update_alert(alert_id):
    """Update an existing alert"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Get the alert
        alert = db.session.get(FireAlert, alert_id)
        if not alert:
            return jsonify({'success': False, 'error': 'Alert not found'}), 404
        
        # Update fields if provided
        if 'title' in data:
            alert.title = data['title'].strip()
        if 'message' in data:
            alert.message = data['message'].strip()
        if 'severity' in data:
            alert.severity = data['severity']
        if 'status' in data:
            alert.status = data['status']
        
        alert.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Alert updated: {alert.title} (ID: {alert.id})")
        return jsonify({
            'success': True,
            'alert': {
                'id': alert.id,
                'title': alert.title,
                'message': alert.message,
                'severity': alert.severity,
                'status': alert.status,
                'updated_at': alert.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error updating alert: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Failed to update alert: {str(e)}'}), 500

@app.route('/api/alerts/<int:alert_id>', methods=['DELETE'])
def delete_alert(alert_id):
    """Delete an alert"""
    try:
        # Get the alert
        alert = db.session.get(FireAlert, alert_id)
        if not alert:
            return jsonify({'success': False, 'error': 'Alert not found'}), 404
        
        # Delete the alert
        db.session.delete(alert)
        db.session.commit()
        
        logger.info(f"Alert deleted: {alert.title} (ID: {alert.id})")
        return jsonify({'success': True, 'message': 'Alert deleted successfully'})
        
    except Exception as e:
        logger.error(f"Error deleting alert: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Failed to delete alert: {str(e)}'}), 500

# Livestock Request Routes
@app.route('/api/livestock-requests', methods=['GET'])
def get_livestock_requests():
    try:
        user_id = request.args.get('user_id')
        
        if user_id:
            # Get requests for user's ranch
            user = db.session.get(User, user_id)
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            # Get all users in the same ranch to include their requests
            ranch_users = User.query.filter_by(ranch_id=user.ranch_id).all()
            user_ids = [u.id for u in ranch_users]
            
            requests = LivestockRequest.query.filter(LivestockRequest.user_id.in_(user_ids)).order_by(LivestockRequest.created_at.desc()).all()
        else:
            requests = LivestockRequest.query.order_by(LivestockRequest.created_at.desc()).all()
        
        # Format requests with user names
        request_list = []
        for req in requests:
            user = db.session.get(User, req.user_id)
            request_list.append({
                'id': req.id,
                'user_id': req.user_id,
                'user_name': user.name if user else 'Unknown User',
                'animal_type': req.animal_type,
                'animal_count': req.animal_count,
                'urgency_level': req.urgency_level,
                'details': req.details,
                'status': req.status,
                'created_at': req.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'requests': request_list
        })
        
    except Exception as e:
        logger.error(f"Error getting livestock requests: {e}")
        return jsonify({'success': False, 'error': 'Failed to get livestock requests'}), 500

@app.route('/api/livestock-requests', methods=['POST'])
def create_livestock_request():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        user_id = data.get('user_id')
        animal_type = data.get('animal_type', '').strip()
        animal_count = data.get('animal_count')
        urgency_level = data.get('urgency_level', 'medium')
        details = data.get('details', '').strip()
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID required'}), 400
        
        if not animal_type or not animal_count or not details:
            return jsonify({'success': False, 'error': 'Animal type, count, and details are required'}), 400
        
        # Verify user exists
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Create livestock request
        livestock_request = LivestockRequest(
            user_id=user_id,
            animal_type=animal_type,
            animal_count=animal_count,
            urgency_level=urgency_level,
            details=details
        )
        
        db.session.add(livestock_request)
        db.session.commit()
        
        logger.info(f"Livestock request created: {animal_type} x{animal_count} by user {user_id}")
        return jsonify({
            'success': True,
            'request': {
                'id': livestock_request.id,
                'animal_type': livestock_request.animal_type,
                'animal_count': livestock_request.animal_count,
                'urgency_level': livestock_request.urgency_level,
                'details': livestock_request.details,
                'created_at': livestock_request.created_at.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error creating livestock request: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Failed to create livestock request: {str(e)}'}), 500

@app.route('/api/livestock-requests/<int:request_id>/help', methods=['POST'])
def offer_help(request_id):
    """Offer help for a livestock request"""
    try:
        data = request.get_json()
        helper_user_id = data.get('user_id') if data else None
        
        if not helper_user_id:
            return jsonify({'success': False, 'error': 'User ID required'}), 400
        
        # Get the livestock request
        livestock_request = db.session.get(LivestockRequest, request_id)
        if not livestock_request:
            return jsonify({'success': False, 'error': 'Livestock request not found'}), 404
        
        # Get helper user
        helper_user = db.session.get(User, helper_user_id)
        if not helper_user:
            return jsonify({'success': False, 'error': 'Helper user not found'}), 404
        
        # Get requester user
        requester_user = db.session.get(User, livestock_request.user_id)
        if not requester_user:
            return jsonify({'success': False, 'error': 'Requester user not found'}), 404
        
        # For now, just log the help offer
        # In a full implementation, you might create a help_offers table
        logger.info(f"Help offered: {helper_user.name} offered to help {requester_user.name} with {livestock_request.animal_type}")
        
        return jsonify({
            'success': True,
            'message': f'Help offer sent to {requester_user.name}'
        })
        
    except Exception as e:
        logger.error(f"Error offering help: {e}")
        return jsonify({'success': False, 'error': f'Failed to offer help: {str(e)}'}), 500

# Admin Routes
@app.route('/api/admin/stats', methods=['GET'])
def get_admin_stats():
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID required'}), 400
        
        user = db.session.get(User, user_id)
        if not user or not user.is_admin:
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
        
        # Get statistics
        total_users = User.query.count()
        total_alerts = FireAlert.query.count()
        active_alerts = FireAlert.query.filter_by(status='active').count()
        resolved_alerts = FireAlert.query.filter_by(status='resolved').count()
        livestock_requests = LivestockRequest.query.count()
        active_ranches = Ranch.query.count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_users': total_users,
                'total_alerts': total_alerts,
                'active_alerts': active_alerts,
                'resolved_alerts': resolved_alerts,
                'livestock_requests': livestock_requests,
                'active_ranches': active_ranches
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting admin stats: {e}")
        return jsonify({'success': False, 'error': 'Failed to get statistics'}), 500

@app.route('/api/admin/alerts', methods=['GET'])
def get_admin_alerts():
    """Get all alerts for admin management"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID required'}), 400
        
        user = db.session.get(User, user_id)
        if not user or not user.is_admin:
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
        
        # Get all alerts with creator and ranch information
        alerts = FireAlert.query.order_by(FireAlert.created_at.desc()).all()
        
        alert_list = []
        for alert in alerts:
            creator = db.session.get(User, alert.created_by)
            ranch = db.session.get(Ranch, alert.ranch_id)
            
            alert_list.append({
                'id': alert.id,
                'title': alert.title,
                'message': alert.message,
                'severity': alert.severity,
                'status': alert.status,
                'latitude': alert.latitude,
                'longitude': alert.longitude,
                'created_at': alert.created_at.isoformat(),
                'updated_at': alert.updated_at.isoformat(),
                'creator_name': creator.name if creator else 'Unknown User',
                'ranch_name': ranch.name if ranch else 'Unknown Ranch'
            })
        
        return jsonify({
            'success': True,
            'alerts': alert_list
        })
        
    except Exception as e:
        logger.error(f"Error getting admin alerts: {e}")
        return jsonify({'success': False, 'error': 'Failed to get alerts'}), 500

@app.route('/api/admin/alerts/<int:alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id):
    """Resolve an alert"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID required'}), 400
        
        user = db.session.get(User, user_id)
        if not user or not user.is_admin:
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
        
        alert = db.session.get(FireAlert, alert_id)
        if not alert:
            return jsonify({'success': False, 'error': 'Alert not found'}), 404
        
        alert.status = 'resolved'
        alert.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Alert resolved: {alert.title} (ID: {alert.id}) by admin {user.name}")
        return jsonify({
            'success': True,
            'message': 'Alert resolved successfully',
            'alert': {
                'id': alert.id,
                'status': alert.status,
                'updated_at': alert.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error resolving alert: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Failed to resolve alert: {str(e)}'}), 500

@app.route('/api/admin/alerts/<int:alert_id>/reopen', methods=['POST'])
def reopen_alert(alert_id):
    """Re-open a resolved alert"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID required'}), 400
        
        user = db.session.get(User, user_id)
        if not user or not user.is_admin:
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
        
        alert = db.session.get(FireAlert, alert_id)
        if not alert:
            return jsonify({'success': False, 'error': 'Alert not found'}), 404
        
        alert.status = 'active'
        alert.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Alert reopened: {alert.title} (ID: {alert.id}) by admin {user.name}")
        return jsonify({
            'success': True,
            'message': 'Alert reopened successfully',
            'alert': {
                'id': alert.id,
                'status': alert.status,
                'updated_at': alert.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error reopening alert: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Failed to reopen alert: {str(e)}'}), 500

@app.route('/api/admin/database/backup', methods=['POST'])
def admin_backup_database():
    """Create a database backup (admin only)"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID required'}), 400
        
        user = db.session.get(User, user_id)
        if not user or not user.is_admin:
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
        
        backup_file = backup_database()
        
        if backup_file:
            return jsonify({
                'success': True,
                'message': 'Database backup created successfully',
                'backup_file': backup_file
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create backup'
            }), 500
        
    except Exception as e:
        logger.error(f"Error creating database backup: {e}")
        return jsonify({'success': False, 'error': f'Failed to create backup: {str(e)}'}), 500

@app.route('/api/admin/database/status', methods=['GET'])
def admin_database_status():
    """Get database status and info (admin only)"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID required'}), 400
        
        user = db.session.get(User, user_id)
        if not user or not user.is_admin:
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
        
        # Get database info
        db_info = {
            'type': 'SQLite',
            'uri': app.config['SQLALCHEMY_DATABASE_URI'].replace('://', '://***:***@') if '@' in app.config['SQLALCHEMY_DATABASE_URI'] else app.config['SQLALCHEMY_DATABASE_URI'],
            'tables': [],
            'backups': []
        }
        
        # Get table info
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            db_info['tables'] = inspector.get_table_names()
        except Exception as e:
            logger.error(f"Error getting table info: {e}")
        
        # Get backup info (for SQLite)
        if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
            try:
                import glob
                import os
                data_dir = os.path.join(os.getcwd(), 'data')
                backup_dir = os.path.join(data_dir, 'backups')
                
                if os.path.exists(backup_dir):
                    backup_files = glob.glob(os.path.join(backup_dir, 'fire_alerts_backup_*.db'))
                    db_info['backups'] = [
                        {
                            'filename': os.path.basename(f),
                            'size': os.path.getsize(f),
                            'modified': datetime.fromtimestamp(os.path.getmtime(f)).isoformat()
                        }
                        for f in backup_files
                    ]
            except Exception as e:
                logger.error(f"Error getting backup info: {e}")
        
        return jsonify({
            'success': True,
            'database': db_info
        })
        
    except Exception as e:
        logger.error(f"Error getting database status: {e}")
        return jsonify({'success': False, 'error': f'Failed to get database status: {str(e)}'}), 500

# Push Notification Functions
def send_fire_alert_notification(alert):
    if not firebase_initialized:
        return
        
    try:
        # Get ranch and users
        ranch = db.session.get(Ranch, alert.ranch_id)
        if not ranch:
            return
            
        users = User.query.filter_by(ranch_id=ranch.id).all()
        tokens = [user.fcm_token for user in users if user.fcm_token]
        
        if not tokens:
            return
        
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=f"🔥 FIRE ALERT - {alert.severity.upper()}",
                body=alert.message
            ),
            data={
                'alert_id': str(alert.id),
                'severity': alert.severity,
                'ranch_name': ranch.name,
                'type': 'fire_alert'
            },
            tokens=tokens
        )
        
        response = messaging.send_multicast(message)
        logger.info(f"FCM Response - Success: {response.success_count}, Failures: {response.failure_count}")
        
    except Exception as e:
        logger.error(f"Failed to send fire alert notification: {e}")

# Database backup and recovery functions
def backup_database():
    """Create a backup of the database"""
    try:
        import shutil
        from datetime import datetime
        
        data_dir = os.path.join(os.getcwd(), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Create backup directory
        backup_dir = os.path.join(data_dir, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
            # SQLite backup
            source_db = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            backup_file = os.path.join(backup_dir, f'fire_alerts_backup_{timestamp}.db')
            
            if os.path.exists(source_db):
                shutil.copy2(source_db, backup_file)
                logger.info(f"Database backup created: {backup_file}")
                return backup_file
        else:
            # PostgreSQL backup (would need pg_dump in production)
            logger.info("PostgreSQL backup would require pg_dump utility")
            return None
            
    except Exception as e:
        logger.error(f"Database backup failed: {e}")
        return None

def restore_database(backup_file):
    """Restore database from backup"""
    try:
        import shutil
        
        # SQLite restore
        target_db = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        if os.path.exists(backup_file):
            shutil.copy2(backup_file, target_db)
            logger.info(f"Database restored from: {backup_file}")
            return True
        else:
            logger.error(f"Backup file not found: {backup_file}")
            return False
            
    except Exception as e:
        logger.error(f"Database restore failed: {e}")
        return False

def cleanup_old_backups(max_backups=10):
    """Clean up old backup files, keeping only the most recent ones"""
    try:
        import glob
        from datetime import datetime
        
        data_dir = os.path.join(os.getcwd(), 'data')
        backup_dir = os.path.join(data_dir, 'backups')
        
        if not os.path.exists(backup_dir):
            return
        
        # Get all backup files
        backup_files = glob.glob(os.path.join(backup_dir, 'fire_alerts_backup_*.db'))
        
        if len(backup_files) > max_backups:
            # Sort by modification time (oldest first)
            backup_files.sort(key=os.path.getmtime)
            
            # Remove oldest files
            files_to_remove = backup_files[:-max_backups]
            for file_path in files_to_remove:
                os.remove(file_path)
                logger.info(f"Removed old backup: {file_path}")
                
    except Exception as e:
        logger.error(f"Backup cleanup failed: {e}")

# Initialize database
def create_tables():
    with app.app_context():
        try:
            # Test database connection using SQLAlchemy 2.0+ syntax
            with db.engine.connect() as conn:
                conn.execute(db.text("SELECT 1"))
                conn.commit()
            logger.info("Database connection successful")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return
        
        # Create backup before making changes
        backup_database()
        
        db.create_all()
        
        # Update existing database schema if needed
        try:
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            
            # Check if User table exists and get its columns
            try:
                user_columns = [column['name'] for column in inspector.get_columns('user')]
                logger.info(f"Current User table columns: {user_columns}")
            except Exception:
                # Table doesn't exist, will be created by db.create_all()
                user_columns = []
            
            # Use SQLAlchemy 2.0+ compatible syntax
            if user_columns and 'email' not in user_columns:
                logger.info("Adding email column to User table")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE "user" ADD COLUMN email VARCHAR(120)'))
                    conn.commit()
            
            if user_columns and 'password_hash' not in user_columns:
                logger.info("Adding password_hash column to User table")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE "user" ADD COLUMN password_hash VARCHAR(128)'))
                    conn.commit()
                
            if user_columns and 'last_login' not in user_columns:
                logger.info("Adding last_login column to User table")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE "user" ADD COLUMN last_login TIMESTAMP'))
                    conn.commit()
                    
            if user_columns and 'is_admin' not in user_columns:
                logger.info("Adding is_admin column to User table")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE "user" ADD COLUMN is_admin BOOLEAN DEFAULT FALSE'))
                    conn.commit()
                    
            if user_columns and 'created_at' not in user_columns:
                logger.info("Adding created_at column to User table")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE "user" ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP'))
                    conn.commit()
            
            # Check and migrate LivestockRequest table
            if 'livestock_request' in inspector.get_table_names():
                livestock_columns = [column['name'] for column in inspector.get_columns('livestock_request')]
                logger.info(f"Current LivestockRequest table columns: {livestock_columns}")
                
                # Migrate from old schema if needed
                if 'requester_id' in livestock_columns and 'user_id' not in livestock_columns:
                    logger.info("Migrating LivestockRequest from old schema to new schema")
                    
                    with db.engine.connect() as conn:
                        # Add new columns
                        conn.execute(text('ALTER TABLE livestock_request ADD COLUMN user_id INTEGER'))
                        
                        if 'urgency_level' not in livestock_columns:
                            conn.execute(text('ALTER TABLE livestock_request ADD COLUMN urgency_level VARCHAR(20) DEFAULT \'medium\''))
                        
                        if 'details' not in livestock_columns:
                            conn.execute(text('ALTER TABLE livestock_request ADD COLUMN details TEXT'))
                        
                        # Copy data from old columns
                        conn.execute(text('UPDATE livestock_request SET user_id = requester_id WHERE user_id IS NULL'))
                        
                        # Set default values for new columns
                        if 'notes' in livestock_columns:
                            conn.execute(text('UPDATE livestock_request SET details = COALESCE(notes, \'Help needed\') WHERE details IS NULL'))
                        else:
                            conn.execute(text('UPDATE livestock_request SET details = \'Help needed\' WHERE details IS NULL'))
                        
                        conn.commit()
                        logger.info("LivestockRequest migration completed")
                
        except Exception as e:
            logger.info(f"Database schema update not needed or failed: {e}")
        
        # Create sample ranch if none exist
        if Ranch.query.count() == 0:
            dragoon_ranch = Ranch(
                name="Dragoon Mountain Ranch", 
                latitude=31.9190, 
                longitude=-109.9673, 
                radius_miles=10.0
            )
            
            db.session.add(dragoon_ranch)
            db.session.commit()
            logger.info("Created Dragoon Mountain Ranch")
        else:
            logger.info(f"Found {Ranch.query.count()} existing ranches")

        # Create admin user if none exists
        if not User.query.filter_by(is_admin=True).first():
            admin_ranch = Ranch.query.first()
            if admin_ranch:
                admin_user = User(
                    name="Admin User",
                    email="admin@ranch.local",
                    password_hash=simple_hash("admin123"),
                    ranch_id=admin_ranch.id,
                    is_admin=True
                )
                db.session.add(admin_user)
                db.session.commit()
                logger.info("Created admin user: admin@ranch.local / admin123")
        
        # Clean up old backups
        cleanup_old_backups()
        
        logger.info("Database initialization completed successfully")

# --- User Management (Admin) ---
@app.route('/api/admin/users', methods=['GET'])
def admin_list_users():
    """List all users (admin only)"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID required'}), 400
        
        user = db.session.get(User, user_id)
        if not user or not user.is_admin:
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
        
        users = User.query.order_by(User.created_at.desc()).all()
        user_list = []
        
        for u in users:
            ranch = db.session.get(Ranch, u.ranch_id)
            user_list.append({
                'id': u.id,
                'name': u.name,
                'email': u.email,
                'phone': u.phone,
                'ranch_id': u.ranch_id,
                'ranch_name': ranch.name if ranch else 'Unknown Ranch',
                'is_admin': u.is_admin,
                'last_login': u.last_login.isoformat() if u.last_login else None,
                'created_at': u.created_at.isoformat() if u.created_at else None
            })
        
        logger.info(f"Admin {user.name} listed {len(user_list)} users")
        return jsonify({'success': True, 'users': user_list})
        
    except Exception as e:
        logger.error(f"List users error: {e}")
        return jsonify({'success': False, 'error': f'Failed to list users: {str(e)}'}), 500

@app.route('/api/admin/users/<int:target_user_id>', methods=['GET'])
def admin_get_user(target_user_id):
    """Get a single user by ID (admin only)"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID required'}), 400
        
        admin_user = db.session.get(User, user_id)
        if not admin_user or not admin_user.is_admin:
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
        
        user = db.session.get(User, target_user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        ranch = db.session.get(Ranch, user.ranch_id)
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'ranch_id': user.ranch_id,
                'ranch_name': ranch.name if ranch else 'Unknown Ranch',
                'is_admin': user.is_admin,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
        })
        
    except Exception as e:
        logger.error(f"Get user error: {e}")
        return jsonify({'success': False, 'error': f'Failed to get user: {str(e)}'}), 500

@app.route('/api/admin/users', methods=['POST'])
def admin_add_user():
    """Add a new user (admin only)"""
    try:
        user_id = request.args.get('user_id')
        admin_user = db.session.get(User, user_id)
        if not admin_user or not admin_user.is_admin:
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Debug logging - show raw data
        logger.info(f"Raw request data: {data}")
        logger.info(f"Data type: {type(data)}")
        logger.info(f"Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip() if data.get('email') else None
        phone = data.get('phone', '').strip() if data.get('phone') else None
        password = data.get('password', '').strip() if data.get('password') else None
        ranch_id = data.get('ranch_id')
        is_admin = bool(data.get('is_admin', False))
        
        # Debug logging - show extracted values
        logger.info(f"Extracted values:")
        logger.info(f"  name: '{name}' (type: {type(name)}, empty: {not name})")
        logger.info(f"  email: '{email}' (type: {type(email)})")
        logger.info(f"  phone: '{phone}' (type: {type(phone)})")
        logger.info(f"  ranch_id: {ranch_id} (type: {type(ranch_id)})")
        logger.info(f"  is_admin: {is_admin}")
        
        # Convert ranch_id to int if it's a string
        if ranch_id and isinstance(ranch_id, str):
            try:
                ranch_id = int(ranch_id)
                logger.info(f"Converted ranch_id from string to int: {ranch_id}")
            except ValueError:
                logger.error(f"Failed to convert ranch_id '{ranch_id}' to int")
                return jsonify({'success': False, 'error': 'Invalid ranch ID format'}), 400
        
        # Debug logging - show final values
        logger.info(f"Final processed values:")
        logger.info(f"  name: '{name}' (empty: {not name})")
        logger.info(f"  email: '{email}'")
        logger.info(f"  phone: '{phone}'")
        logger.info(f"  ranch_id: {ranch_id} (type: {type(ranch_id)})")
        
        # Validation with detailed logging
        if not name:
            logger.error("Validation failed: name is empty")
            return jsonify({'success': False, 'error': 'Name is required'}), 400
        else:
            logger.info("Name validation passed")
        
        if not email and not phone:
            logger.error("Validation failed: neither email nor phone provided")
            return jsonify({'success': False, 'error': 'Email or phone number is required'}), 400
        else:
            logger.info("Email/phone validation passed")
        
        if not ranch_id or ranch_id == 0:
            logger.error(f"Validation failed: ranch_id is {ranch_id}")
            return jsonify({'success': False, 'error': 'Ranch selection is required'}), 400
        else:
            logger.info("Ranch validation passed")
        
        # Check for existing user
        if email and User.query.filter_by(email=email.lower()).first():
            return jsonify({'success': False, 'error': 'Email already in use'}), 400
        if phone and User.query.filter_by(phone=phone).first():
            return jsonify({'success': False, 'error': 'Phone already in use'}), 400
        
        # Verify ranch exists
        ranch = db.session.get(Ranch, ranch_id)
        if not ranch:
            return jsonify({'success': False, 'error': 'Invalid ranch selection'}), 400
        
        # Create new user
        user = User(
            name=name,
            email=email.lower() if email else None,
            phone=phone,
            password_hash=simple_hash(password) if password else None,
            ranch_id=ranch_id,
            is_admin=is_admin
        )
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"Admin created new user: {user.name} (ID: {user.id})")
        return jsonify({
            'success': True, 
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'ranch_id': user.ranch_id,
                'ranch_name': ranch.name,
                'is_admin': user.is_admin,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
        })
        
    except Exception as e:
        logger.error(f"Add user error: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Failed to add user: {str(e)}'}), 500

@app.route('/api/admin/users/<int:edit_user_id>', methods=['PUT'])
def admin_edit_user(edit_user_id):
    """Edit a user (admin only)"""
    try:
        user_id = request.args.get('user_id')
        admin_user = db.session.get(User, user_id)
        if not admin_user or not admin_user.is_admin:
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        user = db.session.get(User, edit_user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Update fields if provided
        if 'name' in data:
            name = data['name'].strip()
            if not name:
                return jsonify({'success': False, 'error': 'Name cannot be empty'}), 400
            user.name = name
        
        if 'email' in data:
            email = data['email'].strip() if data['email'] else None
            if email and email.lower() != user.email:
                if User.query.filter_by(email=email.lower()).first():
                    return jsonify({'success': False, 'error': 'Email already in use'}), 400
                user.email = email.lower()
            elif not email:
                user.email = None
        
        if 'phone' in data:
            phone = data['phone'].strip() if data['phone'] else None
            if phone and phone != user.phone:
                if User.query.filter_by(phone=phone).first():
                    return jsonify({'success': False, 'error': 'Phone already in use'}), 400
                user.phone = phone
            elif not phone:
                user.phone = None
        
        if 'password' in data:
            password = data['password'].strip() if data['password'] else None
            if password:
                user.password_hash = simple_hash(password)
            else:
                user.password_hash = None
        
        if 'ranch_id' in data:
            ranch_id = data['ranch_id']
            
            # Convert ranch_id to int if it's a string
            if ranch_id and isinstance(ranch_id, str):
                try:
                    ranch_id = int(ranch_id)
                except ValueError:
                    return jsonify({'success': False, 'error': 'Invalid ranch ID format'}), 400
            
            if ranch_id and ranch_id != 0:
                ranch = db.session.get(Ranch, ranch_id)
                if not ranch:
                    return jsonify({'success': False, 'error': 'Invalid ranch selection'}), 400
                user.ranch_id = ranch_id
            else:
                return jsonify({'success': False, 'error': 'Ranch selection is required'}), 400
        
        if 'is_admin' in data:
            user.is_admin = bool(data['is_admin'])
        
        # Ensure user has at least email or phone
        if not user.email and not user.phone:
            return jsonify({'success': False, 'error': 'User must have either email or phone number'}), 400
        
        db.session.commit()
        
        # Get ranch info for response
        ranch = db.session.get(Ranch, user.ranch_id)
        
        logger.info(f"Admin updated user: {user.name} (ID: {user.id})")
        return jsonify({
            'success': True, 
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'ranch_id': user.ranch_id,
                'ranch_name': ranch.name if ranch else 'Unknown Ranch',
                'is_admin': user.is_admin,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
        })
        
    except Exception as e:
        logger.error(f"Edit user error: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Failed to edit user: {str(e)}'}), 500

@app.route('/api/admin/users/<int:delete_user_id>', methods=['DELETE'])
def admin_delete_user(delete_user_id):
    """Delete a user (admin only)"""
    try:
        user_id = request.args.get('user_id')
        admin_user = db.session.get(User, user_id)
        if not admin_user or not admin_user.is_admin:
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
        user = db.session.get(User, delete_user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True, 'message': 'User deleted'})
    except Exception as e:
        logger.error(f"Delete user error: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Failed to delete user: {str(e)}'}), 500

if __name__ == '__main__':
    create_tables()
    
    port = int(os.getenv('PORT', 8088))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    logger.info(f"🌐 Starting HTTP server on http://localhost:{port}")
    logger.info("📱 Note: PWA features (install, notifications) require HTTPS")
    logger.info("🔧 For full PWA testing, use ngrok or deploy with HTTPS")
    
    app.run(
        debug=debug,
        host=host,
        port=port,
        threaded=True
    )