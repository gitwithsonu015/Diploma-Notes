from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'diploma-notes-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/notes'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Create upload folder if not exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Password reset tokens storage (token -> user_id)
reset_tokens = {}

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='student')  # student or owner
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    branch = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # notes, syllabus, pyq
    description = db.Column(db.Text)
    file_path = db.Column(db.String(200))
    price = db.Column(db.Integer, default=19)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'), nullable=False)
    payment_proof = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='purchases')
    note = db.relationship('Note', backref='purchases')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    branches = ['Computer Science', 'Civil', 'Mechanical', 'Electrical', 'Electronics']
    categories = ['Notes', 'Syllabus', 'PYQ']
    notes = Note.query.all() if current_user.is_authenticated else []
    return render_template('index.html', branches=branches, categories=categories, notes=notes)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(name=name, email=email, phone=phone, password=hashed_password, role='student')
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == 'owner':
                return redirect(url_for('owner_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        user = User.query.filter_by(email=email, phone=phone).first()
        
        if user:
            # Generate reset token
            token = str(uuid.uuid4())
            reset_tokens[token] = user.id
            
            flash(f'Password reset link: /reset-password/{token}. Share this link with the user (in production, this would be sent via email).', 'success')
            return redirect(url_for('login'))
        else:
            flash('No account found with that email and phone number!', 'error')
    
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user_id = reset_tokens.get(token)
    
    if not user_id:
        flash('Invalid or expired reset token!', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('reset_password.html', token=token)
        
        if len(password) < 6:
            flash('Password must be at least 6 characters!', 'error')
            return render_template('reset_password.html', token=token)
        
        user = User.query.get(user_id)
        if user:
            user.password = generate_password_hash(password, method='pbkdf2:sha256')
            db.session.commit()
            
            # Remove used token
            del reset_tokens[token]
            
            flash('Password updated successfully! Please login with your new password.', 'success')
            return redirect(url_for('login'))
        else:
            flash('User not found!', 'error')
            return redirect(url_for('forgot_password'))
    
    return render_template('reset_password.html', token=token)

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'owner':
        return redirect(url_for('owner_dashboard'))
    
    purchased_notes = Purchase.query.filter_by(user_id=current_user.id, status='approved').all()
    pending_purchases = Purchase.query.filter_by(user_id=current_user.id, status='pending').all()
    return render_template('dashboard.html', purchased=purchased_notes, pending=pending_purchases)

@app.route('/notes')
@login_required
def notes():
    branch = request.args.get('branch')
    category = request.args.get('category')
    
    query = Note.query
    if branch:
        query = query.filter_by(branch=branch)
    if category:
        query = query.filter_by(category=category)
    
    all_notes = query.all()
    branches = ['Computer Science', 'Civil', 'Mechanical', 'Electrical', 'Electronics']
    categories = ['Notes', 'Syllabus', 'PYQ']
    
    return render_template('notes.html', notes=all_notes, branches=branches, categories=categories, selected_branch=branch, selected_category=category)

@app.route('/note/<int:note_id>')
@login_required
def note_detail(note_id):
    note = Note.query.get_or_404(note_id)
    purchased = Purchase.query.filter_by(user_id=current_user.id, note_id=note_id, status='approved').first()
    pending = Purchase.query.filter_by(user_id=current_user.id, note_id=note_id, status='pending').first()
    return render_template('note_detail.html', note=note, purchased=purchased, pending=pending)

@app.route('/purchase/<int:note_id>', methods=['GET', 'POST'])
@login_required
def purchase(note_id):
    note = Note.query.get_or_404(note_id)
    
    existing_purchase = Purchase.query.filter_by(user_id=current_user.id, note_id=note_id).first()
    if existing_purchase:
        if existing_purchase.status == 'approved':
            flash('You have already purchased this note!', 'info')
            return redirect(url_for('dashboard'))
        elif existing_purchase.status == 'pending':
            flash('Your payment is pending verification!', 'info')
            return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        if 'payment_proof' not in request.files:
            flash('Please upload payment proof!', 'error')
            return redirect(url_for('purchase', note_id=note_id))
        
        file = request.files['payment_proof']
        if file.filename == '':
            flash('Please select a file!', 'error')
            return redirect(url_for('purchase', note_id=note_id))
        
        if file:
            filename = f"{current_user.id}_{note_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
            file.save(os.path.join('static/uploads', filename))
            os.makedirs('static/uploads', exist_ok=True)
            
            purchase = Purchase(user_id=current_user.id, note_id=note_id, payment_proof=filename, status='pending')
            db.session.add(purchase)
            db.session.commit()
            
            flash('Payment proof uploaded! Wait for verification.', 'success')
            return redirect(url_for('dashboard'))
    
    return render_template('payment.html', note=note)

@app.route('/download/<int:note_id>')
@login_required
def download(note_id):
    note = Note.query.get_or_404(note_id)
    purchase = Purchase.query.filter_by(user_id=current_user.id, note_id=note_id, status='approved').first()
    
    if not purchase:
        flash('Please purchase this note first!', 'error')
        return redirect(url_for('note_detail', note_id=note_id))
    
    if note.file_path:
        return send_from_directory(app.config['UPLOAD_FOLDER'], note.file_path, as_attachment=True)
    else:
        flash('File not available!', 'error')
        return redirect(url_for('dashboard'))

# Owner Routes
@app.route('/owner')
@login_required
def owner_dashboard():
    if current_user.role != 'owner':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    
    total_sales = Purchase.query.filter_by(status='approved').count()
    pending_payments = Purchase.query.filter_by(status='pending').all()
    all_notes = Note.query.all()
    total_users = User.query.filter_by(role='student').count()
    
    return render_template('owner/dashboard.html', sales=total_sales, pending=pending_payments, notes=all_notes, users=total_users)

@app.route('/owner/add-note', methods=['GET', 'POST'])
@login_required
def add_note():
    if current_user.role != 'owner':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        branch = request.form.get('branch')
        category = request.form.get('category')
        description = request.form.get('description')
        
        file_path = None
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                filename = f"{branch}_{category}_{file.filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                file_path = filename
        
        note = Note(title=title, branch=branch, category=category, description=description, file_path=file_path, price=19)
        db.session.add(note)
        db.session.commit()
        
        flash('Note added successfully!', 'success')
        return redirect(url_for('owner_dashboard'))
    
    branches = ['Computer Science', 'Civil', 'Mechanical', 'Electrical', 'Electronics']
    categories = ['Notes', 'Syllabus', 'PYQ']
    return render_template('owner/add_note.html', branches=branches, categories=categories)

@app.route('/owner/verify-payments')
@login_required
def verify_payments():
    if current_user.role != 'owner':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    
    pending = Purchase.query.filter_by(status='pending').all()
    return render_template('owner/verify.html', purchases=pending)

@app.route('/owner/approve/<int:purchase_id>')
@login_required
def approve_payment(purchase_id):
    if current_user.role != 'owner':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    
    purchase = Purchase.query.get_or_404(purchase_id)
    purchase.status = 'approved'
    db.session.commit()
    
    flash('Payment approved!', 'success')
    return redirect(url_for('verify_payments'))

@app.route('/owner/reject/<int:purchase_id>')
@login_required
def reject_payment(purchase_id):
    if current_user.role != 'owner':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    
    purchase = Purchase.query.get_or_404(purchase_id)
    purchase.status = 'rejected'
    db.session.commit()
    
    flash('Payment rejected!', 'success')
    return redirect(url_for('verify_payments'))

@app.route('/owner/delete-note/<int:note_id>')
@login_required
def delete_note(note_id):
    if current_user.role != 'owner':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    
    note = Note.query.get_or_404(note_id)
    if note.file_path:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], note.file_path))
        except:
            pass
    
    Purchase.query.filter_by(note_id=note_id).delete()
    db.session.delete(note)
    db.session.commit()
    
    flash('Note deleted!', 'success')
    return redirect(url_for('owner_dashboard'))

@app.route('/owner/view-payment-proof/<filename>')
@login_required
def view_payment_proof(filename):
    if current_user.role != 'owner':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    
    return send_from_directory('static/uploads', filename)

# Create database
with app.app_context():
    db.create_all()
    
    # Create owner account if not exists
    owner = User.query.filter_by(role='owner').first()
    if not owner:
        owner = User(
            name='Owner',
            email='owner@diplomanotes.com',
            phone='8294255694',
            password=generate_password_hash('owner123', method='pbkdf2:sha256'),
            role='owner'
        )
        db.session.add(owner)
        db.session.commit()
        print("Owner account created! Email: owner@diplomanotes.com, Password: owner123")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
