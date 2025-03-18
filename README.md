
# OTP Verification System

A secure OTP (One-Time Password) verification system built using:

- **Python (Flask)** - Backend API framework
- **Redis** - In-memory database for OTP storage
- **SMTP Protocol** - Email delivery for OTP codes


## Setup Instructions

### Prerequisites

- Python 3.7+
- Redis server
- Email account for sending OTPs

### Installation

1. Clone the repository:
```bash
git clone https://github.com/dharshan-kumarj/OTP_verification_using_py.git
cd OTP_verification_using_py
```

2. Install required packages:
```bash
pip install flask redis python-dotenv
```

3. Create a `.env` file with your configuration:
```bash
# Create and edit .env file
touch .env
nano .env  # Or use any text editor
```

4. Run the application:
```bash
python app.py
```

## Environment Variables

Create a `.env` file in the project root with the following variables:

```
# Email Configuration
EMAIL_SENDER=your-email@example.com
EMAIL_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

**Note for Gmail users:** You'll need to use an "App Password" instead of your regular password. Enable 2FA on your Google account and generate an App Password from your Google Account settings.

## API Documentation

### Send OTP

Sends a 6-digit OTP code to the provided email address.

**Endpoint:** `POST /send-otp`

**Request Body:**
```json
{
  "email": "recipient@example.com"
}
```

**Success Response (200 OK):**
```json
{
  "message": "OTP sent successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
  "message": "Email is required"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "message": "Failed to send OTP"
}
```

### Verify OTP

Verifies the OTP code sent to the email address.

**Endpoint:** `POST /verify-otp`

**Request Body:**
```json
{
  "email": "recipient@example.com",
  "otp": "123456"
}
```

**Success Response (200 OK):**
```json
{
  "message": "OTP verified successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
  "message": "Email and OTP are required"
}
```

**Error Response (400 Bad Request) - Invalid OTP:**
```json
{
  "message": "Invalid or expired OTP"
}
```

## Testing with Postman

1. **Send OTP Request:**
   - Create a POST request to `http://localhost:5000/send-otp`
   - Set body to raw JSON: `{"email": "your-email@example.com"}`
   - Send request and check your email for the OTP code

2. **Verify OTP Request:**
   - Create a POST request to `http://localhost:5000/verify-otp`
   - Set body to raw JSON: `{"email": "your-email@example.com", "otp": "123456"}`
   - Replace "123456" with the actual OTP received in your email
   - Send request to verify the OTP

## Troubleshooting

1. **Email Not Received**
   - Check spam/junk folder
   - Verify EMAIL_SENDER and EMAIL_PASSWORD in .env file
   - For Gmail, ensure you're using an App Password

2. **Redis Connection Issues**
   - Ensure Redis server is running: `redis-cli ping` should return "PONG"
   - Check REDIS_HOST and REDIS_PORT settings

3. **Authentication Errors**
   - For Gmail, regular passwords won't work. Use App Passwords instead
   - Verify you've enabled "Less secure app access" or created an App Password

## Security Considerations

- OTPs expire after 5 minutes
- OTPs are deleted from Redis after successful verification
- Use HTTPS in production for secure data transmission
- Consider rate limiting to prevent brute force attacks
