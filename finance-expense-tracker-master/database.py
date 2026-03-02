import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

def get_db_connection():
    conn = sqlite3.connect('expense_tracker.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Create expenses table
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        date DATE NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # Create income table
    c.execute('''CREATE TABLE IF NOT EXISTS income (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        description TEXT,
        date DATE NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # Create budget table
    c.execute('''CREATE TABLE IF NOT EXISTS budget (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        period TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    conn.commit()
    conn.close()

def add_user(username, email, password):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        password_hash = generate_password_hash(password)
        c.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                 (username, email, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = get_db_connection()
    c = conn.cursor()
    user = c.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password_hash'], password):
        return dict(user)
    return None

def add_expense(user_id, amount, category, description, date):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO expenses (user_id, amount, category, description, date)
                 VALUES (?, ?, ?, ?, ?)''',
              (user_id, amount, category, description, date))
    conn.commit()
    conn.close()

def add_income(user_id, amount, description, date):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO income (user_id, amount, description, date)
                 VALUES (?, ?, ?, ?)''',
              (user_id, amount, description, date))
    conn.commit()
    conn.close()

def get_user_expenses(user_id, start_date=None, end_date=None):
    conn = get_db_connection()
    c = conn.cursor()
    
    if start_date and end_date:
        expenses = c.execute('''SELECT * FROM expenses 
                              WHERE user_id = ? AND date BETWEEN ? AND ?
                              ORDER BY date DESC''',
                           (user_id, start_date, end_date)).fetchall()
    else:
        expenses = c.execute('''SELECT * FROM expenses 
                              WHERE user_id = ? 
                              ORDER BY date DESC''',
                           (user_id,)).fetchall()
    conn.close()
    return [dict(expense) for expense in expenses]

def get_user_income(user_id, start_date=None, end_date=None):
    conn = get_db_connection()
    c = conn.cursor()
    
    if start_date and end_date:
        income = c.execute('''SELECT * FROM income 
                            WHERE user_id = ? AND date BETWEEN ? AND ?
                            ORDER BY date DESC''',
                         (user_id, start_date, end_date)).fetchall()
    else:
        income = c.execute('''SELECT * FROM income 
                            WHERE user_id = ? 
                            ORDER BY date DESC''',
                         (user_id,)).fetchall()
    conn.close()
    return [dict(inc) for inc in income]

def get_user_budget(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    budget = c.execute('SELECT * FROM budget WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return dict(budget) if budget else None

def set_user_budget(user_id, amount, period):
    conn = get_db_connection()
    c = conn.cursor()
    
    # Check if budget exists
    existing = c.execute('SELECT id FROM budget WHERE user_id = ?', (user_id,)).fetchone()
    
    if existing:
        c.execute('''UPDATE budget 
                    SET amount = ?, period = ?
                    WHERE user_id = ?''',
                 (amount, period, user_id))
    else:
        c.execute('''INSERT INTO budget (user_id, amount, period)
                    VALUES (?, ?, ?)''',
                 (user_id, amount, period))
    
    conn.commit()
    conn.close()
