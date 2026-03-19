import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from firebase_admin import credentials, firestore, initialize_app

app = Flask(__name__)
# Set a secret key for sessions
app.secret_key = os.getenv("FLASK_SECRET", "startup-dev-key-2026")

# 1. FIREBASE SETUP
# (Uses Environment Variables from Vercel)
if not len(initialize_app.__defaults__):
    cred_dict = {
        "type": "service_account",
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "token_uri": "https://oauth2.googleapis.com/token",
    }
    cred = credentials.Certificate(cred_dict)
    initialize_app(cred)

db = firestore.client()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/app')
def main_app():
    # Use a test email if no session exists
    email = session.get('user_email', 'guest_tester@example.com')
    session['user_email'] = email
    
    user_ref = db.collection('users').document(email)
    user_doc = user_ref.get()
    
    is_paid = False
    if user_doc.exists:
        is_paid = user_doc.to_dict().get('is_paid', False)
    
    return render_template('app.html', is_paid=is_paid)

@app.route('/generate_prompt', methods=['POST'])
def generate():
    email = session.get('user_email')
    user_ref = db.collection('users').document(email)
    user_doc = user_ref.get()
    
    user_data = user_doc.to_dict() if user_doc.exists else {"count": 0, "is_paid": False}
    is_paid = user_data.get('is_paid', False)
    count = user_data.get('count', 0)

    # BLOCK if user hit 3 prompts and hasn't paid
    if not is_paid and count >= 3:
        return jsonify({"error": "limit_reached"}), 403

    # MOCK AI RESPONSE (Placeholder until you get capital for API)
    data = request.json
    stack = data.get('stack', 'General')
    goal = data.get('goal', 'Architecture')
    
    mock_response = f"""
🚀 {goal} Blueprint for {stack}
---------------------------------------
[PROTOTYPE MODE: AI DISCONNECTED]

Proposed Structure:
/src
  /api       -> Route handlers
  /core      -> Middleware & Auth
  /models    -> Database schemas
  /services  -> Business logic

Security Recommendations:
1. Implement JWT for session handling.
2. Use CORS headers for cross-origin safety.
3. Sanitize all user inputs before DB entry.

(Upgrade to PRO to unlock full detailed logic)
    """
    
    # Increment the usage count
    user_ref.set({"count": count + 1}, merge=True)
    
    return jsonify({"result": mock_response})

@app.route('/unlock')
def unlock():
    pk = os.getenv("PAYSTACK_PUBLIC_KEY")
    return render_template('unlock.html', paystack_key=pk)

@app.route('/payment_success')
def payment_success():
    email = session.get('user_email')
    if email:
        db.collection('users').document(email).set({"is_paid": True}, merge=True)
    return render_template('success.html')

if __name__ == '__main__':
    app.run(debug=True)