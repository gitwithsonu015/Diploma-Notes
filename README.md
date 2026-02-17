# Diploma Notes Website

A full-stack website for selling engineering diploma notes (PDF) with PhonePe UPI payment integration.

## Features

- **Student Features:**
  - Register/Login
  - Browse notes by branch and category
  - Purchase notes for ₹199 via PhonePe UPI
  - Download PDFs after payment verification
  
- **Owner Features:**
  - Add/manage notes (PDF files)
  - View all purchases and sales statistics
  - Verify payment proofs
  - Approve/reject payments

## Tech Stack

- **Backend:** Python (Flask)
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript
- **Payment:** PhonePe UPI

## Setup Instructions

### 1. Install Python Dependencies
```
pip install -r requirements.txt
```

### 2. Run the Application
```
python app.py
```

### 3. Open in Browser
Go to: http://localhost:5000

## Default Login Credentials

### Owner Account:
- **Email:** owner@diplomanotes.com
- **Password:** owner123

### To Create Student Account:
1. Go to Register page
2. Fill in details
3. Login with credentials

## Project Structure

```
diploma-notes/
├── app.py                 # Main Flask application
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── static/
│   ├── css/style.css    # Styles
│   ├── js/main.js       # JavaScript
│   ├── images/          # Images (QR code)
│   ├── notes/           # PDF notes (upload by owner)
│   └── uploads/         # Payment proofs
└── templates/
    ├── base.html
    ├── index.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── notes.html
    ├── note_detail.html
    ├── payment.html
    ├── success.html
    └── owner/
        ├── dashboard.html
        ├── add_note.html
        └── verify.html
```

## How to Use

### For Owner:
1. Login with owner credentials
2. Go to Owner Panel
3. Click "Add New Note" to add PDF notes
4. Go to "Verify Payments" to approve student purchases
5. Add your UPI ID in the payment page (update in payment.html)

### For Students:
1. Register a new account
2. Browse notes by branch
3. Click on a note and "Buy Now"
4. Scan QR code with PhonePe or pay to UPI ID
5. Upload payment screenshot
6. Wait for owner to verify payment
7. Download PDF after verification

## Payment Setup

To update with your PhonePe details:
1. Open `templates/payment.html`
2. Find and replace "your-upi-id@upi" with your actual UPI ID
3. Optionally add your QR code image in `static/images/qr-code.png`

## Branches Included
- Computer Engineering
- Civil Engineering
- Mechanical Engineering
- Electrical Engineering
- Electronics Engineering

## Categories
- Notes
- Syllabus
- PYQs (Previous Year Questions)

## Note Price
₹199 (One-time payment per note)

---

Created for Diploma Engineering Students
