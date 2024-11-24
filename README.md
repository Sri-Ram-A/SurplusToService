# SurplusToService

A web application that connects food donors with those in need, helping to reduce food waste and serve the community.

![Home Page](home_page.png)

## Features

- User registration and authentication
- Food donation management
- Real-time donation tracking
- Email notifications
- User profile management
- Firebase integration for data storage

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package manager)
- Git

## Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/SurplusToService.git
   cd SurplusToService
   ```

2. **Create a virtual environment** (Optional but recommended)
   ```bash
   python -m venv venv
   
   # On Windows
   .\venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Firebase Setup**
   - Create a new project in [Firebase Console](https://console.firebase.google.com/)
   - Generate a new private key from Project Settings > Service Accounts
   - Save the JSON file as `surplustoservice-6a995-firebase-adminsdk-gssz6-06c67d0a0c.json` in the project root

5. **Configure Email Settings**
   - Open `app.py`
   - Update the email configuration:
     ```python
     SMTP_USER = "your-email@gmail.com"
     SMTP_PASSWORD = "your-app-specific-password"
     ```

6. **Run the application**
   ```bash
   python app.py
   ```
   The application will be available at `http://localhost:5000`

## Project Structure

```
SurplusToService/
├── app.py              # Main application file
├── assets/            # Static files (CSS, JS, images)
├── views/             # HTML templates
└── requirements.txt   # Project dependencies
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Based on the Restaurantly template by BootstrapMade.com. See [LICENSE](https://bootstrapmade.com/license/) for more information.

## Acknowledgments

- [Bootstrap](https://getbootstrap.com)
- [Firebase](https://firebase.google.com)
- [Flask](https://flask.palletsprojects.com)
- [BootstrapMade](https://bootstrapmade.com)
