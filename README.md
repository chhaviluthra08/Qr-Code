# QR Code App

A simple web application to generate, save, and view QR codes, with user authentication and history, built using Streamlit and SQLite.

## Features
- User registration and login
- Passwords securely hashed
- Generate QR codes from text or links
- Save generated QR codes to your personal history
- View your QR code history (admin can view all users' history)
- Admin mode for user management and QR deletion

## Requirements
- Python 3.8+
- See `requirements.txt` for Python dependencies

## Installation
1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd QrCode
   ```
2. **(Optional) Create a virtual environment**
   ```bash
   python3 -m venv env
   source env/bin/activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. **Run the app**
   ```bash
   streamlit run app.py
   ```
2. **Open the app**
   - Go to the local URL provided by Streamlit (usually http://localhost:8501)

## Admin Access
- To view all users and QR codes, log in as:
  - **Username:** `admin`
  - **Password:** `_root_101_`

## File Structure
- `app.py` - Main application code
- `QrApp.db` - SQLite database (auto-created)
- `requirements.txt` - Python dependencies

## License
This project is for educational/demo purposes.
