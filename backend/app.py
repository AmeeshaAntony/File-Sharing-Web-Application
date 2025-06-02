from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import timedelta, datetime

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fileshare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this in production
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROFILE_PHOTOS_FOLDER'] = 'profile_photos'

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROFILE_PHOTOS_FOLDER'], exist_ok=True)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    profile_photo = db.Column(db.String(255))
    files = db.relationship('File', backref='owner', lazy=True)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    shared_with = db.relationship('SharedFile', backref='file', lazy=True)

class SharedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=False)
    shared_with_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    shared_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

# Routes
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.form
        
        # Check if email already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Handle profile photo upload
        profile_photo = None
        if 'profile_photo' in request.files:
            photo = request.files['profile_photo']
            if photo.filename != '':
                filename = secure_filename(photo.filename)
                photo_path = os.path.join(app.config['PROFILE_PHOTOS_FOLDER'], filename)
                photo.save(photo_path)
                profile_photo = filename

        # Create new user
        user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date(),
            phone_number=data['phone_number'],
            profile_photo=profile_photo
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'User created successfully'}), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if user and check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'profile_photo': user.profile_photo
            }
        }), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/upload', methods=['POST'])
@jwt_required()
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        user_id = get_jwt_identity()
        new_file = File(
            filename=filename,
            original_filename=filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            user_id=user_id
        )
        
        db.session.add(new_file)
        db.session.commit()
        
        return jsonify({'message': 'File uploaded successfully'}), 201

@app.route('/api/files', methods=['GET'])
@jwt_required()
def get_files():
    user_id = get_jwt_identity()
    files = File.query.filter_by(user_id=user_id).all()
    
    return jsonify([{
        'id': file.id,
        'filename': file.original_filename,
        'size': file.file_size,
        'upload_date': file.upload_date.isoformat()
    } for file in files]), 200

@app.route('/api/files/<int:file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    user_id = get_jwt_identity()
    file = File.query.filter_by(id=file_id, user_id=user_id).first()
    
    if not file:
        return jsonify({'error': 'File not found'}), 404
    
    os.remove(file.file_path)
    db.session.delete(file)
    db.session.commit()
    
    return jsonify({'message': 'File deleted successfully'}), 200

@app.route('/api/share', methods=['POST'])
@jwt_required()
def share_file():
    data = request.get_json()
    user_id = get_jwt_identity()
    
    file = File.query.filter_by(id=data['file_id'], user_id=user_id).first()
    if not file:
        return jsonify({'error': 'File not found'}), 404
    
    shared_user = User.query.filter_by(email=data['email']).first()
    if not shared_user:
        return jsonify({'error': 'User not found'}), 404
    
    shared_file = SharedFile(file_id=file.id, shared_with_id=shared_user.id)
    db.session.add(shared_file)
    db.session.commit()
    
    return jsonify({'message': 'File shared successfully'}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 