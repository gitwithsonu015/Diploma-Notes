# Engineering Notes PDF Selling Website - Project Plan

## Project Overview
A full-stack website to sell engineering diploma notes (PDF) for Rs. 199 via PhonePe UPI payment.

---

## Tech Stack
- **Backend**: Python (Flask)
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Payment**: PhonePe UPI (QR Code based)

---

## Features

### 1. Student Dashboard
- Student Registration & Login
- Browse notes by branch (Computer, Civil, Mechanical, Electrical, Electronics)
- View notes categories (Notes, Syllabus, PYQs)
- Purchase notes for Rs. 199 via PhonePe UPI
- Download PDFs after successful payment
- Payment history

### 2. Owner Dashboard
- Owner login
- Add/Edit/Delete notes
- View all purchases
- View sales statistics
- Manage branches and categories

### 3. Payment System
- PhonePe UPI QR Code display
- Manual payment verification (student uploads payment screenshot)
- Owner verifies payment and activates access

---

## Database Schema

### Users Table
- id, name, email, phone, password, role (student/owner), created_at

### Notes Table
- id, title, branch, category, description, file_path, price, created_at

### Purchases Table
- id, user_id, note_id, payment_proof, status (pending/approved/rejected), created_at

---

## Project Structure
```
diploma-notes-website/
├── app.py                 # Main Flask application
├── database.db            # SQLite database
├── requirements.txt       # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css      # Styles
│   ├── js/
│   │   └── main.js        # JavaScript
│   ├── images/
│   │   └── qr-code.png    # PhonePe QR (placeholder)
│   └── notes/
│       └── (PDF files)    # Note PDFs
└── templates/
    ├── base.html          # Base template
    ├── index.html         # Home page
    ├── login.html         # Login page
    ├── register.html      # Registration page
    ├── dashboard.html     # Student dashboard
    ├── notes.html         # Notes listing
    ├── payment.html       # Payment page
    ├── owner/
    │   ├── dashboard.html # Owner dashboard
    │   ├── add_note.html  # Add note
    │   └── verify.html    # Verify payments
    └── success.html       # Success page
```

---

## Steps to Build
1. Set up Flask project structure
2. Create database models
3. Create authentication (login/register)
4. Create student dashboard
5. Create notes listing and categories
6. Implement payment flow with QR code
7. Create owner dashboard
8. Add file upload and download functionality

---

## Default Settings
- Price: Rs. 199
- UPI ID: placeholder (to be configured)
- Branches: Computer, Civil, Mechanical, Electrical, Electronics
- Categories: Notes, Syllabus, PYQs

---

## Next Steps
1. Create project files
2. Set up database
3. Implement authentication
4. Build all pages
5. Test the application
