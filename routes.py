from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app import app, get_db_connection, login_required, admin_required
from datetime import datetime
import csv
import io

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    conn = get_db_connection()
    
    # Get statistics
    total_classes = conn.execute('SELECT COUNT(*) as count FROM classes').fetchone()['count']
    total_learners = conn.execute('SELECT COUNT(*) as count FROM learners').fetchone()['count']
    total_marks = conn.execute('SELECT COUNT(*) as count FROM marks').fetchone()['count']
    
    # Get recent classes
    recent_classes = conn.execute('''
        SELECT c.*, COUNT(l.id) as learner_count 
        FROM classes c 
        LEFT JOIN learners l ON c.id = l.class_id 
        GROUP BY c.id 
        ORDER BY c.created_at DESC 
        LIMIT 5
    ''').fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', 
                         total_classes=total_classes,
                         total_learners=total_learners,
                         total_marks=total_marks,
                         recent_classes=recent_classes)

@app.route('/classes')
@login_required
def list_classes():
    """List all classes"""
    conn = get_db_connection()
    classes = conn.execute('''
        SELECT c.*, COUNT(l.id) as learner_count,
               COUNT(m.id) as marks_count
        FROM classes c 
        LEFT JOIN learners l ON c.id = l.class_id 
        LEFT JOIN marks m ON l.id = m.learner_id
        GROUP BY c.id 
        ORDER BY c.name
    ''').fetchall()
    conn.close()
    
    return render_template('classes/list.html', classes=classes)

@app.route('/classes/add', methods=['GET', 'POST'])
@admin_required
def add_class():
    """Add a new class (admin only)"""
    if request.method == 'POST':
        name = request.form['name'].strip()
        description = request.form['description'].strip()
        
        if not name:
            flash('Class name is required.', 'error')
            return render_template('classes/add.html')
        
        conn = get_db_connection()
        
        # Check if class already exists
        existing = conn.execute('SELECT id FROM classes WHERE name = ?', (name,)).fetchone()
        if existing:
            flash('A class with this name already exists.', 'error')
            conn.close()
            return render_template('classes/add.html')
        
        # Add new class
        try:
            conn.execute('INSERT INTO classes (name, description) VALUES (?, ?)',
                        (name, description))
            conn.commit()
            flash(f'Class "{name}" has been added successfully.', 'success')
            conn.close()
            return redirect(url_for('list_classes'))
        except Exception as e:
            flash('An error occurred while adding the class.', 'error')
            print(f"Add class error: {e}")
            conn.close()
    
    return render_template('classes/add.html')

@app.route('/classes/<int:class_id>')
@login_required
def view_class(class_id):
    """View class details and learners"""
    conn = get_db_connection()
    
    # Get class details
    class_info = conn.execute('SELECT * FROM classes WHERE id = ?', (class_id,)).fetchone()
    if not class_info:
        flash('Class not found.', 'error')
        conn.close()
        return redirect(url_for('list_classes'))
    
    # Get learners in this class with their marks
    learners = conn.execute('''
        SELECT l.*, m.test1_mark, m.test2_mark, m.final_mark, m.created_at as marks_date
        FROM learners l 
        LEFT JOIN marks m ON l.id = m.learner_id 
        WHERE l.class_id = ? 
        ORDER BY l.name
    ''', (class_id,)).fetchall()
    
    conn.close()
    
    return render_template('classes/view.html', class_info=class_info, learners=learners)

@app.route('/learners/add/<int:class_id>', methods=['GET', 'POST'])
@admin_required
def add_learner(class_id):
    """Add a new learner to a class (admin only)"""
    conn = get_db_connection()
    
    # Check if class exists
    class_info = conn.execute('SELECT * FROM classes WHERE id = ?', (class_id,)).fetchone()
    if not class_info:
        flash('Class not found.', 'error')
        conn.close()
        return redirect(url_for('list_classes'))
    
    if request.method == 'POST':
        name = request.form['name'].strip()
        gender = request.form['gender']
        
        if not name:
            flash('Learner name is required.', 'error')
            return render_template('learners/add.html', class_info=class_info)
        
        if gender not in ['male', 'female']:
            flash('Please select a valid gender.', 'error')
            return render_template('learners/add.html', class_info=class_info)
        
        # Add new learner
        try:
            conn.execute('INSERT INTO learners (name, gender, class_id) VALUES (?, ?, ?)',
                        (name, gender, class_id))
            conn.commit()
            flash(f'Learner "{name}" has been added to {class_info["name"]}.', 'success')
            conn.close()
            return redirect(url_for('view_class', class_id=class_id))
        except Exception as e:
            flash('An error occurred while adding the learner.', 'error')
            print(f"Add learner error: {e}")
            conn.close()
    
    conn.close()
    return render_template('learners/add.html', class_info=class_info)

