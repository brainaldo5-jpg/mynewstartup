import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import google.generativeai as genai
from firebase_admin import credentials, firestore, initialize_app

app = Flask(__name__)
# IMPORTANT: Change this to a random string in Vercel Env Vars
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret-123")

# 1. FIREBASE SETUP
# This uses Environment Variables set in Vercel for security
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

# 2. GEMINI AI SETUP
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/app')
def main_app():
    # We use a placeholder email for testing if session is empty
    email = session.get('user_email', 'tester@example.com')
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
    if not email:
        return jsonify({"error": "session_expired"}), 401

    user_ref = db.collection('users').document(email)
    user_doc = user_ref.get()
    
    # --- LIMIT LOGIC ---
    user_data = user_doc.to_dict() if user_doc.exists else {"count": 0, "is_paid": False}
    is_paid = user_data.get('is_paid', False)
    count = user_data.get('count', 0)

    # If NOT paid and count is 3 or more, block them
    if not is_paid and count >= 3:
        return jsonify({"error": "limit_reached"}), 403

    # --- AI GENERATION ---
    user_prompt = request.json.get('prompt')
    try:
        response = model.generate_content(f"Act as a Senior Architect. {user_prompt}")
        
        # Increment prompt count in Firebase
        user_ref.set({"count": count + 1}, merge=True)
        
        return jsonify({"result": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/unlock')
def unlock():
    # We pass the Paystack Public Key here so unlock.html can use it
    paystack_pk = os.getenv("PAYSTACK_PUBLIC_KEY")
    return render_template('unlock.html', paystack_key=paystack_pk)

@app.route('/payment_success')
def payment_success():
    email = session.get('user_email')
    if email:
        # Update user to PRO status
        db.collection('users').document(email).set({"is_paid": True}, merge=True)
        
    return render_template('success.html') # Create a simple success page or redirect

if __name__ == '__main__':
    app.run(debug=True)