from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Placeholder for accounts (to be replaced with a database later)
SAMPLE_ACCOUNTS = [
    {"id": 1, "name": "Checking Account", "balance": 2500.00},
    {"id": 2, "name": "Savings Account", "balance": 15000.00},
    {"id": 3, "name": "Business Account", "balance": 50000.00},
]

# Placeholder for login credentials (for testing purposes)
SAMPLE_USERS = {
    "test": "test",
}

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def handle_login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Check credentials
    if username in SAMPLE_USERS and SAMPLE_USERS[username] == password:
        return redirect(url_for('dashboard'))
    else:
        return "Invalid username or password", 401

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/transfer')
def transfer():
    # Pass sample accounts to the template
    return render_template('transfer.html', accounts=SAMPLE_ACCOUNTS)

@app.route('/transfer', methods=['POST'])
def process_transfer():
    from_account_id = int(request.form.get('fromAccount'))
    to_account = request.form.get('toAccount')
    amount = float(request.form.get('amount'))
    notes = request.form.get('notes')
    frequency = request.form.get('frequency')

    # Log transfer details (this will eventually be replaced with database logic)
    print(f"Transfer from Account ID: {from_account_id}")
    print(f"To Account: {to_account}")
    print(f"Amount: {amount}")
    print(f"Notes: {notes}")
    print(f"Frequency: {frequency}")

    return "Transfer processed successfully!"

@app.route('/history')
def transaction_history():
    filter_type = request.args.get("type")
    # Filter logic can be added here once the database is implemented
    if filter_type == "debit":
        return "Filtered for Expenses (Debit)"
    elif filter_type == "credit":
        return "Filtered for Income (Credit)"
    elif filter_type == "transfer":
        return "Filtered for Transfers"
    else:
        return render_template('history.html')

@app.route('/register')
def register():
    return render_template('registration.html')


if __name__ == '__main__':
    app.run(debug=True)
