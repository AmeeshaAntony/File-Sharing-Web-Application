from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import timedelta, datetime
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import secrets # Import secrets module

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fileshare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this in production
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROFILE_PHOTOS_FOLDER'] = 'profile_photos'
app.config['SECRET_KEY'] = 'b7b6e0135582657a393275bc2d77dee6cb56462af64082da0eb68b09acd275dc' # Add a secret key for token generation

# Email Configuration (UPDATE WITH YOUR EMAIL DETAILS)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ameesha468@gmail.com' # Replace with your email
app.config['MAIL_PASSWORD'] = 'amlu opqj bawp cyfe' # Replace with your app password
app.config['MAIL_DEFAULT_SENDER'] = 'ameesha468@gmail.com' # Replace with your email
app.config['SECURITY_PASSWORD_SALT'] = '1167cb3d941a0f31d7586466e3774dd01ddd36e3dbc63343d7ba4239c0c406cc' # Replace with your generated secret

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
mail = Mail(app)
s = URLSafeTimedSerializer(app.config['SECURITY_PASSWORD_SALT'])

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
    reset_token = db.Column(db.String(128), unique=True, nullable=True)
    reset_token_expiration = db.Column(db.DateTime, nullable=True)
    files = db.relationship('File', backref='owner', lazy=True)

    # Method to get a reset token
    def get_reset_token(self, expires_sec=1800): # Token expires in 30 minutes
        self.reset_token = secrets.token_hex(16)
        self.reset_token_expiration = datetime.utcnow() + timedelta(seconds=expires_sec)
        db.session.commit()
        return self.reset_token

    # Method to verify a reset token
    @staticmethod
    def verify_reset_token(token):
        user = User.query.filter_by(reset_token=token).first()
        if user and user.reset_token_expiration > datetime.utcnow():
            return user
        return None

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

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    print("Endpoint hit")
    email = request.json.get('email')
    user = User.query.filter_by(email=email).first()
    
    if not user:
        print("User not found")
        return jsonify({'message': 'If your email address is in our database, you will receive a password recovery link at that email address.'}), 200

    try:
        print("User found, generating token...")
        token = user.get_reset_token()
        print(f"Generated token: {token}")

        reset_link = f"http://localhost:3000/reset-password/{token}"
        print(f"Reset link: {reset_link}")
        
        msg = Message('Password Reset Request', recipients=[user.email])
        msg.body = f'To reset your password, visit the following link: {reset_link}\n\nIf you did not make this request, simply ignore this email.\n'
        
        print("Sending mail...")
        mail.send(msg)
        print("Mail sent successfully")

        return jsonify({'message': 'If your email address is in our database, you will receive a password recovery link at that email address.'}), 200

    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({'message': 'If your email address is in our database, you will receive a password recovery link at that email address.'}), 200

@app.route('/api/reset-password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    user = User.verify_reset_token(token)
    if not user:
        return jsonify({'error': 'Invalid or expired token'}), 400

    if request.method == 'POST':
        data = request.get_json()
        password = data.get('password')
        
        if not password:
             return jsonify({'error': 'Password is required'}), 400

        user.password_hash = generate_password_hash(password)
        user.reset_token = None
        user.reset_token_expiration = None
        db.session.commit()

        return jsonify({'message': 'Password has been reset!'}), 200
    else:
        # For GET request, frontend can use this to check token validity
        return jsonify({'message': 'Valid token'}), 200

@app.route('/api/upload', methods=['POST'])
@jwt_required()
def upload_file():
    try:
        print("Incoming request files:", request.files)
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        uploaded_files = request.files.getlist('file')
        if not uploaded_files or all(f.filename == '' for f in uploaded_files):
            return jsonify({'error': 'No selected file'}), 400

        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        for file in uploaded_files:
            if file.filename == '':
                continue

            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            user_id = get_jwt_identity()
            new_file = File(
                filename=filename,
                original_filename=file.filename,
                file_path=file_path,
                file_size=os.path.getsize(file_path),
                user_id=user_id
            )

            db.session.add(new_file)
            db.session.commit()

        return jsonify({'message': 'Files uploaded successfully'}), 201
    
    except Exception as e:
        print("Upload error:", str(e))
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/files', methods=['GET'])
@jwt_required()
def get_files():
    user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_term = request.args.get('search', type=str)

    query = File.query.filter_by(user_id=user_id)

    if search_term:
        query = query.filter(File.original_filename.ilike(f'%{search_term}%'))

    total_files = query.count()
    files = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return jsonify({
        'files': [{
            'id': file.id,
            'filename': file.original_filename,
            'size': file.file_size,
            'upload_date': file.upload_date.isoformat()
        } for file in files],
        'total_files': total_files,
        'per_page': per_page,
        'current_page': page
    }), 200

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

@app.route('/api/files/<int:file_id>/download', methods=['GET'])
@jwt_required()
def download_file(file_id):
    user_id = get_jwt_identity()
    file = File.query.filter_by(id=file_id, user_id=user_id).first()

    if not file:
        return jsonify({'error': 'File not found or unauthorized'}), 404

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found on server'}), 404

    return send_from_directory(app.config['UPLOAD_FOLDER'], file.filename, as_attachment=True, download_name=file.original_filename)

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
        return jsonify({'error': 'Recipient user not found'}), 404

    # Check if already shared
    already_shared = SharedFile.query.filter_by(file_id=file.id, shared_with_id=shared_user.id).first()
    if already_shared:
        return jsonify({'message': 'File already shared with this user'}), 200

    shared_file = SharedFile(
        file_id=file.id,
        shared_with_id=shared_user.id
    )
    
    db.session.add(shared_file)
    db.session.commit()
    
    return jsonify({'message': f'File shared successfully with {shared_user.email}'}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 