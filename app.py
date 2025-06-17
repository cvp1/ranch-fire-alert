# app.py - Flask application with HTTP only (no SSL complexity)
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, messaging
import os
from datetime import datetime
import json
import logging
from werkzeug.serving import WSGIRequestHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///fire_alerts.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
db = SQLAlchemy(app)

# Custom request handler to suppress socket errors
class QuietWSGIRequestHandler(WSGIRequestHandler):
    def log_error(self, format, *args):
        if "Socket is not connected" not in str(args):
            super().log_error(format, *args)

# Initialize Firebase Admin SDK
firebase_initialized = False
try:
    firebase_key_path = os.getenv('FIREBASE_KEY_PATH', 'firebase-key.json')
    if os.path.exists(firebase_key_path):
        cred = credentials.Certificate(firebase_key_path)
        firebase_admin.initialize_app(cred)
        firebase_initialized = True
        logger.info("Firebase initialized successfully")
    else:
        logger.warning(f"{firebase_key_path} not found. Creating dummy file...")
        # Create a dummy Firebase key file for development
        dummy_key = {
            "type": "service_account",
            "project_id": os.getenv('FIREBASE_PROJECT_ID', 'your-project-id'),
            "private_key_id": "dummy",
            "private_key": "-----BEGIN PRIVATE KEY-----\nDUMMY\n-----END PRIVATE KEY-----\n",
            "client_email": f"dummy@{os.getenv('FIREBASE_PROJECT_ID', 'your-project')}.iam.gserviceaccount.com",
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
    phone = db.Column(db.String(20), nullable=True)
    fcm_token = db.Column(db.String(500), nullable=True)
    ranch_id = db.Column(db.Integer, db.ForeignKey('ranch.id'), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
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
    fire_alert_id = db.Column(db.Integer, db.ForeignKey('fire_alert.id'), nullable=False)
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    animal_type = db.Column(db.String(50), nullable=False)
    animal_count = db.Column(db.Integer, nullable=False)
    pickup_location = db.Column(db.String(200), nullable=False)
    contact_info = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='open')
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Error handlers
@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Not found'}), 404

# API Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """Return frontend configuration from environment variables"""
    config = {
        'firebase': {
            'apiKey': os.getenv('FIREBASE_API_KEY'),
            'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN'),
            'projectId': os.getenv('FIREBASE_PROJECT_ID'),
            'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
            'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
            'appId': os.getenv('FIREBASE_APP_ID')
        },
        'vapidKey': os.getenv('FIREBASE_VAPID_KEY')
    }
    
    # Check if all required Firebase config is present
    firebase_config_complete = all([
        config['firebase']['apiKey'],
        config['firebase']['authDomain'],
        config['firebase']['projectId'],
        config['firebase']['messagingSenderId'],
        config['firebase']['appId'],
        config['vapidKey']
    ])
    
    if not firebase_config_complete:
        logger.warning("Incomplete Firebase configuration in environment variables")
        # Return dummy config for development
        config = {
            'firebase': {
                'apiKey': 'demo-api-key',
                'authDomain': 'demo-project.firebaseapp.com',
                'projectId': 'demo-project',
                'storageBucket': 'demo-project.appspot.com',
                'messagingSenderId': '123456789',
                'appId': '1:123456789:web:demo'
            },
            'vapidKey': 'demo-vapid-key'
        }
    
    return jsonify(config)

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        'status': 'running',
        'firebase_enabled': firebase_initialized,
        'database_connected': True,
        'https_enabled': request.is_secure,
        'config_loaded': bool(os.getenv('FIREBASE_API_KEY')),
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        required_fields = ['name', 'ranch_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        user = User(
            name=data['name'],
            phone=data.get('phone'),
            fcm_token=data.get('fcm_token'),
            ranch_id=data['ranch_id']
        )
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"User registered: {user.name} (ID: {user.id})")
        return jsonify({'success': True, 'user_id': user.id})
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Registration failed'}), 500

@app.route('/api/ranches', methods=['GET'])
def get_ranches():
    try:
        ranches = Ranch.query.all()
        return jsonify([{
            'id': r.id,
            'name': r.name,
            'latitude': r.latitude,
            'longitude': r.longitude
        } for r in ranches])
    except Exception as e:
        logger.error(f"Error getting ranches: {e}")
        return jsonify({'success': False, 'error': 'Failed to get ranches'}), 500

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    try:
        ranch_id = request.args.get('ranch_id')
        if ranch_id:
            alerts = FireAlert.query.filter_by(ranch_id=ranch_id, status='active').all()
        else:
            alerts = FireAlert.query.filter_by(status='active').all()
        
        return jsonify([{
            'id': alert.id,
            'title': alert.title,
            'message': alert.message,
            'severity': alert.severity,
            'status': alert.status,
            'latitude': alert.latitude,
            'longitude': alert.longitude,
            'created_at': alert.created_at.isoformat()
        } for alert in alerts])
        
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return jsonify({'success': False, 'error': 'Failed to get alerts'}), 500

