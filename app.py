import os
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_cors import CORS
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Set the location for the Restaurantly folder
loc = "C:\\Users\\SriRam.A\\Documents"

# Initialize Flask app with the correct template and static folder paths
app = Flask(__name__, 
            template_folder=os.path.join(loc, "Restaurantly","views"),
            static_folder=os.path.join(loc, "Restaurantly", "assets"))

# Set a secret key for session management
app.secret_key = 'your_secret_key_here'  # Replace with a strong, random key

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "niranjansk.ai23@rvce.edu.in"
SMTP_PASSWORD = "HarryPotter@03"

# Initialize Firebase Admin SDK
cred = credentials.Certificate(os.path.join(loc, "Restaurantly", "surplustoservice-6a995-firebase-adminsdk-gssz6-06c67d0a0c.json"))
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

# Enable CORS for all routes
CORS(app)

def send_donation_email(json_file_path, donor_email, receiver_email, order_details):
    try:
        subject = "Food Donation Details"
        body = f"""
        Hello,

        Here are the details of the food donation:

        Food Type: {order_details.get("food_type", "N/A")}
        Available Quantity: {order_details.get("available_quantity", "N/A")}
        Servings Needed: {order_details.get("question_2", {}).get("answer", "N/A")}
        Preferred Pickup/Delivery Time: {order_details.get("question_3", {}).get("answer", "N/A")}
        Pickup or Delivery: {order_details.get("question_4", {}).get("answer", "N/A")}
        Delivery Address: {order_details.get("question_5", {}).get("answer", "N/A")}

        Thank you for your donation!

        Best regards,
        The Food Rescue Team
        """

        msg = MIMEMultipart()
        msg['From'] = donor_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(donor_email, receiver_email, msg.as_string())
        server.quit()

        return True, "Email sent successfully!"
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"

@app.route('/')
def index():
    donations_ref = db.collection('donations')
    recent_donations = donations_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(5).get()
    
    donations_list = []
    for donation in recent_donations:
        donation_dict = donation.to_dict()
        donations_list.append(donation_dict)
    
    return render_template('index.html', recent_donations=donations_list)

@app.route('/store_answer', methods=['POST'])
def store_answer():
    data = request.get_json(silent=True)
    print("Received data:", data)
    
    if data is None:
        return jsonify({'status': 'error', 'message': 'No data received or JSON parsing failed'}), 400

    question = data.get('question')
    answer = data.get('answer')
    
    if not question or not answer:
        return jsonify({'status': 'error', 'message': 'Both question and answer are required'}), 400

    if os.path.exists("donations.json"):
        with open("donations.json", "r") as f:
            try:
                responses = json.load(f)
            except json.JSONDecodeError:
                responses = {}
    else:
        responses = {}

    responses[question] = answer

    with open("donations.json", "w") as f:
        json.dump(responses, f, indent=4)

    print("Updated JSON content:", responses)
    return jsonify({'status': 'success'})

@app.route('/complete_order', methods=['POST'])
def complete_order():
    if 'user' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    donor_email = data.get('donor_email')
    receiver_email = session['user']['email']
    chatbot_responses = data.get('chatbot_responses', {})

    try:
        # Get donor information
        donor_query = db.collection('users').where('email', '==', donor_email).limit(1).get()
        donor_data = None
        for doc in donor_query:
            donor_data = doc.to_dict()
            break

        # Get receiver information
        receiver_query = db.collection('users').where('email', '==', receiver_email).limit(1).get()
        receiver_data = None
        for doc in receiver_query:
            receiver_data = doc.to_dict()
            break

        if not donor_data or not receiver_data:
            return jsonify({'error': 'User information not found'}), 404

        order_data = {
            'donor': {
                'email': donor_email,
                'address': donor_data.get('address'),
                'contact': donor_data.get('contact')
            },
            'receiver': {
                'email': receiver_email,
                'address': receiver_data.get('address'),
                'contact': receiver_data.get('contact')
            },
            'order_details': chatbot_responses,
            'timestamp': datetime.now().isoformat()
        }

        # Save to Firestore
        db.collection('orders').add(order_data)

        # Save to JSON file
        filename = f"orders\\order_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(order_data, f, indent=4)

        # Send email
        success, message = send_donation_email(
            filename,
            donor_email,
            receiver_email,
            chatbot_responses
        )

        response_data = {
            'message': 'Order completed successfully',
            'filename': filename,
            'order_data': order_data,
            'email_status': {
                'success': success,
                'message': message
            }
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        contact = request.form.get('contact')
        address = request.form.get('address')

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))

        # Check if user already exists
        users_query = db.collection('users').where('email', '==', email).limit(1).get()
        if any(doc.exists for doc in users_query):
            flash('Email already registered', 'error')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        user_data = {
            'name': name,
            'email': email,
            'password': hashed_password,
            'contact': contact,
            'address': address
        }
        
        db.collection('users').add(user_data)

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    else:
        return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        users_query = db.collection('users').where('email', '==', email).limit(1).get()
        user_data = None
        for doc in users_query:
            user_data = doc.to_dict()
            break

        if user_data and check_password_hash(user_data['password'], password):
            session['user'] = user_data
            flash('Logged in successfully', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'error')
            return redirect(url_for('login'))
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/make_donation', methods=['GET', 'POST'])
def make_donation():
    if 'user' not in session:
        flash('Please log in to make a donation', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        donation_data = {
            'food_type': request.form.get('foodType'),
            'quantity': request.form.get('quantity'),
            'storage': request.form.get('storage'),
            'dietary': request.form.get('dietary'),
            'expiry_date': request.form.get('expiryDate'),
            'expiry_time': request.form.get('expiryTime'),
            'transportation': request.form.get('transportation'),
            'user_email': session['user']['email'],
            'timestamp': datetime.now()
        }

        db.collection('donations').add(donation_data)

        flash('Donation submitted successfully', 'success')
        return redirect(url_for('view_donations'))
    
    return render_template('make_donation.html')

@app.route('/view_donation')
def view_donations():
    donations_ref = db.collection('donations')
    donations_stream = donations_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
    
    donations_list = []
    for donation in donations_stream:
        donation_dict = donation.to_dict()
        donations_list.append(donation_dict)
    
    return render_template('view_donation.html', donations=donations_list)

@app.route('/user_posts/<user_email>')
def user_posts(user_email):
    donations_ref = db.collection('donations')
    user_donations = donations_ref.where('user_email', '==', user_email).order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
    
    donations_list = []
    for donation in user_donations:
        donation_dict = donation.to_dict()
        donations_list.append(donation_dict)
    
    return render_template('user_posts.html', donations=donations_list, user_email=user_email)

@app.route('/users')
def users():
    if 'user' not in session:
        flash('Please log in to view this page', 'error')
        return redirect(url_for('login'))

    users_ref = db.collection('users')
    users_stream = users_ref.stream()
    
    users_list = []
    for user in users_stream:
        user_dict = user.to_dict()
        user_dict.pop('password', None)  # Remove password from the displayed data
        users_list.append(user_dict)
    
    return render_template('users.html', users=users_list)

@app.route('/profile')
def profile():
    if 'user' not in session:
        flash('Please log in to view your profile', 'error')
        return redirect(url_for('login'))
    return render_template("profile.html")

if __name__ == '__main__':
    app.run(debug=True)