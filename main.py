import random
import smtplib
import redis
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Flask app setup
app = Flask(__name__)

# Get configuration from environment variables
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_DB = int(os.environ.get('REDIS_DB', 0))
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')  # Get Redis password

SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
EMAIL_SENDER = os.environ.get('EMAIL_SENDER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

# Improved Redis connection with error handling
try:
    # Include password in Redis connection
    redis_client = redis.StrictRedis(
        host=REDIS_HOST, 
        port=REDIS_PORT, 
        db=REDIS_DB,
        password=REDIS_PASSWORD,  # Add password parameter
        decode_responses=True,
        socket_timeout=5,  # Add timeout to avoid hanging
        socket_connect_timeout=5
    )
    # Test connection
    redis_client.ping()
    print(f"Successfully connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
except Exception as e:
    print(f"Redis connection error: {e}")
    # You could exit the application here or implement a fallback mechanism

def send_email(email, otp):
    try:
        # Validate email credentials are available
        if not EMAIL_SENDER or not EMAIL_PASSWORD:
            print("Missing email credentials in environment variables")
            return False
            
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
    try:
        if send_email(email, otp):
            redis_client.setex(email, 300, otp)  # Store OTP in Redis for 5 minutes
            return jsonify({'message': 'OTP sent successfully'}), 200
        else:
            return jsonify({'message': 'Failed to send OTP email'}), 500
    except redis.RedisError as e:
        print(f"Redis error in send_otp: {e}")
        return jsonify({'message': 'OTP service temporarily unavailable'}), 503
    except Exception as e:
        print(f"Unexpected error in send_otp: {e}")
        return jsonify({'message': 'An unexpected error occurred'}), 500

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    
    if not email or not otp:
        return jsonify({'message': 'Email and OTP are required'}), 400
    
    try:
        stored_otp = redis_client.get(email)
        
        if stored_otp and stored_otp == otp:
            redis_client.delete(email)  # Remove OTP after verification
            return jsonify({'message': 'OTP verified successfully'}), 200
        else:
            return jsonify({'message': 'Invalid or expired OTP'}), 400
    except redis.RedisError as e:
        print(f"Redis error in verify_otp: {e}")
        return jsonify({'message': 'OTP verification service temporarily unavailable'}), 503
    except Exception as e:
        print(f"Unexpected error in verify_otp: {e}")
        return jsonify({'message': 'An unexpected error occurred'}), 500

# Add a simple health check endpoint
@app.route('/', methods=['GET'])
def health_check():
    try:
        # Check Redis connection as part of health check
        redis_client.ping()
        return jsonify({
            'status': 'healthy', 
            'message': 'OTP service is running',
            'redis_connected': True
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'degraded', 
            'message': 'OTP service is running but Redis is not connected',
            'redis_connected': False,
            'error': str(e)
        }), 200

# Add Redis connection test endpoint
@app.route('/test-redis', methods=['GET'])
def test_redis():
    try:
        # Set a test value
        test_key = 'test_connection'
        test_value = f'working_{random.randint(1000, 9999)}'
        
        # Try operations
        redis_client.setex(test_key, 60, test_value)
        retrieved = redis_client.get(test_key)
        
        return jsonify({
            'status': 'success',
            'message': 'Redis connection is working',
            'test_value': test_value,
            'retrieved_value': retrieved,
            'host': REDIS_HOST,
            'port': REDIS_PORT
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get('PORT', 5000))
    
    # Important: bind to 0.0.0.0 instead of default 127.0.0.1
    app.run(host='0.0.0.0', port=port, debug=False)