@app.route('/api/alerts', methods=['POST'])
def create_alert():
    try:
        data = request.get_json()
        alert = FireAlert(
            title=data['title'],
            message=data['message'],
            ranch_id=data['ranch_id'],
            severity=data.get('severity', 'medium'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            created_by=data['user_id']
        )
        
        db.session.add(alert)
        db.session.commit()
        
        send_fire_alert_notification(alert)
        
        logger.info(f"Fire alert created: {alert.title} (ID: {alert.id})")
        return jsonify({'success': True, 'alert_id': alert.id})
        
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to create alert'}), 500

@app.route('/api/livestock-requests', methods=['POST'])
def create_livestock_request():
    try:
        data = request.get_json()
        request_obj = LivestockRequest(
            fire_alert_id=data['fire_alert_id'],
            requester_id=data['user_id'],
            animal_type=data['animal_type'],
            animal_count=data['animal_count'],
            pickup_location=data['pickup_location'],
            contact_info=data['contact_info'],
            notes=data.get('notes')
        )
        
        db.session.add(request_obj)
        db.session.commit()
        
        send_livestock_request_notification(request_obj)
        
        logger.info(f"Livestock request created: {request_obj.id}")
        return jsonify({'success': True, 'request_id': request_obj.id})
        
    except Exception as e:
        logger.error(f"Error creating livestock request: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to create livestock request'}), 500

@app.route('/api/livestock-requests', methods=['GET'])
def get_livestock_requests():
    try:
        fire_alert_id = request.args.get('fire_alert_id')
        requests = LivestockRequest.query.filter_by(fire_alert_id=fire_alert_id).all()
        
        return jsonify([{
            'id': req.id,
            'animal_type': req.animal_type,
            'animal_count': req.animal_count,
            'pickup_location': req.pickup_location,
            'contact_info': req.contact_info,
            'status': req.status,
            'notes': req.notes,
            'created_at': req.created_at.isoformat()
        } for req in requests])
        
    except Exception as e:
        logger.error(f"Error getting livestock requests: {e}")
        return jsonify({'success': False, 'error': 'Failed to get livestock requests'}), 500

# Static file routes
@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def service_worker():
    return send_from_directory('static', 'sw.js')

@app.route('/icon-192.png')
def icon_192():
    return send_from_directory('static/icons', 'icon-192.png')

@app.route('/icon-512.png')
def icon_512():
    return send_from_directory('static/icons', 'icon-512.png')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static/icons', 'icon-192.png')

# Push notification functions
def send_fire_alert_notification(alert):
    if not firebase_initialized:
        logger.warning("Firebase not initialized - skipping notification")
        return
        
    try:
        ranch = Ranch.query.get(alert.ranch_id)
        users = User.query.filter_by(ranch_id=ranch.id).all()
        tokens = [user.fcm_token for user in users if user.fcm_token]
        
        if not tokens:
            logger.warning("No FCM tokens found for notification")
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

def send_livestock_request_notification(livestock_request):
    if not firebase_initialized:
        return
        
    try:
        fire_alert = FireAlert.query.get(livestock_request.fire_alert_id)
        ranch = Ranch.query.get(fire_alert.ranch_id)
        users = User.query.filter_by(ranch_id=ranch.id).all()
        tokens = [user.fcm_token for user in users if user.fcm_token]
        
        if not tokens:
            return
        
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=f"🐄 Livestock Help Needed - {ranch.name}",
                body=f"Need help moving {livestock_request.animal_count} {livestock_request.animal_type}"
            ),
            data={
                'request_id': str(livestock_request.id),
                'fire_alert_id': str(fire_alert.id),
                'type': 'livestock_request'
            },
            tokens=tokens
        )
        
        response = messaging.send_multicast(message)
        logger.info(f"Livestock notification - Success: {response.success_count}, Failures: {response.failure_count}")
        
    except Exception as e:
        logger.error(f"Failed to send livestock notification: {e}")

# Initialize database
def create_tables():
    with app.app_context():
        db.create_all()
        
        if Ranch.query.count() == 0:
            sample_ranches = [
                Ranch(name="Dragoon Mountain Ranch", latitude=34.0522, longitude=-118.2437, radius_miles=10.0),
                Ranch(name="Mountain View Ranch", latitude=34.1522, longitude=-118.3437, radius_miles=8.0),
                Ranch(name="Desert Springs Ranch", latitude=33.9522, longitude=-118.1437, radius_miles=12.0)
            ]
            
            for ranch in sample_ranches:
                db.session.add(ranch)
            
            db.session.commit()
            logger.info(f"Created {len(sample_ranches)} sample ranches")

if __name__ == '__main__':
    create_tables()
    
    # Configuration from environment variables
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
        threaded=True,
        request_handler=QuietWSGIRequestHandler
    )