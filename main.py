import random
import smtplib
import redis
from flask import Flask, request, jsonify

# Flask app setup
app = Flask(__name__)

# Redis connection
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# SMTP configuration
SMTP_SERVER = 'smtp.gmail.com'  # Change based on your email provider
SMTP_PORT = 587
EMAIL_SENDER = 'example@gmail.com'
EMAIL_PASSWORD = 'APP_Password'

def send_email(email, otp):
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            message = f"Subject: Your OTP Code\n\nYour OTP code is {otp}"
            server.sendmail(EMAIL_SENDER, email, message)
        return True
    except smtplib.SMTPAuthenticationError:
        print("SMTP Authentication Error: Check your email/password or enable App Passwords.")
        return False
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'message': 'Email is required'}), 400
    
    otp = str(random.randint(100000, 999999))  # Generate 6-digit OTP
    if send_email(email, otp):
        redis_client.setex(email, 300, otp)  # Store OTP in Redis for 5 minutes
        return jsonify({'message': 'OTP sent successfully'}), 200
    else:
        return jsonify({'message': 'Failed to send OTP'}), 500

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    
    if not email or not otp:
        return jsonify({'message': 'Email and OTP are required'}), 400
    
    stored_otp = redis_client.get(email)
    
    if stored_otp and stored_otp == otp:
        redis_client.delete(email)  # Remove OTP after verification
        return jsonify({'message': 'OTP verified successfully'}), 200
    else:
        return jsonify({'message': 'Invalid or expired OTP'}), 400

if __name__ == '__main__':
    app.run(debug=True)
