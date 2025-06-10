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
import pytz

app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"],
        "supports_credentials": True
    }
})

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fileshare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this in production
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROFILE_PHOTOS_FOLDER'] = 'profile_photos'
app.config['SECRET_KEY'] = 'b7b6e0135582657a393275bc2d77dee6cb56462af64082da0eb68b09acd275dc' # Add a secret key for token generation
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

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

class PublicShare(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=False)
    share_token = db.Column(db.String(64), unique=True, nullable=False)
    recipient_email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text)
    expiration_time = db.Column(db.Integer, nullable=False)  # in hours
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    file = db.relationship('File', backref='public_shares')

    def __init__(self, **kwargs):
        super(PublicShare, self).__init__(**kwargs)
        # No need for manual localization here if column is timezone=True

class FileAccess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=False)
    share_token = db.Column(db.String(64), nullable=False)
    access_time = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))

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
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password are required'}), 400
            
        print("Login attempt for email:", data.get('email'))
        print("Received password:", data.get('password'))
        
        user = User.query.filter_by(email=data['email']).first()
        if not user:
            print("User not found")
            return jsonify({'error': 'No account found with this email'}), 401
        
        print("User found with ID:", user.id)
        print("Stored password hash:", user.password_hash)
        print("Checking password...")
        
        is_password_correct = check_password_hash(user.password_hash, data['password'])
        print("Password check result:", is_password_correct)
        
        if is_password_correct:
            print("Password correct, generating token")
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
        
        print("Password incorrect")
        return jsonify({'error': 'Incorrect password'}), 401
        
    except Exception as e:
        print("Login error:", str(e))
        return jsonify({'error': 'An error occurred during login'}), 500

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

@app.route('/api/files/<int:file_id>', methods=['GET'])
@jwt_required()
def get_file_details(file_id):
    user_id = get_jwt_identity()
    file = File.query.filter_by(id=file_id, user_id=user_id).first()
    
    if not file:
        return jsonify({'error': 'File not found'}), 404
    
    return jsonify({
        'id': file.id,
        'filename': file.original_filename,
        'size': file.file_size,
        'upload_date': file.upload_date.isoformat()
    }), 200

@app.route('/api/share', methods=['POST'])
@jwt_required()
def share_file():
    data = request.get_json()
    user_id = get_jwt_identity()
    
    file = File.query.filter_by(id=data['file_id'], user_id=user_id).first()
    if not file:
        return jsonify({'error': 'File not found'}), 404

    # Check if file already has a public share
    existing_share = PublicShare.query.filter_by(file_id=file.id).first()
    
    # Get expiration_hours from the current request
    expiration_hours = int(data.get('expiration_time', 24))
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist)

    # Calculate new expires_at based on current request's expiration_hours
    if expiration_hours == 1:
        expires_at_new = current_time + timedelta(hours=1)
    else:
        days = 0
        if expiration_hours == 24:
            days = 1
        elif expiration_hours == 72:
            days = 3
        elif expiration_hours == 168:
            days = 7
        elif expiration_hours == 720:
            days = 30
        else:
            # Fallback for unexpected values, treat as days
            days = expiration_hours // 24

        # Set expiration to end of the day (23:59:59) of the target day
        expires_at_new = (current_time + timedelta(days=days)).replace(hour=23, minute=59, second=59)

    # expires_at_new is already timezone-aware because current_time is.
    # SQLAlchemy will handle UTC conversion when saving to DateTime(timezone=True)

    if existing_share:
        # If share exists, update its expiration and reuse the link
        existing_share.expiration_time = expiration_hours
        existing_share.expires_at = expires_at_new  # Save timezone-aware datetime
        db.session.commit()

        share_link = f"http://localhost:3000/shared/{existing_share.share_token}"
        expires_at_for_email = existing_share.expires_at.astimezone(ist) # Convert back to IST for email
    else:
        # If no existing share, create a new one
        share_token = secrets.token_urlsafe(32)
        public_share = PublicShare(
            file_id=file.id,
            share_token=share_token,
            recipient_email=data['email'],
            message=data.get('message', ''),
            expiration_time=expiration_hours,
            expires_at=expires_at_new  # Save timezone-aware datetime
        )
        db.session.add(public_share)
        db.session.commit()

        share_link = f"http://localhost:3000/shared/{share_token}"
        expires_at_for_email = expires_at_new.astimezone(ist) # Convert to IST for email
    
    # Send email with new share link (or updated expiration)
    try:
        msg = Message(
            'File Shared With You',
            recipients=[data['email']]
        )
        msg.body = f"""
        A file has been shared with you.

        File: {file.original_filename}
        Message: {data.get('message', '')}
        
        You can access the file using this link: {share_link}
        
        This link will expire on {expires_at_for_email.strftime('%Y-%m-%d %H:%M:%S %Z')}
        """
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email: {e}")
        # Don't return error to user, just log it
    
    return jsonify({
        'message': 'File shared successfully',
        'share_link': share_link,
        'expires_at': expires_at_for_email.strftime('%Y-%m-%d %H:%M:%S %Z')
    }), 200

