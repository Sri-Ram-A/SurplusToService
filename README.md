# SurplusToService

> **Connecting food donors to those in need. Fighting waste. Feeding communities.**

**SurplusToService** is a full-stack web application that connects food donors (such as restaurants or individuals) with NGOs and food receivers in real-time. It streamlines donation management, tracks inventory, and ensures food reaches people before it’s wasted — all with a clean UI and minimal effort for users.

![Home Page](home_page.png)

---

## 🚀 Key Features

* ✅ User registration & login system
* 🍱 Donation listing, tracking & status management
* 🔔 Automated email notifications for donations
* 🗂️ User profile dashboard
* 📡 PostgreSQL/Supabase backend support
* 🤖 Integrated chatbot assistant (WIP)

---

## 🛠️ Prerequisites

Ensure you have the following installed:

* Python 3.8 or higher
* `pip` (Python package manager)
* Git
* PostgreSQL (for local DB users)

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Sri-Ram-A/SurplusToService.git
cd SurplusToService
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# On Windows
.\venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🗃️ Database Configuration (PostgreSQL / Supabase)

The application supports two ways of connecting to PostgreSQL:

### 🔌 Option A: Local PostgreSQL

1. Make sure PostgreSQL is installed and running.
2. Create a new database (e.g., `surplus_db`)
3. Add this to your `.env` file:

   ```
   DATABASE_URL=postgresql://<username>:<password>@localhost/<dbname>
   ```

   Example:

   ```
   DATABASE_URL=postgresql://postgres:mysecret@localhost/surplus_db
   ```

---

### ☁️ Option B: Supabase Cloud Database

1. Go to [https://supabase.com](https://supabase.com) and create a free project.
2. Go to your project → `Database` → Click `Connect`
3. Choose **URI - Direct Connection**, and copy the full PostgreSQL URI.
4. Add it to your `.env` file like this:

   ```
   DATABASE_URL=postgresql://postgres.bpcqnsaiekuxmzwtkszv:PASSWORD@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
   ```

---

## 📧 Email Notifications Setup

Configure your Gmail for automated emails via SMTP.

1. Visit: [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Generate a 16-character App Password for your Gmail account.
3. Add the following to your `.env` file:

   ```
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-16-digit-app-password
   ```

---
## Reference Image for Setting up Supabase and SMTP
![SETUP STEPS](gmail_and_datbase_setup.jpg)
---
## 🔑 Flask Secret Key

For session security, add this to your `.env`:

```
SECRET_KEY=your_flask_secret_key
```

---

## ▶️ Running the Application

```bash
python app.py
```

The app will be available at: [http://localhost:5000](http://localhost:5000)

---

## Final .env format
```
DATABASE_URL=postgresql://postgres.qwertyuiopasdfg:[PASSWORD]@aws-0-ap-south-1.pooler.supabase.com:0000/postgres
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_gmail@gmail.com
SMTP_PASSWORD=your_16_digit_password
SECRET_KEY=your_flask_secret_key
```
---
## 🧭 Project Structure

```
SurplusToService/
├── app.py              # Main Flask app
├── database.py         # SQLAlchemy DB setup
├── .env                # Your private config
├── assets/             # Static assets (CSS, JS, images)
├── views/              # HTML templates
├── chatbot/            # Chatbot logic
└── requirements.txt    # Python dependencies
└── orders/             # (.json order entries)
```

---

## 🤝 Contributing

Want to help improve the platform?

1. Fork this repository
2. Create your feature branch:

   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. Commit and push:

   ```bash
   git commit -m "Add AmazingFeature"
   git push origin feature/AmazingFeature
   ```
4. Open a Pull Request!

---
## 📜 Contributors
- [Niranjan S Kaithota](https://github.com/NiranjanKaithota)  
- [Sreeharish TJ](https://github.com/TJSreeharish)  
- [Mohith Tp](https://GitHub/MohithTP) 
- [SriRam.A](https://github.com/Sri-Ram-A)







