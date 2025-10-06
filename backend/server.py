from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import json
import io
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Create the main app without a prefix
app = FastAPI(title="DataPulse Analytics Platform", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

security = HTTPBearer()

# Pydantic Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: User

class Dataset(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    filename: str
    file_size: int
    file_type: str
    status: str = "processing"  # processing, completed, failed
    upload_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time: Optional[float] = None
    row_count: Optional[int] = None
    column_count: Optional[int] = None

class DatasetAnalysis(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    dataset_id: str
    summary_stats: dict
    correlations: dict
    missing_data: dict
    outliers: dict
    ai_insights: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Helper Functions
def create_jwt_token(user_data: dict) -> str:
    payload = {
        'user_id': user_data['id'],
        'email': user_data['email'],
        'exp': datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = verify_jwt_token(credentials.credentials)
    user = await db.users.find_one({"id": payload["user_id"]})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return User(**user)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def analyze_dataframe(df: pd.DataFrame) -> dict:
    """Analyze dataframe and return insights"""
    analysis = {}
    
    # Summary statistics
    summary_stats = {}
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
    
    if numeric_columns:
        summary_stats['numeric'] = df[numeric_columns].describe().to_dict()
    if categorical_columns:
        summary_stats['categorical'] = {col: df[col].value_counts().head().to_dict() for col in categorical_columns}
    
    analysis['summary_stats'] = summary_stats
    
    # Correlations (only for numeric columns)
    if len(numeric_columns) > 1:
        correlations = df[numeric_columns].corr()
        # Convert to serializable format
        analysis['correlations'] = correlations.to_dict()
    else:
        analysis['correlations'] = {}
    
    # Missing data analysis
    missing_data = {
        'total_missing': df.isnull().sum().to_dict(),
        'percentage_missing': (df.isnull().sum() / len(df) * 100).to_dict()
    }
    analysis['missing_data'] = missing_data
    
    # Outlier detection using IsolationForest
    outliers = {}
    if len(numeric_columns) >= 2:
        try:
            # Prepare data for outlier detection
            outlier_data = df[numeric_columns].dropna()
            if len(outlier_data) > 10:  # Need enough data points
                scaler = StandardScaler()
                scaled_data = scaler.fit_transform(outlier_data)
                
                isolation_forest = IsolationForest(contamination=0.1, random_state=42)
                outlier_predictions = isolation_forest.fit_predict(scaled_data)
                
                outlier_count = sum(1 for pred in outlier_predictions if pred == -1)
                outliers['total_outliers'] = outlier_count
                outliers['outlier_percentage'] = (outlier_count / len(outlier_data)) * 100
                
                # Get indices of outliers
                outlier_indices = [i for i, pred in enumerate(outlier_predictions) if pred == -1]
                outliers['outlier_rows'] = outlier_indices[:10]  # Limit to first 10
        except Exception as e:
            outliers['error'] = f"Could not perform outlier detection: {str(e)}"
    
    analysis['outliers'] = outliers
    
    return analysis

async def generate_ai_insights(analysis_data: dict, df_info: dict) -> str:
    """Generate AI insights using LLM"""
    try:
        # Get LLM key from environment
        llm_key = os.environ.get('EMERGENT_LLM_KEY')
        if not llm_key:
            return "AI insights unavailable - API key not configured"
        
        # Initialize LLM chat
        chat = LlmChat(
            api_key=llm_key,
            session_id=f"datapulse-{uuid.uuid4()}",
            system_message="You are a data analyst expert. Provide concise, actionable insights about datasets in 2-3 paragraphs."
        ).with_model("openai", "gpt-4o-mini")
        
        # Prepare analysis summary for LLM
        prompt = f"""
        Analyze this dataset and provide key insights:
        
        Dataset Info:
        - Rows: {df_info.get('row_count', 'Unknown')}
        - Columns: {df_info.get('column_count', 'Unknown')}
        
        Analysis Results:
        - Missing Data: {analysis_data.get('missing_data', {})}
        - Outliers: {analysis_data.get('outliers', {})}
        - Correlations Available: {len(analysis_data.get('correlations', {})) > 0}
        
        Please provide:
        1. Key data quality observations
        2. Notable patterns or concerns
        3. Recommendations for further analysis
        
        Keep it concise and actionable.
        """
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        return response
    except Exception as e:
        return f"AI insights generation failed: {str(e)}"

# Authentication Routes
@api_router.post("/auth/register", response_model=TokenResponse)
async def register_user(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists with this email")
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email
    )
    
    # Store user with hashed password
    user_dict = user.dict()
    user_dict['password'] = hashed_password
    
    await db.users.insert_one(user_dict)
    
    # Create JWT token
    access_token = create_jwt_token(user.dict())
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user
    )

@api_router.post("/auth/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin):
    # Find user by email
    user = await db.users.find_one({"email": login_data.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(login_data.password, user['password']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create JWT token
    user_obj = User(**user)
    access_token = create_jwt_token(user_obj.dict())
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_obj
    )

@api_router.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# Dataset Routes
@api_router.post("/datasets/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    # Validate file type
    if not file.filename.endswith(('.csv', '.json')):
        raise HTTPException(status_code=400, detail="Only CSV and JSON files are supported")
    
    # Check file size (50MB limit)
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 50MB limit")
    
    try:
        # Create dataset record
        dataset = Dataset(
            user_id=current_user.id,
            filename=file.filename,
            file_size=len(content),
            file_type=file.content_type or 'application/octet-stream'
        )
        
        start_time = datetime.now()
        
        # Process the file based on type
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        elif file.filename.endswith('.json'):
            df = pd.read_json(io.StringIO(content.decode('utf-8')))
        
        # Update dataset with processing results
        dataset.status = "completed"
        dataset.processing_time = (datetime.now() - start_time).total_seconds()
        dataset.row_count = len(df)
        dataset.column_count = len(df.columns)
        
        # Store dataset
        await db.datasets.insert_one(dataset.dict())
        
        # Perform analysis
        analysis_results = analyze_dataframe(df)
        
        # Generate AI insights
        df_info = {
            'row_count': dataset.row_count,
            'column_count': dataset.column_count
        }
        ai_insights = await generate_ai_insights(analysis_results, df_info)
        
        # Store analysis results
        analysis = DatasetAnalysis(
            dataset_id=dataset.id,
            summary_stats=analysis_results['summary_stats'],
            correlations=analysis_results['correlations'],
            missing_data=analysis_results['missing_data'],
            outliers=analysis_results['outliers'],
            ai_insights=ai_insights
        )
        
        await db.analyses.insert_one(analysis.dict())
        
        return {
            "message": "File processed successfully",
            "dataset_id": dataset.id,
            "processing_time": dataset.processing_time,
            "rows": dataset.row_count,
            "columns": dataset.column_count
        }
        
    except Exception as e:
        # Update dataset status to failed
        dataset.status = "failed"
        await db.datasets.insert_one(dataset.dict())
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

@api_router.get("/datasets")
async def get_user_datasets(current_user: User = Depends(get_current_user)):
    datasets = await db.datasets.find({"user_id": current_user.id}).to_list(100)
    return [Dataset(**dataset) for dataset in datasets]

@api_router.get("/datasets/{dataset_id}/analysis")
async def get_dataset_analysis(
    dataset_id: str,
    current_user: User = Depends(get_current_user)
):
    # Verify user owns the dataset
    dataset = await db.datasets.find_one({"id": dataset_id, "user_id": current_user.id})
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Get analysis results
    analysis = await db.analyses.find_one({"dataset_id": dataset_id})
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return {
        "dataset": Dataset(**dataset),
        "analysis": DatasetAnalysis(**analysis)
    }

@api_router.delete("/datasets/{dataset_id}")
async def delete_dataset(
    dataset_id: str,
    current_user: User = Depends(get_current_user)
):
    # Verify user owns the dataset
    dataset = await db.datasets.find_one({"id": dataset_id, "user_id": current_user.id})
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Delete dataset and analysis
    await db.datasets.delete_one({"id": dataset_id})
    await db.analyses.delete_one({"dataset_id": dataset_id})
    
    return {"message": "Dataset deleted successfully"}

# Health check
@api_router.get("/")
async def root():
    return {"message": "DataPulse Analytics API is running"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc)}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()