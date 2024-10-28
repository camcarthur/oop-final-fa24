# main.py

from flask import Flask, render_template, request, redirect, url_for, session
from user_auth import UserAuth
from bank_system import BankSystem

app = Flask(__name__)
app.secret_key = ''  # Replace with a secure, random key

# Initialize banking system and user authentication
bank_system = BankSystem()
user_auth = UserAuth(bank_system)

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')  # The home page with login/register options

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        result = user_auth.register_user(username, password)
        if result['success']:
            return redirect(url_for('login'))
        return render_template('register.html', error=result['message'])
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = user_auth.login_user(username, password)
        if user:
            session['user_id'] = user.user_id  # Store user ID in session
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user_accounts = bank_system.get_user_accounts(user_id)
    return render_template('dashboard.html', accounts=user_accounts)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

# Additional routes for other banking operations
@app.route('/deposit', methods=['POST'])
def deposit():
    if 'user_id' in session:
        account_id = request.form['account_id']
        amount = float(request.form['amount'])
        bank_system.deposit(session['user_id'], account_id, amount)
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/withdraw', methods=['POST'])
def withdraw():
    if 'user_id' in session:
        account_id = request.form['account_id']
        amount = float(request.form['amount'])
        bank_system.withdraw(session['user_id'], account_id, amount)
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/transfer', methods=['POST'])
def transfer():
    if 'user_id' in session:
        from_account = request.form['from_account']
        to_account = request.form['to_account']
        amount = float(request.form['amount'])
        bank_system.transfer_funds(session['user_id'], from_account, to_account, amount)
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
