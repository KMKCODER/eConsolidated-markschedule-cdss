from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from app import app, get_db_connection

@app.route('/')
def index():
    """Home page - redirect to login or dashboard"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash('Please fill in all fields.', 'error')
            return render_template('auth/login.html')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash(f'Welcome, {user["username"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    """User logout"""
    username = session.get('username', 'User')
    session.clear()
    flash(f'Goodbye, {username}!', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register new teacher (only admin can access this)"""
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('login'))
    
    # Check if current user is admin
    conn = get_db_connection()
    current_user = conn.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if not current_user or current_user['role'] != 'admin':
        conn.close()
        flash('You need admin privileges to register new users.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']
        
        # Validation
        if not all([username, password, confirm_password, role]):
            flash('Please fill in all fields.', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('auth/register.html')
        
        if role not in ['admin', 'teacher']:
            flash('Invalid role selected.', 'error')
            return render_template('auth/register.html')
        
        # Check if username already exists
        existing_user = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
            conn.close()
            return render_template('auth/register.html')
        
        # Create new user
        password_hash = generate_password_hash(password)
        try:
            conn.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                        (username, password_hash, role))
            conn.commit()
            flash(f'User "{username}" has been successfully registered as {role}.', 'success')
            conn.close()
            return redirect(url_for('manage_users'))
        except Exception as e:
            flash('An error occurred while creating the user.', 'error')
            print(f"Registration error: {e}")
    
    conn.close()
    return render_template('auth/register.html')