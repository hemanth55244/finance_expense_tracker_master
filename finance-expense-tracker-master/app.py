from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
from database import init_db, add_user, verify_user, add_expense, add_income, set_user_budget
from expense_tracker import get_user_summary, generate_monthly_report, check_budget_alert
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize database
init_db()

# Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html')
        
        if add_user(username, email, password):
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username or email already exists', 'error')
    
    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = verify_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    summary = get_user_summary(user_id)
    budget_alert = check_budget_alert(user_id)
    report = generate_monthly_report(user_id)
    
    return render_template('dashboard.html',
                         summary=summary,
                         budget_alert=budget_alert,
                         charts=report['charts'])

@app.route('/add-expense', methods=['GET', 'POST'])
@login_required
def add_expense_route():
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            category = request.form['category']
            description = request.form['description']
            date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            
            add_expense(session['user_id'], amount, category, description, date)
            flash('Expense added successfully!', 'success')
            return redirect(url_for('dashboard'))
        except ValueError:
            flash('Invalid input. Please check your values.', 'error')
    
    return render_template('add_expense.html')

@app.route('/add-income', methods=['GET', 'POST'])
@login_required
def add_income_route():
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            description = request.form['description']
            date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            
            add_income(session['user_id'], amount, description, date)
            flash('Income added successfully!', 'success')
            return redirect(url_for('dashboard'))
        except ValueError:
            flash('Invalid input. Please check your values.', 'error')
    
    return render_template('add_income.html')

@app.route('/budget', methods=['GET', 'POST'])
@login_required
def budget():
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            period = request.form['period']
            
            set_user_budget(session['user_id'], amount, period)
            flash('Budget updated successfully!', 'success')
            return redirect(url_for('dashboard'))
        except ValueError:
            flash('Invalid input. Please check your values.', 'error')
    
    return render_template('budget.html')

@app.route('/reports')
@login_required
def reports():
    user_id = session['user_id']
    report = generate_monthly_report(user_id)
    return render_template('reports.html', report=report)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
