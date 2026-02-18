// Main JavaScript for eConsolidated Mark Schedule

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components when DOM is loaded
    initializeFormValidation();
    initializeMarkCalculations();
    initializeTableFeatures();
    initializeAlerts();
    initializeCSVUpload(); // Add CSV upload initialization
    
    console.log('eConsolidated Mark Schedule loaded successfully');
});

// Form Validation
function initializeFormValidation() {
    // Password confirmation validation
    const confirmPasswordInputs = document.querySelectorAll('input[name="confirm_password"]');
    confirmPasswordInputs.forEach(input => {
        input.addEventListener('input', function() {
            const password = document.querySelector('input[name="password"]').value;
            const confirmPassword = this.value;
            
            if (password !== confirmPassword) {
                this.setCustomValidity('Passwords do not match');
                this.classList.add('is-invalid');
            } else {
                this.setCustomValidity('');
                this.classList.remove('is-invalid');
            }
        });
    });
    
    // Mark input validation
    const markInputs = document.querySelectorAll('input[type="number"]');
    markInputs.forEach(input => {
        input.addEventListener('input', function() {
            const value = parseInt(this.value);
            const max = parseInt(this.max);
            const min = parseInt(this.min);
            
            if (value > max) {
                this.value = max;
                showAlert(`Maximum value is ${max}`, 'warning');
            } else if (value < min && this.value !== '') {
                this.value = min;
                showAlert(`Minimum value is ${min}`, 'warning');
            }
        });
    });
    
    // Required field highlighting
    const requiredInputs = document.querySelectorAll('input[required], select[required], textarea[required]');
    requiredInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (!this.value.trim()) {
                this.classList.add('is-invalid');
            } else {
                this.classList.remove('is-invalid');
            }
        });
        
        input.addEventListener('input', function() {
            if (this.value.trim()) {
                this.classList.remove('is-invalid');
            }
        });
    });
}

// Mark Calculations and Live Updates
function initializeMarkCalculations() {
    const markInputs = document.querySelectorAll('input[name*="test"]');
    
    markInputs.forEach(input => {
        input.addEventListener('input', function() {
            updateRowTotal(this);
        });
    });
}

function updateRowTotal(input) {
    const row = input.closest('tr');
    if (!row) return;
    
    // Extract learner ID from input name
    const learnerId = input.name.split('_')[1];
    
    const test1Input = row.querySelector(`input[name="test1_${learnerId}"]`);
    const test2Input = row.querySelector(`input[name="test2_${learnerId}"]`);
    
    const test1Value = parseInt(test1Input?.value) || 0;
    const test2Value = parseInt(test2Input?.value) || 0;
    
    // Only show preview if both values are entered
    if (test1Value > 0 && test2Value > 0) {
        const total = test1Value + test2Value;
        const totalCell = row.querySelector('td:nth-child(6)'); // Assuming total is 6th column
        
        if (totalCell) {
            totalCell.innerHTML = `
                <strong class="text-${total >= 50 ? 'success' : 'danger'}">
                    ${total}/100 <small class="text-muted">(preview)</small>
                </strong>
            `;
        }
        
        // Update status
        const statusCell = row.querySelector('td:nth-child(8)'); // Assuming status is 8th column
        if (statusCell) {
            statusCell.innerHTML = `
                <span class="badge bg-info">
                    <i class="bi bi-clock"></i> Ready to submit
                </span>
            `;
        }
    }
}

// Table Features
function initializeTableFeatures() {
    // Add sorting to tables
    const tables = document.querySelectorAll('.table');
    tables.forEach(table => {
        makeTableSortable(table);
    });
    
    // Add row highlighting
    const tableRows = document.querySelectorAll('.table tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.01)';
            this.style.transition = 'transform 0.2s ease';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
}

function makeTableSortable(table) {
    const headers = table.querySelectorAll('th');
    headers.forEach((header, index) => {
        // Skip action columns
        if (header.textContent.toLowerCase().includes('action')) return;
        
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            sortTable(table, index);
        });
    });
}

function sortTable(table, columnIndex) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    const isNumeric = rows.every(row => {
        const cellText = row.cells[columnIndex]?.textContent.trim();
        return !isNaN(parseFloat(cellText)) || cellText === '';
    });
    
    rows.sort((a, b) => {
        const aText = a.cells[columnIndex]?.textContent.trim() || '';
        const bText = b.cells[columnIndex]?.textContent.trim() || '';
        
        if (isNumeric) {
            return parseFloat(aText) - parseFloat(bText);
        } else {
            return aText.localeCompare(bText);
        }
    });
    
    // Clear and re-append sorted rows
    tbody.innerHTML = '';
    rows.forEach(row => tbody.appendChild(row));
}

// Alert System
function initializeAlerts() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-20px)';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });
}

function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.container');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${getAlertIcon(type)} ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.insertAdjacentElement('afterbegin', alert);
    
    // Auto-dismiss after 4 seconds
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => alert.remove(), 300);
    }, 4000);
}

