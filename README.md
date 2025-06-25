# SmartLib Manager - Web Application

A modern, web-based library management system built with Flask. This application allows you to manage books, track borrowings, generate QR codes, and maintain user accounts through an intuitive web interface.

*Note: This is the web version of SmartLib Manager. The original Tkinter version files are still available in the same directory.*

## Features

### 📚 Book Management
- Add new books with detailed information (title, author, ISBN, category, etc.)
- View all books in table or grid format
- Search and filter books by various criteria
- Generate QR codes for each book
- Track book availability status

### 👥 User Management
- User registration and authentication
- Secure login system with session management
- Default admin account for initial setup

### 📋 Borrowing System
- Issue books to students
- Track borrowed books with due dates
- Return books functionality
- Overdue book notifications
- Borrowing history and statistics

### 📊 Dashboard & Analytics
- Real-time library statistics
- Recent activity tracking
- Quick action buttons
- System status information

### 🎨 Modern UI/UX
- Responsive Bootstrap-based design
- Mobile-friendly interface
- Intuitive navigation
- Professional styling with gradients and animations

### 🔐 Security Features
- Password hashing using SHA-256
- Session-based authentication
- CSRF protection through Flask sessions
- Input validation and sanitization

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup Instructions

1. **Navigate to the project directory:**
   ```bash
   cd SMARTLIB_MANAGER
   ```

2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the web application:**
   ```bash
   python app.py
   ```

4. **Access the application:**
   Open your web browser and navigate to: `http://localhost:5000`

## Default Login Credentials

**Admin Account:**
- Username: `admin`
- Password: `admin123`

*Note: Please change the default password after first login for security.*

## Quick Start Guide

1. Start the application using `python app.py`
2. Open your browser and go to `http://localhost:5000`
3. Login with the default admin credentials
4. Start adding books and managing your library!

## Legacy Tkinter Version

The original Tkinter desktop version is still available in the same directory:
- Run `python main.py` for the desktop version
- All original features are preserved
- Database is compatible between both versions

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## Usage

### First Time Setup

1. Run the application using `python main.py`
2. Login with default credentials:
   - Username: `admin`
   - Password: `admin123`

### Adding Books

1. Click "📚 Add New Book"
2. Fill in the book details (Title is required)
3. Click "Save Book"
4. A QR code will be automatically generated in the `qr_codes` folder

### Borrowing Books

1. Click "📤 Borrow Book"
2. Enter student name
3. Select an available book from the dropdown
4. Click "Borrow Book"

### Returning Books

1. Click "📥 Return Book"
2. Enter student name
3. Select the borrowed book from the dropdown
4. Click "Return Book"

### Viewing Records

- **View All Books**: See all books with their availability status
- **View Borrowed Books**: See currently borrowed books with borrowing duration

## File Structure

```
SMARTLIB_MANAGER/
├── main.py              # Main application entry point
├── login.py             # Login system
├── books.py             # Book management functions
├── borrow_return.py     # Borrowing and returning functions
├── qr_module.py         # QR code generation utilities
├── config.py            # Application configuration
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── library.db          # SQLite database (created automatically)
└── qr_codes/           # QR code storage directory (created automatically)
```

## Database Schema

### Books Table

- `id`: Primary key (auto-increment)
- `title`: Book title (required, unique)
- `author`: Book author (optional)
- `isbn`: ISBN number (optional)
- `available`: Availability status (1 = available, 0 = borrowed)
- `date_added`: Timestamp when book was added

### Borrowed Table

- `id`: Primary key (auto-increment)
- `student_name`: Name of the student who borrowed the book
- `book_title`: Title of the borrowed book
- `borrow_date`: Timestamp when book was borrowed
- `return_date`: Timestamp when book was returned (NULL if not returned)

## Configuration

The application can be customized by modifying `config.py`:

- **Admin Credentials**: Change default username/password
- **UI Colors**: Customize the color scheme
- **Validation Rules**: Set maximum lengths for various fields
- **Default Settings**: Configure borrowing periods and limits

## Dependencies

- **tkinter**: GUI framework (included with Python)
- **sqlite3**: Database (included with Python)
- **Pillow**: Image processing for QR codes
- **qrcode**: QR code generation

## Security Notes

⚠️ **Important**: This application is designed for educational and small-scale use. For production environments:

1. Change the default admin credentials in `config.py`
2. Implement proper password hashing
3. Add user session management
4. Consider using a more robust database system
5. Implement proper logging and audit trails

## Troubleshooting

### Common Issues

1. **"No module named 'PIL'" error**

   ```bash
   pip install Pillow
   ```

2. **"No module named 'qrcode'" error**

   ```bash
   pip install qrcode
   ```

3. **Database errors**

   - Delete `library.db` file and restart the application
   - The database will be recreated automatically

4. **QR code generation fails**
   - Ensure the `qr_codes` directory has write permissions
   - Check that Pillow is properly installed

### Performance Tips

- The application creates QR codes in the `qr_codes` directory
- Regularly backup the `library.db` file
- For large libraries (1000+ books), consider database optimization

## Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For support or questions:

1. Check the troubleshooting section above
2. Review the code comments for implementation details
3. Create an issue in the project repository

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Author**: Library Management System Team
