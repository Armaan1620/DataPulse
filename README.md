Here are the step-by-step instructions to run the DataPulse analytics platform on your local machine:

📋 Prerequisites
Make sure you have these installed:

Python 3.11+
Node.js 18+
Yarn (npm install -g yarn)
MongoDB 5.0+
🛠️ Setup Instructions

1. Project Setup

# Create project directory

mkdir datapulse-platform
cd datapulse-platform

# Create the basic structure

mkdir backend frontend 2. Backend Setup

# Navigate to backend directory

cd backend

# Create virtual environment (recommended)

python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

# Install dependencies

pip install fastapi uvicorn motor python-dotenv pandas numpy scikit-learn PyJWT bcrypt python-multipart emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/

# Create .env file

touch .env
Edit backend/.env:

MONGO_URL=mongodb://localhost:27017
DB_NAME=datapulse_db
CORS_ORIGINS=\*
JWT_SECRET=datapulse-jwt-secret-key-change-in-production
EMERGENT_LLM_KEY=sk-emergent-0802d4aF7651cE5Bb9
Copy the server.py file from the project (you can find the complete code in the chat history above)

3. Frontend Setup

# Navigate to frontend directory

cd ../frontend

# Initialize React app with Vite

yarn create react-app . --template typescript

# Or if using create-react-app: npx create-react-app .

# Install additional dependencies

yarn add axios react-router-dom

# Install Tailwind CSS

yarn add -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Create .env file

touch .env
Edit frontend/.env:

REACT_APP_BACKEND_URL=http://localhost:8001
Copy the src/App.js and src/App.css files from the project

4. MongoDB Setup

# Install MongoDB locally (Ubuntu/Debian)

sudo apt update
sudo apt install mongodb

# Start MongoDB service

sudo systemctl start mongodb
sudo systemctl enable mongodb

# Or using Docker

docker run -d -p 27017:27017 --name mongodb mongo:5.0
🚀 Running the Application
Method 1: Manual Start (Development)
Terminal 1 - Start Backend:

cd backend
source venv/bin/activate # Activate virtual environment
uvicorn server:app --reload --host 0.0.0.0 --port 8001
Terminal 2 - Start Frontend:

cd frontend
yarn start
Method 2: Using Supervisor (Production-like)
Install Supervisor:

sudo apt install supervisor # Ubuntu/Debian

# or

brew install supervisor # macOS
Create supervisor config files:

/etc/supervisor/conf.d/backend.conf:

[program:backend]
command=/path/to/your/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001
directory=/path/to/your/backend
autostart=true
autorestart=true
user=your-username
/etc/supervisor/conf.d/frontend.conf:

[program:frontend]
command=yarn start
directory=/path/to/your/frontend
autostart=true
autorestart=true
user=your-username
environment=PORT=3000
Start services:

sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start backend frontend
🌐 Access the Application
Once both services are running:

Frontend Dashboard: http://localhost:3000
Backend API: http://localhost:8001
API Documentation: http://localhost:8001/docs
🧪 Test the Platform

1. Create Account
   Go to http://localhost:3000
   Click "Sign up"
   Enter: username, email, password
   Login with your credentials
2. Upload Sample Data
   Create a test CSV file (sample_data.csv):

name,age,salary,department,experience,performance_score
John Doe,28,65000,Engineering,3,8.5
Jane Smith,32,75000,Marketing,5,9.2
Bob Johnson,45,95000,Engineering,15,7.8
Alice Brown,29,68000,Sales,4,8.9
Charlie Wilson,35,82000,Marketing,7,9.1
Or a test JSON file (sample_data.json):

[
{"name": "John Doe", "age": 28, "salary": 65000, "department": "Engineering", "experience": 3, "performance_score": 8.5},
{"name": "Jane Smith", "age": 32, "salary": 75000, "department": "Marketing", "experience": 5, "performance_score": 9.2},
{"name": "Bob Johnson", "age": 45, "salary": 95000, "department": "Engineering", "experience": 15, "performance_score": 7.8}
] 3. Upload and Analyze
Drag & drop your sample file
Wait for processing to complete
Click on the dataset to view analysis
See AI insights, correlations, and statistics
🔧 Troubleshooting
Common Issues:
Backend won't start:

# Check MongoDB is running

sudo systemctl status mongodb

# Check dependencies

pip list | grep -E "(fastapi|pandas|scikit-learn)"

# Check logs

tail -f /var/log/supervisor/backend.\*.log
Frontend won't start:

# Clear cache

yarn cache clean

# Reinstall dependencies

rm -rf node_modules package-lock.json yarn.lock
yarn install
Database connection issues:

# Test MongoDB connection

mongosh mongodb://localhost:27017

# Check environment variables

cat backend/.env
CORS issues:

Ensure CORS_ORIGINS=\* in backend/.env
Check that frontend is accessing http://localhost:8001
📦 Project Structure
datapulse-platform/
├── backend/
│ ├── server.py # FastAPI application
│ ├── requirements.txt # Python dependencies
│ └── .env # Backend configuration
├── frontend/
│ ├── src/
│ │ ├── App.js # React application
│ │ └── App.css # Styles
│ ├── package.json # Node dependencies
│ └── .env # Frontend configuration
└── README.md # Documentation
🎯 What You Should See
Login Page - Clean authentication interface
Dashboard - File upload area and dataset list
Analysis View - Comprehensive data insights including:
AI-generated insights (powered by GPT)
Summary statistics
Correlation matrix
Missing data analysis
Outlier detection results
The platform should successfully process your CSV/JSON files and provide intelligent analysis with AI-powered insights!
