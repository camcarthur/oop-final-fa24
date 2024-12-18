from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps
from datetime import timedelta

app = Flask(__name__)
app.secret_key = ".env"
app.permanent_session_lifetime = timedelta(minutes=30) 
# Test accounts
SAMPLE_ACCOUNTS = [
    {"id": 1, "name": "Checking Account", "balance": 2500.00},
    {"id": 2, "name": "Savings Account", "balance": 15000.00},
    {"id": 3, "name": "Business Account", "balance": 50000.00},
]

# Test credentials for login
SAMPLE_USERS = {
    "test":"test",
    "admin":"admin",
}

# Payload for admin page 
FAKE_USERS = [
    {"id": 1, "username": "colinm", "email": "email@1.com", "num_accounts": "5", "balance": 42500.00},
    {"id": 2, "username": "jakep", "email": "email@2.com", "num_accounts": "8", "balance": 2315000.00},
    {"id": 3, "username": "carloso", "email": "email@3.com", "num_accounts": "1", "balance": 50000.00},
]

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Authenticate user
        if username in SAMPLE_USERS and SAMPLE_USERS[username] == password:
            session["username"] = username  # cache username
            if username == "admin":
                return redirect(url_for("admin"))
            else:
                return redirect(url_for("dashboard"))
        else:
            return "Invalid username or password", 401
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Mock 
    user_name = "Colin McArthur"  # Placeholder username
    transactions = [
        {"date": "08/03/2024", "type": "expense", "description": "Marty S.A.S.", "amount": 852.04},
        {"date": "02/03/2024", "type": "expense", "description": "Groceries", "amount": 120.50},
        {"date": "01/03/2024", "type": "expense", "description": "Royer", "amount": 487.09},
        {"date": "11/03/2024", "type": "income", "description": "Salary", "amount": 707.95},
        {"date": "08/03/2024", "type": "income", "description": "Bonus", "amount": 1931.61},
        {"date": "07/03/2024", "type": "income", "description": "Refund", "amount": 640.10},
    ]
    pending_transfers = 3  # Placeholder for pending transfers

    # Summed up balance
    total_balance = sum(account["balance"] for account in SAMPLE_ACCOUNTS)

    return render_template(
        'dashboard.html',
        user_name=user_name,
        transactions=transactions,
        pending_transfers=pending_transfers,
        total_balance=total_balance,
    )

@app.route('/transfer')
@login_required
def transfer():
    return render_template('transfer.html', accounts=SAMPLE_ACCOUNTS)

@app.route('/transfer', methods=['POST'])
@login_required
def process_transfer():
    from_account_id = int(request.form.get('fromAccount'))
    transfer_type = request.form.get('transferType')
    amount = float(request.form.get('amount'))

    from_account = next((acc for acc in SAMPLE_ACCOUNTS if acc["id"] == from_account_id), None)

    if not from_account or from_account["balance"] < amount:
        return "Insufficient funds or invalid account.", 400

    if transfer_type == "internal":
        to_account_id = int(request.form.get('toInternalAccount'))
        to_account = next((acc for acc in SAMPLE_ACCOUNTS if acc["id"] == to_account_id), None)
        if not to_account:
            return "Invalid target account.", 400

        # Process internal transfer
        from_account["balance"] -= amount
        to_account["balance"] += amount
        print(f"Internal Transfer: ${amount} from {from_account['name']} to {to_account['name']}")

    elif transfer_type == "external":
        to_account = request.form.get('toExternalAccount')
        notes = request.form.get('notesExternal')

        # Process external transfer 
        from_account["balance"] -= amount
        print(f"External Transfer: ${amount} from {from_account['name']} to External Account {to_account}. Notes: {notes}")

    return "Transfer processed successfully!"

@app.route('/history')
@login_required
def transaction_history():
    filter_type = request.args.get("type")
    # Basic filtering (replace with db)
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

@app.route('/admin')
@login_required
def admin():
    # Pass user data 
    return render_template('admin.html', users=FAKE_USERS)

@app.route('/logout')
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route('/admin/transaction', methods=['POST'])
@login_required
def add_transaction():
    if session.get("username") != "admin":
        return "Unauthorized", 403

    account_id = int(request.form.get("account_id"))
    amount = float(request.form.get("amount"))
    transaction_type = request.form.get("type")

    # Find account by account_id
    account = next((acc for acc in SAMPLE_ACCOUNTS if acc["id"] == account_id), None)
    if not account:
        return f"Account with ID {account_id} not found.", 404

    # Transfer with error handling
    if transaction_type == "deposit":
        account["balance"] += amount
        message = f"Successfully deposited ${amount:.2f} to account {account_id}."
    elif transaction_type == "withdraw":
        if account["balance"] < amount:
            return f"Insufficient funds in account {account_id}.", 400
        account["balance"] -= amount
        message = f"Successfully withdrew ${amount:.2f} from account {account_id}."

    return render_template("admin.html", users=FAKE_USERS, message=message)


if __name__ == '__main__':
    app.run(debug=True)