@app.route('/api/shared/<token>', methods=['GET', 'OPTIONS'])
def get_shared_file(token):
    try:
        if request.method == 'OPTIONS':
            return '', 200
            
        share = PublicShare.query.filter_by(share_token=token).first()
        if not share:
            return jsonify({'error': 'Share link not found'}), 404
        
        # Current time in IST for comparison
        ist = pytz.timezone('Asia/Kolkata')
        current_time_ist = datetime.now(ist)

        # share.expires_at is already timezone-aware (UTC) from DB, convert to IST for comparison
        share_expires_at_ist = share.expires_at.astimezone(ist)
        
        if share_expires_at_ist < current_time_ist:
            return jsonify({'error': 'Share link has expired'}), 410
        
        file = File.query.get(share.file_id)
        if not file:
            return jsonify({'error': 'File not found'}), 404
        
        # Record file access
        try:
            file_access = FileAccess(
                file_id=file.id,
                share_token=token
            )
            db.session.add(file_access)
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Rollback on error
            # Log but don't fail the request
        
        # Check if the request wants JSON details or the actual file
        if request.headers.get('Accept') == 'application/json':
            return jsonify({
                'filename': file.original_filename,
                'size': file.file_size,
                'message': share.message,
                'expires_at': share_expires_at_ist.strftime('%Y-%m-%d %H:%M:%S %Z') # Use IST for display
            }), 200
        
        # If not requesting JSON, serve the file for download
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found on server'}), 404

        return send_from_directory(
            app.config['UPLOAD_FOLDER'],
            file.filename,
            as_attachment=True,
            download_name=file.original_filename
        )
    except Exception as e:
        print(f"Error in get_shared_file: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/shared-files', methods=['GET'])
@jwt_required()
def get_shared_files():
    user_id = get_jwt_identity()
    ist = pytz.timezone('Asia/Kolkata')
    
    shared_files = db.session.query(
        File, PublicShare
    ).join(
        PublicShare, File.id == PublicShare.file_id
    ).filter(
        File.user_id == user_id
    ).order_by(
        PublicShare.created_at.desc()  # Sort by creation date in descending order
    ).all()
    
    result = []
    for file, share in shared_files:
        # Convert stored UTC-aware datetimes to IST for display
        share_created_at_ist = share.created_at.astimezone(ist) if share.created_at.tzinfo else ist.localize(share.created_at)
        share_expires_at_ist = share.expires_at.astimezone(ist) if share.expires_at.tzinfo else ist.localize(share.expires_at)

        first_access = db.session.query(FileAccess).filter_by(
            file_id=file.id,
            share_token=share.share_token
        ).order_by(FileAccess.access_time.asc()).first()
        
        first_access_time_ist = None
        if first_access and first_access.access_time:
            first_access_time_ist = first_access.access_time.astimezone(ist) if first_access.access_time.tzinfo else ist.localize(first_access.access_time)

        result.append({
            'file_id': file.id,
            'filename': file.original_filename,
            'share_date': share_created_at_ist.strftime('%Y-%m-%d %H:%M:%S %Z'),
            'expires_at': share_expires_at_ist.strftime('%Y-%m-%d %H:%M:%S %Z'),
            'share_token': share.share_token,
            'recipient_email': share.recipient_email,
            'message': share.message,
            'is_accessed': first_access is not None,
            'first_access_time': first_access_time_ist.strftime('%Y-%m-%d %H:%M:%S %Z') if first_access_time_ist else None
        })
    
    return jsonify(result), 200

@app.route('/api/shared-files/<token>', methods=['DELETE'])
@jwt_required()
def delete_shared_file(token):
    user_id = get_jwt_identity()

    try:
        # Find the public share entry
        share = PublicShare.query.filter_by(share_token=token).first()

        if not share:
            return jsonify({'error': 'Shared link not found'}), 404

        # Verify that the user owns the file associated with the share link
        file = File.query.get(share.file_id)
        if not file or file.user_id != user_id:
            return jsonify({'error': 'Unauthorized to delete this shared link'}), 403

        # Delete associated file access records first
        FileAccess.query.filter_by(share_token=token).delete()

        # Delete the public share entry
        db.session.delete(share)
        db.session.commit()

        return jsonify({'message': 'Shared link deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error deleting shared file: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/api/test-user', methods=['POST'])
def create_test_user():
    try:
        # Check if test user already exists
        test_email = 'test@example.com'
        if User.query.filter_by(email=test_email).first():
            return jsonify({'message': 'Test user already exists'}), 200

        # Create test user
        user = User(
            first_name='Test',
            last_name='User',
            email=test_email,
            password_hash=generate_password_hash('test123'),
            date_of_birth=datetime.now().date(),
            phone_number='1234567890'
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'Test user created successfully'}), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/check-user/<email>', methods=['GET'])
def check_user(email):
    try:
        user = User.query.filter_by(email=email).first()
        if user:
            return jsonify({
                'exists': True,
                'id': user.id,
                'email': user.email,
                'password_hash': user.password_hash,
                'first_name': user.first_name,
                'last_name': user.last_name
            }), 200
        return jsonify({'exists': False}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/change-password', methods=['POST'])
@jwt_required()
def change_password():
    try:
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current password and new password are required'}), 400
            
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        if not check_password_hash(user.password_hash, current_password):
            return jsonify({'error': 'Current password is incorrect'}), 401
            
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        print("Change password error:", str(e))
        return jsonify({'error': 'An error occurred while changing password'}), 500

@app.route('/api/verify-password', methods=['POST'])
@jwt_required()
def verify_password():
    try:
        data = request.get_json()
        current_password = data.get('current_password')
        
        if not current_password:
            return jsonify({'error': 'Current password is required'}), 400
            
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        if not check_password_hash(user.password_hash, current_password):
            return jsonify({'error': 'Current password is incorrect'}), 401
            
        return jsonify({'message': 'Password verified successfully'}), 200
        
    except Exception as e:
        print("Verify password error:", str(e))
        return jsonify({'error': 'An error occurred while verifying password'}), 500

@app.route('/api/user', methods=['GET'])
@jwt_required()
def get_user_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify({
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'date_of_birth': user.date_of_birth.isoformat(),
            'phone_number': user.phone_number,
            'profile_photo': user.profile_photo
        }), 200
        
    except Exception as e:
        print("Get user profile error:", str(e))
        return jsonify({'error': 'An error occurred while fetching user profile'}), 500

@app.route('/api/user', methods=['PUT'])
@jwt_required()
def update_user_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Update basic info
        user.first_name = request.form.get('first_name', user.first_name)
        user.last_name = request.form.get('last_name', user.last_name)
        user.email = request.form.get('email', user.email)
        user.phone_number = request.form.get('phone_number', user.phone_number)
        
        # Update date of birth if provided
        if 'date_of_birth' in request.form:
            user.date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()

        # Handle profile photo upload
        if 'profile_photo' in request.files:
            photo = request.files['profile_photo']
            if photo.filename != '':
                # Delete old profile photo if exists
                if user.profile_photo:
                    old_photo_path = os.path.join(app.config['PROFILE_PHOTOS_FOLDER'], user.profile_photo)
                    if os.path.exists(old_photo_path):
                        os.remove(old_photo_path)

                # Save new profile photo
                filename = secure_filename(photo.filename)
                photo_path = os.path.join(app.config['PROFILE_PHOTOS_FOLDER'], filename)
                photo.save(photo_path)
                user.profile_photo = filename

        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'date_of_birth': user.date_of_birth.isoformat(),
                'phone_number': user.phone_number,
                'profile_photo': user.profile_photo
            }
        }), 200
        
    except Exception as e:
        print("Update profile error:", str(e))
        return jsonify({'error': 'An error occurred while updating profile'}), 500

@app.route('/profile_photos/<filename>')
def serve_profile_photo(filename):
    return send_from_directory(app.config['PROFILE_PHOTOS_FOLDER'], filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 