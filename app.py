from dotenv import load_dotenv
load_dotenv() 
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from database import Database,db,User
from flask_cors import CORS
import os

# Dynamically get the root project directory (where this file lives)
base_dir = os.path.abspath(os.path.dirname(__file__))
# Build full paths for template and static folders
template_dir = os.path.join(base_dir, "views")
static_dir = os.path.join(base_dir, "assets")
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key =  os.getenv('SECRET_KEY') # Set a secret key for session management
CORS(app) # Enable CORS for all routes
Database.init_app(app)

@app.route('/')
def index():
    recent_donations = Database.get_recent_donations(5)
    return render_template('index.html', recent_donations=recent_donations)

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

    Database.store_chatbot_response(question, answer)
    return jsonify({'status': 'success'})

@app.route('/complete_order', methods=['POST'])
def complete_order():
    # Check if user is logged in
    if 'user' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    # Get JSON data from request
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400

    # Debug: print received data
    print("Received data:", data)

    # Get and validate emails
    donor_email = data.get('donor_email')
    receiver_email = session.get('user', {}).get('email')
    chatbot_responses = data.get('chatbot_responses', {})

    # Validate required fields
    if not donor_email:
        return jsonify({
            'error': 'Missing donor_email in request data'
        }), 400
    
    if not receiver_email:
        return jsonify({
            'error': 'User email not found in session'
        }), 400

    try:
        # Verify both users exist first (case-insensitive search)
        donor = User.query.filter(User.email.ilike(donor_email)).first()
        receiver = User.query.filter(User.email.ilike(receiver_email)).first()

        if not donor:
            return jsonify({
                'error': f'Donor with email {donor_email} not found'
            }), 404
            
        if not receiver:
            return jsonify({
                'error': f'Receiver with email {receiver_email} not found'
            }), 404

        # Create the order
        filename, order_data = Database.create_order(
            donor.email,  # Use the exact email from DB
            receiver.email,
            chatbot_responses
        )
        
        # Send email
        success, message = Database.send_donation_email(
            filename,
            donor.email,
            receiver.email,
            chatbot_responses
        )

        return jsonify({
            'message': 'Order completed successfully',
            'order_id': order_data.id,
            'email_status': success,
            'details': message
        }), 200

    except Exception as e:
        print(f"Error in complete_order: {str(e)}")  # Debug print
        return jsonify({'error': f'Server error: {str(e)}'}), 500  
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

        try:
            Database.register_user(name, email, password, contact, address)
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(str(e), 'error')
            return redirect(url_for('register'))
    else:
        return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user_data = Database.login_user(email, password)

        if user_data:
            # Store only serializable data in session
            session['user'] = {
                'id': user_data.id,
                'name': user_data.name,
                'email': user_data.email,
                'contact': user_data.contact,
                'address': user_data.address
            }
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
            'user_email': session['user']['email']
        }

        Database.create_donation(**donation_data)
        flash('Donation submitted successfully', 'success')
        return redirect(url_for('view_donations'))
    
    return render_template('make_donation.html')

@app.route('/view_donation')
def view_donations():
    donations = Database.get_all_donations()
    return render_template('view_donation.html', donations=donations)

@app.route('/user_posts/<user_email>')
def user_posts(user_email):
    donations = Database.get_user_donations(user_email)
    return render_template('user_posts.html', donations=donations, user_email=user_email)

@app.route('/users')
def users():
    if 'user' not in session:
        flash('Please log in to view this page', 'error')
        return redirect(url_for('login'))

    users_list = Database.get_all_users()
    return render_template('users.html', users=users_list)

@app.route('/profile')
def profile():
    if 'user' not in session:
        flash('Please log in to view your profile', 'error')
        return redirect(url_for('login'))
    return render_template("profile.html")

@app.route('/test_email')
def test_email():
    success, msg = Database.send_donation_email(
        "dummy.txt",
        "srirnsametalmart@gmail.com",
        "srirama.ai23@rvce.edu.in",
        {
            "Test Q1": "Test A1",
            "Test Q2": "Test A2"
        }
    )
    return jsonify({'success': success, 'message': msg})


if __name__ == '__main__':
    app.run(debug=True)