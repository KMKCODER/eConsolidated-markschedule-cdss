# eConsolidated Mark Schedule System

A comprehensive web application for managing learner results and academic performance tracking. Built with Flask and designed for educational institutions.

## 📋 Features

### 🔐 User Management
- **Role-based authentication** (Admin & Teacher)
- **Admin capabilities**: Create classes, add learners, manage users
- **Teacher capabilities**: Upload marks, view reports, access all classes

### 📚 Class Management
- Create and organize classes
- Add learners with gender tracking
- View class performance statistics

### 📊 Mark Management
- **Two-test system**: Test 1 (40 marks) + Test 2 (60 marks) = 100 total
- Automatic final mark calculation
- Grade assignment (A+, A, B, C, D, F)
- Bulk mark upload for entire classes

### 📈 Reports & Analytics
- Class performance summaries
- Gender-based statistics
- Grade distribution analysis
- Overall system metrics

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/KMKCODER/eConsolidated-markschedule-cdss.git
   cd eConsolidated-markschedule-cdss
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Open your browser and go to: `http://127.0.0.1:5000`
   - Default login: **Username:** `admin` **Password:** `admin123`

### 🔧 First Time Setup

1. **Login with default admin account**
2. **Create classes** (e.g., "Grade 10A", "Form 2B")
3. **Add learners** to each class
4. **Create teacher accounts** for other staff
5. **Start uploading marks**

## 💡 Usage Guide

### For Administrators

1. **Add a New Class**
   - Navigate to "Admin" → "Add Class"
   - Enter class name and description
   - Click "Add Class"

2. **Add Learners**
   - Go to a class and click "Add Learner"
   - Enter learner name and select gender
   - Click "Add Learner"

3. **Create Teacher Accounts**
   - Go to "Admin" → "Add User"
   - Fill in username, password, and select "Teacher" role
   - Click "Register User"

### For Teachers & Admins

1. **Upload Marks**
   - Navigate to a class
   - Click "Upload Marks"
   - Enter Test 1 marks (0-40) and Test 2 marks (0-60)
   - Click "Upload Marks"

2. **View Reports**
   - Go to "Reports" to see performance analytics
   - View class summaries, gender statistics, and grade distributions

## 🗂️ Project Structure

```
eConsolidated-markschedule-cdss/
├── app.py                 # Main Flask application
├── auth.py               # Authentication routes
├── routes.py             # Application routes
├── requirements.txt      # Python dependencies
├── markschedule.db      # SQLite database (auto-created)
├── templates/           # HTML templates
│   ├── base.html        # Base layout
│   ├── dashboard.html   # Dashboard page
│   ├── auth/           # Authentication templates
│   ├── classes/        # Class management templates
│   ├── learners/       # Learner management templates
│   ├── marks/          # Mark upload templates
│   ├── users/          # User management templates
│   └── reports.html    # Reports page
└── static/             # Static files
    ├── css/style.css   # Custom styling
    └── js/main.js      # JavaScript functionality
```

## 🗄️ Database Schema

### Users Table
- `id` (Primary Key)
- `username` (Unique)
- `password_hash`
- `role` (admin/teacher)
- `created_at`

### Classes Table
- `id` (Primary Key)
- `name` (Unique)
- `description`
- `created_at`

### Learners Table
- `id` (Primary Key)
- `name`
- `gender` (male/female)
- `class_id` (Foreign Key → Classes)
- `created_at`

### Marks Table
- `id` (Primary Key)
- `learner_id` (Foreign Key → Learners, Unique)
- `test1_mark` (0-40)
- `test2_mark` (0-60)
- `final_mark` (Auto-calculated: test1_mark + test2_mark)
- `created_at`
- `updated_at`

## 🔒 Security Features

- Password hashing using Werkzeug security
- Session-based authentication
- Role-based access control
- SQL injection protection with parameterized queries
- CSRF protection through Flask sessions

## 🎨 Design Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Bootstrap 5**: Modern, clean interface
- **Interactive Elements**: Hover effects, animations, live calculations
- **Grade Color Coding**: Visual representation of performance levels
- **Print-Friendly**: Reports can be printed with clean formatting

## 🔧 Configuration

### Database Configuration
The application uses SQLite by default. To change the database:

```python
# In app.py
app.config['DATABASE'] = 'your_database_name.db'
```

### Security Configuration
**⚠️ Important for Production:**

```python
# Change the secret key in app.py
app.secret_key = 'your-secure-secret-key-here'
```

### Default Admin Account
Change the default admin password in `app.py`:

```python
# In init_db() function
admin_password = generate_password_hash('your-secure-password')
```

## 📱 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Contact the development team

## 🔄 Version History

- **v1.0.0** (2026) - Initial release
  - Complete mark management system
  - User authentication and authorization
  - Reports and analytics
  - Responsive web interface

---