@app.route('/marks/upload/<int:class_id>', methods=['GET', 'POST'])
@login_required
def upload_marks(class_id):
    """Upload marks for learners in a class"""
    conn = get_db_connection()
    
    # Check if class exists
    class_info = conn.execute('SELECT * FROM classes WHERE id = ?', (class_id,)).fetchone()
    if not class_info:
        flash('Class not found.', 'error')
        conn.close()
        return redirect(url_for('list_classes'))
    
    # Get learners in this class
    learners = conn.execute('''
        SELECT l.*, m.test1_mark, m.test2_mark, m.final_mark 
        FROM learners l 
        LEFT JOIN marks m ON l.id = m.learner_id 
        WHERE l.class_id = ? 
        ORDER BY l.name
    ''', (class_id,)).fetchall()
    
    if request.method == 'POST':
        updates_made = 0
        errors = []
        
        for learner in learners:
            learner_id = learner['id']
            test1_mark = request.form.get(f'test1_{learner_id}')
            test2_mark = request.form.get(f'test2_{learner_id}')
            
            # Skip if both marks are empty
            if not test1_mark and not test2_mark:
                continue
            
            # Validate marks
            try:
                if test1_mark:
                    test1_mark = int(test1_mark)
                    if test1_mark < 0 or test1_mark > 40:
                        errors.append(f"{learner['name']}: Test 1 mark must be between 0 and 40")
                        continue
                else:
                    test1_mark = None
                
                if test2_mark:
                    test2_mark = int(test2_mark)
                    if test2_mark < 0 or test2_mark > 60:
                        errors.append(f"{learner['name']}: Test 2 mark must be between 0 and 60")
                        continue
                else:
                    test2_mark = None
                
                # Allow partial updates (just Test 1 or just Test 2)
                if test1_mark is None and test2_mark is None:
                    continue
                
                # Check if marks already exist
                existing_marks = conn.execute('SELECT id, test1_mark, test2_mark FROM marks WHERE learner_id = ?', (learner_id,)).fetchone()
                
                if existing_marks:
                    # Update existing marks (keep existing values for marks not provided)
                    current_test1 = test1_mark if test1_mark is not None else existing_marks['test1_mark']
                    current_test2 = test2_mark if test2_mark is not None else existing_marks['test2_mark']
                    
                    # Only update if we have at least one mark
                    if current_test1 is not None or current_test2 is not None:
                        conn.execute('''
                            UPDATE marks 
                            SET test1_mark = ?, test2_mark = ?, updated_at = CURRENT_TIMESTAMP 
                            WHERE learner_id = ?
                        ''', (current_test1, current_test2, learner_id))
                        updates_made += 1
                else:
                    # Insert new marks (allow partial entry)
                    if test1_mark is not None or test2_mark is not None:
                        conn.execute('''
                            INSERT INTO marks (learner_id, test1_mark, test2_mark) 
                            VALUES (?, ?, ?)
                        ''', (learner_id, test1_mark, test2_mark))
                        updates_made += 1
                
            except ValueError:
                errors.append(f"{learner['name']}: Invalid mark values")
                continue
        
        if errors:
            for error in errors:
                flash(error, 'error')
        
        if updates_made > 0:
            conn.commit()
            flash(f'Successfully updated marks for {updates_made} learner(s).', 'success')
            conn.close()
            return redirect(url_for('view_class', class_id=class_id))
        else:
            flash('No valid marks were submitted for update.', 'warning')
    
    conn.close()
    return render_template('marks/upload.html', class_info=class_info, learners=learners)

@app.route('/users')
@admin_required
def manage_users():
    """Manage users (admin only)"""
    conn = get_db_connection()
    users = conn.execute('''
        SELECT id, username, role, created_at 
        FROM users 
        ORDER BY role, username
    ''').fetchall()
    conn.close()
    
    return render_template('users/list.html', users=users)

