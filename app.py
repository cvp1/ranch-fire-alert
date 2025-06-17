# app.py - Main Flask application
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, messaging
import os
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fire_alerts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize Firebase Admin SDK
# Place your firebase service account key as 'firebase-key.json'
try:
    cred = credentials.Certificate('firebase-key.json')
    firebase_admin.initialize_app(cred)
except:
    print("Warning: Firebase credentials not found. Push notifications disabled.")

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
    severity = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    status = db.Column(db.String(20), default='active')   # active, resolved, expired
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
    status = db.Column(db.String(20), default='open')  # open, assigned, completed
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# API Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    
    user = User(
        name=data['name'],
        phone=data.get('phone'),
        fcm_token=data.get('fcm_token'),
        ranch_id=data['ranch_id']
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'success': True, 'user_id': user.id})

@app.route('/api/update-token', methods=['POST'])
def update_fcm_token():
    data = request.get_json()
    user = User.query.get(data['user_id'])
    
    if user:
        user.fcm_token = data['fcm_token']
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'User not found'}), 404

@app.route('/api/ranches', methods=['GET'])
def get_ranches():
    ranches = Ranch.query.all()
    return jsonify([{
        'id': r.id,
        'name': r.name,
        'latitude': r.latitude,
        'longitude': r.longitude
    } for r in ranches])

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
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

@app.route('/api/alerts', methods=['POST'])
def create_alert():
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
    
    # Send push notifications
    send_fire_alert_notification(alert)
    
    return jsonify({'success': True, 'alert_id': alert.id})

@app.route('/api/livestock-requests', methods=['POST'])
def create_livestock_request():
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
    
    # Notify ranch members about livestock request
    send_livestock_request_notification(request_obj)
    
    return jsonify({'success': True, 'request_id': request_obj.id})

@app.route('/api/livestock-requests', methods=['GET'])
def get_livestock_requests():
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
# Add this after your other routes
@app.route('/manifest.json')
def manifest():
    return app.send_static_file('manifest.json')

@app.route('/sw.js')
def service_worker():
    return app.send_static_file('sw.js')

@app.route('/firebase-messaging-sw.js')
def firebase_sw():
    # Firebase expects this file at root
    return app.send_static_file('sw.js')
@app.route('/icon-192.png')
def icon_192():
    return app.send_static_file('icon-192.png')

@app.route('/icon-512.png')
def icon_512():
    return app.send_static_file('icon-512.png')

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('icon-192.png')

# Push notification functions
def send_fire_alert_notification(alert):
    ranch = Ranch.query.get(alert.ranch_id)
    users = User.query.filter_by(ranch_id=ranch.id).all()
    
    tokens = [user.fcm_token for user in users if user.fcm_token]
    
    if not tokens:
        return
    
    severity_colors = {
        'low': '#FFA500',      # Orange
        'medium': '#FF4500',   # Red Orange  
        'high': '#FF0000',     # Red
        'critical': '#8B0000'  # Dark Red
    }
    
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
        android=messaging.AndroidConfig(
            notification=messaging.AndroidNotification(
                color=severity_colors.get(alert.severity, '#FF4500'),
                priority='high',
                sound='default'
            )
        ),
        tokens=tokens
    )
    
    try:
        response = messaging.send_multicast(message)
        print(f"Successfully sent fire alert to {response.success_count} devices")
    except Exception as e:
        print(f"Error sending push notification: {e}")

def send_livestock_request_notification(livestock_request):
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
    
    try:
        response = messaging.send_multicast(message)
        print(f"Successfully sent livestock request to {response.success_count} devices")
    except Exception as e:
        print(f"Error sending livestock notification: {e}")

# Initialize database

def create_tables():
    with app.app_context():
        db.create_all()
        
        # Create sample ranch if none exist
        if Ranch.query.count() == 0:
            sample_ranch = Ranch(
                name="Valley Ranch",
                latitude=34.0522,
                longitude=-118.2437,
                radius_miles=10.0
            )
            db.session.add(sample_ranch)
            db.session.commit()

if __name__ == '__main__':
    create_tables()
    # Add these parameters for better mobile compatibility
    app.run(
        debug=True, 
        host='0.0.0.0', 
        port=8088, 
        threaded=True,
        use_reloader=False  # This can help with mobile connections
    )
