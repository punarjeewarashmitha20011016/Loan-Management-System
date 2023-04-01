from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True

from collections import defaultdict

loan_amounts = defaultdict(int)
pending_loans = []
max_loan_amount = 1000
current_balance = 1000
users = []


@app.route('/', methods=['GET', 'POST'])
def home():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        # current_balance[session['username']] = 0
        users.append(session['username'])
        loan_amounts[username] = 0
        print(loan_amounts)
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    if request.method == 'POST':
        loan_amount = int(request.form['loan_amount'])
        if loan_amount > max_loan_amount:
            return render_template('dashboard.html', error_message='Loan amount exceeds maximum limit')
        pending_loans[username] = loan_amount
        return redirect(url_for('dashboard'))

    total_amount = 0
    for loan in pending_loans:
        if loan['username'] == username:
            total_amount += loan['amount']

    loan_balance = max_loan_amount - total_amount
    # loan_balance = current_balance
    return render_template('dashboard.html', username=username, loan_amount=loan_amounts[username],
                           max_loan_amount=max_loan_amount, pending_loans=pending_loans, loan_balance=loan_balance)


@app.route('/request_loan', methods=['POST'])
def request_loan():
    username = session['username']
    # loan_amount = loan_amounts[username]
    loan_amount_str = request.form['loan_amount']
    loan_amount = int(loan_amount_str)
    print(loan_amount)
    # Check that the loan amount is valid
    if loan_amount <= 0:
        print('Invalid loan amount.')
        return redirect(url_for('dashboard'))
    if current_balance > max_loan_amount:
        print('Loan amount exceeds maximum limit.')
        return redirect(url_for('dashboard'))
    if current_balance > max_loan_amount:
        print('Loan amount exceeds maximum limit.')
        return redirect(url_for('dashboard'))
    current_balance - loan_amount
    # Add the loan request to the list of pending loans
    loan_id = len(pending_loans) + 1

    print(loan_id)
    pending_loans.append(
        {'id': loan_id, 'username': username, 'amount': loan_amount, 'approvals': set(), 'rejects': set(), })

    print('Loan request submitted successfully.')
    return redirect(url_for('dashboard'))


@app.route('/approve_loan/<int:loan_id>', methods=['GET', 'POST'])
def approve_loan(loan_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    for loan in pending_loans:
        if loan['id'] != loan_id:
            print("vote")
            print(loan_id)
            return redirect(url_for('dashboard'))

    if request.method == 'POST':
        vote = request.form['vote']
        total_users = len(users) / 2
        print(vote)

        for loan in pending_loans:
            if loan['id'] == loan_id:
                if username in loan['approvals']:
                    print("ap 123")
                    return render_template('vote.html', error_message='You have already voted', already_voted="true",
                                           loan={"amount": loan["amount"], "borrower": loan["username"]})

        if vote == 'approve':
            # pending_loans[loan_id]['approvals'][username] = True
            for loan in pending_loans:
                if loan['id'] == loan_id:
                    loan['approvals'].add(username)

        elif vote == 'reject':
            # pending_loans[loan_id]['approvals'][username] = True
            for loan in pending_loans:
                if loan['id'] == loan_id:
                    loan['rejects'].add(username)
        # elif vote == 'reject':
        #     pending_loans[loan_id]['votes'][username] = False

        approvals_sum = 0
        for loan in pending_loans:
            if loan['id'] == loan_id:
                approvals_sum += len(loan['approvals'])
        print("pending_loans")
        if approvals_sum > total_users:
            # borrower = pending_loans[loan_id]['borrower']
            # loan_amount = pending_loans[loan_id]['loan_amount']
            # loan_amounts[borrower] += loan_amount
            total_amount = 0
            for loan in pending_loans:
                if loan['id'] == loan_id:
                    total_amount += loan['amount']
            current_balance - total_amount

            print("amount")
            print(total_amount)
            print(pending_loans)
            for loan in pending_loans:
                if loan['id'] == loan_id:
                    pending_loans.remove(loan)
                    print(pending_loans)  # del pending_loans[loan_id]
        print("12")
        print(pending_loans)
        return redirect(url_for('dashboard'))

    # if username in pending_loans[loan_id]['votes']:
    #     return render_template('vote.html', error_message='You have already voted')

    print(pending_loans)
    return render_template('vote.html', loan=pending_loans[loan_id])


if __name__ == '__main__':
    sess = Session()
    sess.init_app(app)
    app.run(debug=True)
