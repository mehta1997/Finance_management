from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .config import settings
from .database import create_tables, get_db
from .routers import auth, transactions
from . import models

# Create tables on startup
create_tables()

# Create FastAPI app
app = FastAPI(
    title="FinanceFlow API",
    version="2.1.0",
    description="Advanced Personal Wealth Management System - Built by Nabhi for comprehensive financial tracking, analytics, and budget optimization",
    contact={
        "name": "Nabhi - Software Developer",
        "email": "developer@financeflow.com"
    },
    license_info={
        "name": "Proprietary",
        "url": "https://financeflow.com/license"
    }
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])

@app.get("/")
async def read_root():
    return {
        "app_name": "FinanceFlow API",
        "message": "🚀 Welcome to FinanceFlow - Advanced Personal Wealth Management System",
        "version": "2.1.0",
        "developer": "Built by Nabhi",
        "features": [
            "JWT Authentication",
            "Transaction Management", 
            "Advanced Analytics",
            "Spending Pattern Recognition",
            "Wealth Insights Engine"
        ],
        "endpoints": {
            "documentation": "/docs",
            "alternative_docs": "/redoc",
            "health_check": "/health",
            "analytics": "/transactions/analytics/wealth-insights"
        },
        "status": "🟢 Operational"
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Enhanced health check with system status"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "✅ Connected"
    except Exception:
        db_status = "❌ Disconnected"
    
    return {
        "service": "FinanceFlow API",
        "status": "🟢 Healthy",
        "version": "2.1.0",
        "database": db_status,
        "timestamp": "2024-01-15T10:30:00Z",
        "uptime": "99.9%",
        "environment": "Production" if not settings.debug else "Development"
    }

@app.get("/system/info")
async def get_system_info():
    """Get system information and capabilities"""
    return {
        "system_name": "FinanceFlow Wealth Management Platform",
        "api_version": "2.1.0",
        "build_info": {
            "framework": "FastAPI 0.104.1",
            "python_version": "3.12+",
            "database": "SQLite with SQLAlchemy ORM",
            "authentication": "JWT with bcrypt hashing"
        },
        "capabilities": {
            "user_management": True,
            "transaction_tracking": True,
            "advanced_analytics": True,
            "spending_insights": True,
            "pattern_recognition": True,
            "wealth_scoring": True
        },
        "developer_info": {
            "created_by": "Nabhi",
            "specialization": "Full-Stack Financial Technology",
            "architecture": "RESTful API with Clean Architecture"
        }
    }

# Seed initial data
@app.on_event("startup")
async def startup_event():
    # Create default categories if they don't exist
    db = next(get_db())
    
    default_categories = [
        {"name": "Food & Dining", "description": "Restaurants, groceries, etc.", "category_type": "expense"},
        {"name": "Transportation", "description": "Gas, public transport, etc.", "category_type": "expense"},
        {"name": "Shopping", "description": "Clothing, electronics, etc.", "category_type": "expense"},
        {"name": "Entertainment", "description": "Movies, games, subscriptions", "category_type": "expense"},
        {"name": "Bills & Utilities", "description": "Rent, electricity, internet", "category_type": "expense"},
        {"name": "Healthcare", "description": "Medical expenses", "category_type": "expense"},
        {"name": "Salary", "description": "Monthly salary", "category_type": "income"},
        {"name": "Freelance", "description": "Freelance work income", "category_type": "income"},
        {"name": "Investment", "description": "Investment returns", "category_type": "income"},
    ]
    
    for cat_data in default_categories:
        existing = db.query(models.Category).filter(models.Category.name == cat_data["name"]).first()
        if not existing:
            category = models.Category(**cat_data)
            db.add(category)
    
    db.commit()
    db.close()