@app.route('/reports')
@login_required
def reports():
    """View reports and statistics"""
    conn = get_db_connection()
    
    # Class performance summary
    class_stats = conn.execute('''
        SELECT c.name as class_name,
               COUNT(l.id) as total_learners,
               COUNT(m.id) as marked_learners,
               ROUND(AVG(m.final_mark), 2) as average_mark,
               MAX(m.final_mark) as highest_mark,
               MIN(m.final_mark) as lowest_mark
        FROM classes c
        LEFT JOIN learners l ON c.id = l.class_id
        LEFT JOIN marks m ON l.id = m.learner_id
        GROUP BY c.id, c.name
        ORDER BY c.name
    ''').fetchall()
    
    # Gender distribution
    gender_stats = conn.execute('''
        SELECT l.gender,
               COUNT(l.id) as count,
               ROUND(AVG(m.final_mark), 2) as average_mark
        FROM learners l
        LEFT JOIN marks m ON l.id = m.learner_id
        GROUP BY l.gender
    ''').fetchall()
    
    conn.close()
    
    return render_template('reports.html', class_stats=class_stats, gender_stats=gender_stats)

@app.route('/upload/learners', methods=['GET', 'POST'])
@admin_required
def upload_learners_csv():
    """Upload learners from CSV file (admin only)"""
    conn = get_db_connection()
    classes = conn.execute('SELECT * FROM classes ORDER BY name').fetchall()
    
    if request.method == 'POST':
        if 'csv_file' not in request.files:
            flash('No file selected.', 'error')
            return render_template('upload/learners.html', classes=classes)
        
        csv_file = request.files['csv_file']
        if csv_file.filename == '':
            flash('No file selected.', 'error')
            return render_template('upload/learners.html', classes=classes)
        
        if not csv_file.filename.lower().endswith('.csv'):
            flash('Please upload a CSV file.', 'error')
            return render_template('upload/learners.html', classes=classes)
        
        try:
            # Read CSV content
            csv_content = csv_file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            
            # Validate CSV headers
            required_headers = ['name', 'gender', 'class_name']
            if not all(header in csv_reader.fieldnames for header in required_headers):
                flash(f'CSV must have columns: {', '.join(required_headers)}', 'error')
                return render_template('upload/learners.html', classes=classes)
            
            # Process CSV data
            added_count = 0
            errors = []
            
            for row_num, row in enumerate(csv_reader, start=2):
                name = row.get('name', '').strip()
                gender = row.get('gender', '').strip().lower()
                class_name = row.get('class_name', '').strip()
                
                # Validation
                if not name:
                    errors.append(f'Row {row_num}: Name is required')
                    continue
                
                if gender not in ['male', 'female']:
                    errors.append(f'Row {row_num}: Gender must be "male" or "female"')
                    continue
                
                if not class_name:
                    errors.append(f'Row {row_num}: Class name is required')
                    continue
                
                # Find class
                class_info = conn.execute('SELECT id FROM classes WHERE name = ?', (class_name,)).fetchone()
                if not class_info:
                    errors.append(f'Row {row_num}: Class "{class_name}" not found')
                    continue
                
                # Check if learner already exists
                existing = conn.execute('SELECT id FROM learners WHERE name = ? AND class_id = ?', (name, class_info['id'])).fetchone()
                if existing:
                    errors.append(f'Row {row_num}: Learner "{name}" already exists in class "{class_name}"')
                    continue
                
                # Add learner
                try:
                    conn.execute('INSERT INTO learners (name, gender, class_id) VALUES (?, ?, ?)',
                                (name, gender, class_info['id']))
                    added_count += 1
                except Exception as e:
                    errors.append(f'Row {row_num}: Error adding "{name}" - {str(e)}')
                    continue
            
            if added_count > 0:
                conn.commit()
                flash(f'Successfully added {added_count} learner(s).', 'success')
            
            if errors:
                for error in errors[:10]:  # Show only first 10 errors
                    flash(error, 'error')
                if len(errors) > 10:
                    flash(f'... and {len(errors) - 10} more errors', 'error')
            
            conn.close()
            return redirect(url_for('upload_learners_csv'))
            
        except Exception as e:
            flash(f'Error processing CSV: {str(e)}', 'error')
            conn.close()
    
    conn.close()
    return render_template('upload/learners.html', classes=classes)

