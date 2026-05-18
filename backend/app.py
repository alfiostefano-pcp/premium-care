"""
FastAPI backend for Premium Care Financial Agent
Handles multi-user authentication, file uploads, and real-time analysis
"""

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import os
import shutil
from typing import List, Optional
import asyncio

from backend.config import Config
from backend.database import Base, User, BankStatement, Transaction, FinancialAnalysis, Recommendation
from backend.pdf_processor import PDFProcessor
from backend.analyzer import FinancialAnalyzer
from backend.llm_agent import FinancialAdvisor
from pydantic import BaseModel
import jwt
from passlib.context import CryptContext

# ============================================================================
# PYDANTIC MODELS (Request/Response)
# ============================================================================

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

class TransactionResponse(BaseModel):
    id: int
    date: datetime
    amount: float
    description: str
    category: str
    merchant: str
    is_recurring: bool

class AnalysisResponse(BaseModel):
    summary: dict
    spending_by_category: dict
    recurring_transactions: dict
    anomalies: List[dict]
    merchant_analysis: dict

class RecommendationResponse(BaseModel):
    title: str
    description: str
    category: str
    priority: str
    potential_savings: float
    action_steps: List[str]

# ============================================================================
# SECURITY SETUP
# ============================================================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    
    to_encode = {"sub": str(user_id), "exp": expire}
    encoded_jwt = jwt.encode(to_encode, Config.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str) -> int:
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return int(user_id)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ============================================================================
# DATABASE SETUP
# ============================================================================

DATABASE_URL = f"sqlite:///{Config.DATABASE_PATH}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# FASTAPI APP SETUP
# ============================================================================

app = FastAPI(
    title="Premium Care - Financial Analysis Agent",
    description="Multi-user financial analysis and optimization platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/auth/register", response_model=UserResponse)
