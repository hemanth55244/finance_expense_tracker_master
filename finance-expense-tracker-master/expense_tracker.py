import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from database import get_user_expenses, get_user_income, get_user_budget
import os

CHART_PATH = 'static/charts'

def ensure_chart_directory():
    os.makedirs(CHART_PATH, exist_ok=True)

def get_user_summary(user_id, period='year'):
    # Get date range
    today = datetime.now()
    if period == 'month':
        start_date = today.replace(day=1).strftime('%Y-%m-%d')
    else:  # year
        start_date = today.replace(month=1, day=1).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    
    # Get expenses and income
    expenses = get_user_expenses(user_id, start_date, end_date)
    income = get_user_income(user_id, start_date, end_date)
    
    # Calculate totals
    total_expenses = sum(expense['amount'] for expense in expenses)
    total_income = sum(inc['amount'] for inc in income)
    savings = total_income - total_expenses
    
    # Get budget info
    budget = get_user_budget(user_id)
    budget_amount = budget['amount'] if budget else 0
    budget_status = {
        'exceeded': total_expenses > budget_amount if budget else False,
        'percentage': (total_expenses / budget_amount * 100) if budget and budget_amount > 0 else 0
    }
    
    return {
        'total_expenses': total_expenses,
        'total_income': total_income,
        'savings': savings,
        'budget_status': budget_status
    }

def generate_expense_chart(user_id, chart_type='pie', period='month'):
    ensure_chart_directory()
    
    # Get date range
    today = datetime.now()
    if period == 'month':
        start_date = today.replace(day=1).strftime('%Y-%m-%d')
    else:  # year
        start_date = today.replace(month=1, day=1).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    
    # Get expenses
    expenses = get_user_expenses(user_id, start_date, end_date)
    
    if not expenses:
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(expenses)
    
    plt.figure(figsize=(10, 6))
    plt.style.use('default')
    
    if chart_type == 'pie':
        # Generate pie chart of expenses by category
        category_expenses = df.groupby('category')['amount'].sum()
        plt.pie(category_expenses, labels=category_expenses.index, autopct='%1.1f%%')
        plt.title('Expenses by Category')
        filename = f'pie_chart_{user_id}_{period}.png'
    else:  # bar
        # Generate bar chart of daily expenses
        daily_expenses = df.groupby('date')['amount'].sum()
        daily_expenses.plot(kind='bar')
        plt.title('Daily Expenses')
        plt.xlabel('Date')
        plt.ylabel('Amount')
        plt.xticks(rotation=45)
        filename = f'bar_chart_{user_id}_{period}.png'
    
    # Save chart
    filepath = os.path.join(CHART_PATH, filename)
    plt.savefig(filepath, bbox_inches='tight')
    plt.close()
    
    return filename

def generate_monthly_report(user_id):
    # Get yearly data
    summary = get_user_summary(user_id, 'year')

    # Generate charts
    pie_chart = generate_expense_chart(user_id, 'pie', 'year')
    bar_chart = generate_expense_chart(user_id, 'bar', 'year')
    
    return {
        'summary': summary,
        'charts': {
            'pie': pie_chart,
            'bar': bar_chart
        }
    }

def check_budget_alert(user_id):
    summary = get_user_summary(user_id)
    budget = get_user_budget(user_id)
    
    if not budget:
        return None
    
    return {
        'exceeded': summary['budget_status']['exceeded'],
        'percentage': summary['budget_status']['percentage'],
        'amount': budget['amount']
    }