function getAlertIcon(type) {
    const icons = {
        'success': '<i class="bi bi-check-circle"></i>',
        'error': '<i class="bi bi-exclamation-triangle"></i>',
        'warning': '<i class="bi bi-exclamation-circle"></i>',
        'info': '<i class="bi bi-info-circle"></i>'
    };
    return icons[type] || icons['info'];
}

// Form Submission Handlers
function handleFormSubmission(form, showLoading = true) {
    if (showLoading) {
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            const originalText = submitButton.innerHTML;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
            submitButton.disabled = true;
            
            // Re-enable after 10 seconds as fallback
            setTimeout(() => {
                submitButton.innerHTML = originalText;
                submitButton.disabled = false;
            }, 10000);
        }
    }
}

// Utility Functions
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

function calculatePercentage(value, total) {
    if (total === 0) return 0;
    return Math.round((value / total) * 100);
}

// Export functions for global use
window.eConsolidatedMS = {
    showAlert,
    confirmAction,
    handleFormSubmission,
    formatNumber,
    calculatePercentage
};

// Handle form submissions to show loading states
document.addEventListener('submit', function(e) {
    handleFormSubmission(e.target);
});

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K to focus search (if exists)
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[type="search"], input[placeholder*="search" i]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape to close modals/alerts
    if (e.key === 'Escape') {
        const alerts = document.querySelectorAll('.alert .btn-close');
        alerts.forEach(closeBtn => closeBtn.click());
    }
});

// Console welcome message
console.log(`
╔═══════════════════════════════════════════════════════╗
║           eConsolidated Mark Schedule System          ║
║               📚 Educational Excellence 📚             ║  
║                                                       ║
║  Built with: Flask + Bootstrap + SQLite               ║
║  Version: 1.0.0                                       ║
║  Year: 2026                                           ║
╚═══════════════════════════════════════════════════════╝
`);

// CSV Upload Functions
function initializeCSVUpload() {
    // CSV Upload file validation
    const csvFileInputs = document.querySelectorAll('input[type="file"][accept=".csv"]');
    csvFileInputs.forEach(input => {
        input.addEventListener('change', function() {
            validateCSVFile(this);
        });
    });
    
    // CSV upload form enhancement
    const csvForms = document.querySelectorAll('form[enctype="multipart/form-data"]');
    csvForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const fileInput = form.querySelector('input[type="file"]');
            if (fileInput && !validateCSVFile(fileInput)) {
                e.preventDefault();
                return false;
            }
            
            // Show enhanced loading state for CSV upload
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing CSV...';
                submitBtn.disabled = true;
            }
        });
    });
}

function validateCSVFile(input) {
    const file = input.files[0];
    
    if (file) {
        // Check file type
        if (!file.name.toLowerCase().endsWith('.csv')) {
            showCSVFileError(input, 'Please select a CSV file (.csv extension required)');
            return false;
        }
        
        // Check file size (limit to 5MB)
        const maxSize = 5 * 1024 * 1024; // 5MB
        if (file.size > maxSize) {
            showCSVFileError(input, 'File size must be less than 5MB');
            return false;
        }
        
        // Show success
        showCSVFileSuccess(input, `File selected: ${file.name} (${formatFileSize(file.size)})`);
        return true;
    }
    
    return false;
}

function showCSVFileError(input, message) {
    input.classList.add('is-invalid');
    input.classList.remove('is-valid');
    
    // Remove existing feedback
    const existingFeedback = input.parentNode.querySelector('.invalid-feedback');
    if (existingFeedback) {
        existingFeedback.remove();
    }
    
    // Add error feedback
    const feedback = document.createElement('div');
    feedback.className = 'invalid-feedback';
    feedback.textContent = message;
    input.parentNode.appendChild(feedback);
    
    // Show alert
    showAlert(message, 'error');
}

function showCSVFileSuccess(input, message) {
    input.classList.add('is-valid');
    input.classList.remove('is-invalid');
    
    // Remove existing feedback
    const existingFeedback = input.parentNode.querySelector('.invalid-feedback');
    if (existingFeedback) {
        existingFeedback.remove();
    }
    
    // Update small text
    const smallText = input.parentNode.querySelector('.form-text');
    if (smallText) {
        smallText.textContent = message;
        smallText.className = 'form-text text-success';
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Enhanced CSV Preview Function
function previewCSVContent(file, callback) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const csvContent = e.target.result;
        const lines = csvContent.split('\n').slice(0, 6); // Preview first 5 rows + header
        callback(lines);
    };
    reader.readAsText(file);
}

// CSV Template Download Functions
function downloadLearnerCSVTemplate() {
    const csvContent = "name,gender,class_name\nJohn Smith,male,Grade 10A\nJane Doe,female,Grade 10A\nMary Johnson,female,Grade 10B";
    downloadCSVFile('learners_template.csv', csvContent);
}

function downloadMarksCSVTemplate() {
    const csvContent = "learner_name,test1_mark,test2_mark,class_name\nJohn Smith,35,55,Grade 10A\nJane Doe,38,52,Grade 10A\nMary Johnson,32,48,Grade 10B";
    downloadCSVFile('marks_template.csv', csvContent);
}

function downloadCSVFile(filename, content) {
    const blob = new Blob([content], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    showAlert(`Template downloaded: ${filename}`, 'success');
}