def register(user: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = hash_password(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        created_at=new_user.created_at
    )

@app.post("/auth/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(user.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }

# ============================================================================
# FILE UPLOAD ENDPOINTS
# ============================================================================

@app.post("/upload/statement")
async def upload_statement(
    file: UploadFile = File(...),
    token: str = None,
    db: Session = Depends(get_db)
):
    """Upload and process a bank statement PDF"""
    
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    user_id = verify_token(token)
    
    # Validate file
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Save file
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(Config.UPLOAD_FOLDER, file.filename)
        
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Process PDF
        processor = PDFProcessor()
        transactions = processor.extract_transactions(file_path)
        
        if not transactions:
            raise HTTPException(status_code=400, detail="No transactions found in PDF")
        
        # Save to database
        statement = BankStatement(
            user_id=user_id,
            filename=file.filename,
            transaction_count=len(transactions),
            total_amount=sum(t['amount'] for t in transactions)
        )
        db.add(statement)
        db.commit()
        db.refresh(statement)
        
        # Save transactions
        for tx in transactions:
            transaction = Transaction(
                statement_id=statement.id,
                date=tx['date'],
                amount=tx['amount'],
                description=tx['description'],
                category=tx.get('category', 'Uncategorized'),
                merchant=tx.get('merchant', 'Unknown')
            )
            db.add(transaction)
        
        db.commit()
        
        return {
            "statement_id": statement.id,
            "filename": file.filename,
            "transaction_count": len(transactions),
            "message": "Statement processed successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

# ============================================================================
# ANALYSIS ENDPOINTS
# ============================================================================

@app.get("/analysis/{statement_id}", response_model=AnalysisResponse)
async def analyze_statement(
    statement_id: int,
    token: str = None,
    db: Session = Depends(get_db)
):
    """Get analysis for a bank statement"""
    
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    user_id = verify_token(token)
    
    # Get statement
    statement = db.query(BankStatement).filter(
        BankStatement.id == statement_id,
        BankStatement.user_id == user_id
    ).first()
    
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")
    
    # Get transactions
    transactions = db.query(Transaction).filter(
        Transaction.statement_id == statement_id
    ).all()
    
    # Perform analysis
    analyzer = FinancialAnalyzer()
    summary = analyzer.calculate_summary_stats([
        {
            'date': tx.date,
            'amount': tx.amount,
            'description': tx.description,
            'category': tx.category
        } for tx in transactions
    ])
    
    spending = analyzer.get_spending_by_category([
        {
            'date': tx.date,
            'amount': tx.amount,
            'description': tx.description,
            'category': tx.category
        } for tx in transactions
    ])
    
    recurring = analyzer.detect_recurring_transactions([
        {
            'date': tx.date,
            'amount': tx.amount,
            'description': tx.description,
            'category': tx.category
        } for tx in transactions
    ])
    
    anomalies = analyzer.detect_anomalies([
        {
            'date': tx.date,
            'amount': tx.amount,
            'description': tx.description,
            'category': tx.category
        } for tx in transactions
    ])
    
    merchants = analyzer.get_merchant_analysis([
        {
            'date': tx.date,
            'amount': tx.amount,
            'description': tx.description,
            'merchant': tx.merchant
        } for tx in transactions
    ])
    
    # Save analysis
    analysis = FinancialAnalysis(
        statement_id=statement_id,
        summary_stats=str(summary),
        spending_by_category=str(spending),
        anomalies_detected=len(anomalies)
    )
    db.add(analysis)
    db.commit()
    
    return AnalysisResponse(
        summary=summary,
        spending_by_category=spending,
        recurring_transactions=recurring,
        anomalies=[
            {
                'date': str(a['date']),
                'amount': a['amount'],
                'description': a['description'],
                'z_score': a.get('z_score', 0)
            } for a in anomalies
        ],
        merchant_analysis=merchants
    )

@app.get("/recommendations/{statement_id}", response_model=List[RecommendationResponse])
async def get_recommendations(
    statement_id: int,
    token: str = None,
    db: Session = Depends(get_db)
):
    """Get AI recommendations for a statement"""
    
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    user_id = verify_token(token)
    
    # Get statement
    statement = db.query(BankStatement).filter(
        BankStatement.id == statement_id,
        BankStatement.user_id == user_id
    ).first()
    
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")
    
    # Get transactions
    transactions = db.query(Transaction).filter(
        Transaction.statement_id == statement_id
    ).all()
    
    tx_data = [
        {
            'date': tx.date,
            'amount': tx.amount,
            'description': tx.description,
            'category': tx.category
        } for tx in transactions
    ]
    
    # Generate recommendations
    advisor = FinancialAdvisor()
    recommendations = advisor.generate_recommendations(tx_data)
    
    # Save recommendations
    for rec in recommendations:
        recommendation = Recommendation(
            statement_id=statement_id,
            title=rec.get('title', ''),
            description=rec.get('description', ''),
            category=rec.get('category', ''),
            priority=rec.get('priority', 'medium'),
            potential_savings=rec.get('potential_savings', 0)
        )
        db.add(recommendation)
    
    db.commit()
    
    return [
        RecommendationResponse(
            title=rec.get('title', ''),
            description=rec.get('description', ''),
            category=rec.get('category', ''),
            priority=rec.get('priority', 'medium'),
            potential_savings=rec.get('potential_savings', 0),
            action_steps=rec.get('action_steps', [])
        ) for rec in recommendations
    ]

# ============================================================================
# USER ENDPOINTS
# ============================================================================

@app.get("/user/profile", response_model=UserResponse)
async def get_profile(token: str = None, db: Session = Depends(get_db)):
    """Get current user profile"""
    
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    user_id = verify_token(token)
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at
    )

@app.get("/user/statements")
async def get_statements(token: str = None, db: Session = Depends(get_db)):
    """Get all statements for current user"""
    
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    user_id = verify_token(token)
    statements = db.query(BankStatement).filter(BankStatement.user_id == user_id).all()
    
    return [
        {
            "id": s.id,
            "filename": s.filename,
            "uploaded_at": s.uploaded_at,
            "transaction_count": s.transaction_count,
            "total_amount": s.total_amount
        } for s in statements
    ]

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# ============================================================================
# STARTUP
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.API_HOST, port=Config.API_PORT)
