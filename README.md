# Mini Secure Fintech Wallet — Phase 1 (Basic Working App)

This is **Phase 1**: a fully working wallet app with NO security controls yet.
This is intentional — the assignment requires you to first show weaknesses,
then add controls, then re-test ("before-and-after" testing).

## Features included
- Create/register an account
- Login / Logout
- View balance
- Transfer funds to another registered user
- View transaction history

## How to run

1. Open a terminal in this folder.
2. (Recommended) Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Mac/Linux
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the app:
   ```
   python app.py
   ```
5. Open your browser to: http://127.0.0.1:5000

The database (`instance/wallet.db`) is created automatically on first run.
Every new registered user starts with a balance of Rs. 1000 (for demo purposes).

## Try it out
1. Register two users, e.g. `ali` and `sara`.
2. Login as `ali`, go to Transfer, send Rs. 200 to `sara`.
3. Check the dashboard — Ali's balance decreased.
4. Logout, login as `sara` — her balance increased.
5. Check History for both users — the transaction appears for both.

## ⚠️ Known weaknesses (deliberately left in for Phase 2 analysis)
Do NOT fix these yet — you'll use these as your "before" state for the
security analysis and before/after testing. Some obvious ones to start
your analysis with:

1. Passwords are stored in **plain text** in the database.
2. `app.secret_key` is a **hardcoded, weak string** — sessions can be forged.
3. No **rate limiting** on login — vulnerable to brute-force password guessing.
4. No **CSRF protection** on forms.
5. Debug mode (`debug=True`) is on — this can leak stack traces / internals.
6. Any registered user can see the full app; there's no protection against
   trying to directly reach another user's data via manipulated inputs
   (worth testing further — e.g., are transaction IDs or user IDs guessable
   anywhere?).
7. No input validation beyond basic type/emptiness checks.
8. No logging/audit trail beyond the transactions table itself.
9. No account lockout after repeated failed logins.

You are NOT expected to fix all of these — pick the most important ones,
justify why, and implement + test controls for those (see assignment
Section 5–7). This list is a starting point for your own analysis, not
a substitute for it.

## Project structure
```
wallet/
├── app.py                 # Main Flask app (all routes)
├── requirements.txt
├── instance/
│   └── wallet.db           # SQLite database (auto-created)
├── templates/               # HTML pages (Jinja2)
│   ├── base.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── transfer.html
│   └── history.html
└── static/
    └── style.css
```