@app.route('/upload/marks', methods=['GET', 'POST'])
@login_required
def upload_marks_csv():
    """Upload marks from CSV file"""
    conn = get_db_connection()
    classes = conn.execute('SELECT * FROM classes ORDER BY name').fetchall()
    
    if request.method == 'POST':
        if 'csv_file' not in request.files:
            flash('No file selected.', 'error')
            return render_template('upload/marks.html', classes=classes)
        
        csv_file = request.files['csv_file']
        if csv_file.filename == '':
            flash('No file selected.', 'error')
            return render_template('upload/marks.html', classes=classes)
        
        if not csv_file.filename.lower().endswith('.csv'):
            flash('Please upload a CSV file.', 'error')
            return render_template('upload/marks.html', classes=classes)
        
        try:
            # Read CSV content
            csv_content = csv_file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            
            # Validate CSV headers
            required_headers = ['learner_name', 'test1_mark', 'test2_mark', 'class_name']
            if not all(header in csv_reader.fieldnames for header in required_headers):
                flash(f'CSV must have columns: {', '.join(required_headers)}', 'error')
                return render_template('upload/marks.html', classes=classes)
            
            # Process CSV data
            updated_count = 0
            errors = []
            
            for row_num, row in enumerate(csv_reader, start=2):
                learner_name = row.get('learner_name', '').strip()
                test1_mark = row.get('test1_mark', '').strip()
                test2_mark = row.get('test2_mark', '').strip()
                class_name = row.get('class_name', '').strip()
                
                # Validation
                if not learner_name:
                    errors.append(f'Row {row_num}: Learner name is required')
                    continue
                
                if not class_name:
                    errors.append(f'Row {row_num}: Class name is required')
                    continue
                
                # Validate marks (allow partial uploads)
                try:
                    if test1_mark:
                        test1_mark = int(test1_mark)
                        if test1_mark < 0 or test1_mark > 40:
                            errors.append(f'Row {row_num}: Test 1 mark must be between 0 and 40')
                            continue
                    else:
                        test1_mark = None
                    
                    if test2_mark:
                        test2_mark = int(test2_mark)
                        if test2_mark < 0 or test2_mark > 60:
                            errors.append(f'Row {row_num}: Test 2 mark must be between 0 and 60')
                            continue
                    else:
                        test2_mark = None
                        
                    if test1_mark is None and test2_mark is None:
                        errors.append(f'Row {row_num}: At least one test mark is required')
                        continue
                        
                except ValueError:
                    errors.append(f'Row {row_num}: Invalid mark values')
                    continue
                
                # Find learner
                learner = conn.execute('''
                    SELECT l.id FROM learners l
                    JOIN classes c ON l.class_id = c.id
                    WHERE l.name = ? AND c.name = ?
                ''', (learner_name, class_name)).fetchone()
                
                if not learner:
                    errors.append(f'Row {row_num}: Learner "{learner_name}" not found in class "{class_name}"')
                    continue
                
                # Update or insert marks (allow partial updates)
                try:
                    existing_marks = conn.execute('SELECT id, test1_mark, test2_mark FROM marks WHERE learner_id = ?', (learner['id'],)).fetchone()
                    
                    if existing_marks:
                        # Update existing marks (keep existing values for marks not provided)
                        current_test1 = test1_mark if test1_mark is not None else existing_marks['test1_mark']
                        current_test2 = test2_mark if test2_mark is not None else existing_marks['test2_mark']
                        
                        conn.execute('''
                            UPDATE marks 
                            SET test1_mark = ?, test2_mark = ?, updated_at = CURRENT_TIMESTAMP 
                            WHERE learner_id = ?
                        ''', (current_test1, current_test2, learner['id']))
                    else:
                        # Insert new marks (allow partial entry)
                        conn.execute('''
                            INSERT INTO marks (learner_id, test1_mark, test2_mark) 
                            VALUES (?, ?, ?)
                        ''', (learner['id'], test1_mark, test2_mark))
                    
                    updated_count += 1
                    
                except Exception as e:
                    errors.append(f'Row {row_num}: Error updating marks for "{learner_name}" - {str(e)}')
                    continue
            
            if updated_count > 0:
                conn.commit()
                flash(f'Successfully updated marks for {updated_count} learner(s).', 'success')
            
            if errors:
                for error in errors[:10]:  # Show only first 10 errors
                    flash(error, 'error')
                if len(errors) > 10:
                    flash(f'... and {len(errors) - 10} more errors', 'error')
            
            conn.close()
            return redirect(url_for('upload_marks_csv'))
            
        except Exception as e:
            flash(f'Error processing CSV: {str(e)}', 'error')
            conn.close()
    
    conn.close()
    return render_template('upload/marks.html', classes=classes)