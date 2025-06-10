import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

db = SQLAlchemy()

# Email configuration from environment
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')  # default if not set
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))  # convert to intnp
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    contact = db.Column(db.String(20))
    address = db.Column(db.String(200))
    donations = db.relationship('Donation', backref='donor', lazy=True)
    orders_as_donor = db.relationship('Order', foreign_keys='Order.donor_id', backref='donor', lazy=True)
    orders_as_receiver = db.relationship('Order', foreign_keys='Order.receiver_id', backref='receiver', lazy=True)

class Donation(db.Model):
    __tablename__ = 'donations'
    id = db.Column(db.Integer, primary_key=True)
    food_type = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.String(50), nullable=False)
    storage = db.Column(db.String(100))
    dietary = db.Column(db.String(100))
    expiry_date = db.Column(db.String(20))
    expiry_time = db.Column(db.String(20))
    transportation = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_details = db.Column(db.JSON, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Database:
    @staticmethod
    def init_app(app):
        # Configure database URI
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)
        print("💕Successfully initiated Database")
        with app.app_context():
            db.create_all()

    @staticmethod
    def get_recent_donations(limit=5):
        return Donation.query.order_by(desc(Donation.timestamp)).limit(limit).all()

    @staticmethod
    def store_chatbot_response(question, answer):
        # This remains the same as it uses local JSON file
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

    @staticmethod
    def create_order(donor_email, receiver_email, chatbot_responses):
        donor = User.query.filter_by(email=donor_email).first()
        receiver = User.query.filter_by(email=receiver_email).first()

        if not donor or not receiver:
            raise Exception('User information not found')

        order = Order(
            donor_id=donor.id,
            receiver_id=receiver.id,
            order_details=chatbot_responses
        )
        db.session.add(order)
        db.session.commit()

        # Ensure orders directory exists
        orders_dir = "orders"
        if not os.path.exists(orders_dir):
            os.makedirs(orders_dir)

        # Save to JSON file
        filename = f"orders/order_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        order_data = {
            'donor': {
                'name': donor.name,
                'email': donor.email,
                'address': donor.address,
                'contact': donor.contact
            },
            'receiver': {
                'name': receiver.name,
                'email': receiver.email,
                'address': receiver.address,
                'contact': receiver.contact
            },
            'order_details': chatbot_responses,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(order_data, f, indent=4)
        return filename, order
    @staticmethod
    def register_user(name, email, password, contact, address):
        if User.query.filter_by(email=email).first():
            raise Exception('Email already registered')

        hashed_password = generate_password_hash(password)

        user = User(
            name=name,
            email=email,
            password=hashed_password,
            contact=contact,
            address=address
        )
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def login_user(email, password):
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            return user
        return None

    @staticmethod
    def create_donation(food_type, quantity, storage, dietary, expiry_date, expiry_time, transportation, user_email):
        user = User.query.filter_by(email=user_email).first()
        if not user:
            raise Exception('User not found')

        donation = Donation(
            food_type=food_type,
            quantity=quantity,
            storage=storage,
            dietary=dietary,
            expiry_date=expiry_date,
            expiry_time=expiry_time,
            transportation=transportation,
            user_id=user.id
        )
        db.session.add(donation)
        db.session.commit()
        return donation

    @staticmethod
    def get_all_donations():
        donation_records = (
            db.session.query(Donation, User.email.label('user_email'))
            .join(User, Donation.user_id == User.id)
            .order_by(desc(Donation.timestamp))
            .all()
        )

        donations = []
        for donation, user_email in donation_records:
            donations.append({
                'id': donation.id,
                'food_type': donation.food_type,
                'quantity': donation.quantity,
                'storage': donation.storage,
                'dietary': donation.dietary,
                'expiry_date': donation.expiry_date,
                'expiry_time': donation.expiry_time,
                'transportation': donation.transportation,
                'user_email': user_email,
            })

        return donations

    @staticmethod
    def get_user_donations(user_email):
        user = User.query.filter_by(email=user_email).first()
        if not user:
            return []
        return Donation.query.filter_by(user_id=user.id).order_by(desc(Donation.timestamp)).all()

    @staticmethod
    def get_all_users():
        users = User.query.all()
        # Convert to dict and remove password
        return [{k: v for k, v in user.__dict__.items() if k != 'password' and not k.startswith('_')} 
                for user in users]

    @staticmethod
    def send_donation_email(json_file_path, donor_email, receiver_email, order_details):
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = int(os.getenv("SMTP_PORT"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")

        try:
            # Connect to the SMTP server
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)

            # 1️⃣ Email to the donor
            donor_msg = MIMEMultipart()
            donor_msg['From'] = smtp_user
            donor_msg['To'] = donor_email
            donor_msg['Subject'] = "🎉 Thank You for Your Donation!"

            donor_body = f"""
            Hi there! 👋<br><br>
            Thanks a lot for your generous donation. Here's what you donated:<br>
            <pre>{order_details}</pre><br>
            Your donation file is saved as: <strong>{json_file_path}</strong><br><br>
            Keep spreading the kindness! 💖
            """
            donor_msg.attach(MIMEText(donor_body, 'html'))

            server.sendmail(smtp_user, donor_email, donor_msg.as_string())

            # 2️⃣ Email to the receiver
            receiver_msg = MIMEMultipart()
            receiver_msg['From'] = smtp_user
            receiver_msg['To'] = receiver_email
            receiver_msg['Subject'] = "📦 You've Received a Donation!"

            receiver_body = f"""
            Hello! 🎁<br><br>
            Great news — you've received a donation!<br>
            Here are the details:<br>
            <pre>{order_details}</pre><br>
            File reference: <strong>{json_file_path}</strong><br><br>
            Wishing you all the best! 🌟
            """
            receiver_msg.attach(MIMEText(receiver_body, 'html'))

            server.sendmail(smtp_user, receiver_email, receiver_msg.as_string())

            server.quit()
            return True, "Emails sent successfully."

        except Exception as e:
            return False, f"Failed to send emails: {e}"
        # This method remains unchanged as it doesn't interact with the database
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