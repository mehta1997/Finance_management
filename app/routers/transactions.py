from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from ..database import get_db
from ..auth import get_current_active_user
from .. import models, schemas

router = APIRouter()


@router.post("/", response_model=schemas.Transaction)
async def create_transaction(
    transaction: schemas.TransactionCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new transaction"""
    # Verify account belongs to user
    account = db.query(models.Account).filter(
        models.Account.id == transaction.account_id,
        models.Account.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Create transaction
    db_transaction = models.Transaction(
        **transaction.dict(),
        user_id=current_user.id
    )
    
    db.add(db_transaction)
    
    # Update account balance
    if transaction.transaction_type == schemas.TransactionType.income:
        account.balance += transaction.amount
    elif transaction.transaction_type == schemas.TransactionType.expense:
        account.balance -= transaction.amount
    
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction


@router.get("/", response_model=List[schemas.Transaction])
async def get_transactions(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    account_id: Optional[int] = None,
    category_id: Optional[int] = None,
    transaction_type: Optional[schemas.TransactionType] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get user's transactions with filtering options"""
    query = db.query(models.Transaction).filter(models.Transaction.user_id == current_user.id)
    
    # Apply filters
    if account_id:
        query = query.filter(models.Transaction.account_id == account_id)
    if category_id:
        query = query.filter(models.Transaction.category_id == category_id)
    if transaction_type:
        query = query.filter(models.Transaction.transaction_type == transaction_type)
    if start_date:
        query = query.filter(models.Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(models.Transaction.transaction_date <= end_date)
    
    transactions = query.order_by(models.Transaction.transaction_date.desc()).offset(skip).limit(limit).all()
    return transactions


@router.get("/{transaction_id}", response_model=schemas.Transaction)
async def get_transaction(
    transaction_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific transaction"""
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return transaction


@router.put("/{transaction_id}", response_model=schemas.Transaction)
async def update_transaction(
    transaction_id: int,
    transaction_update: schemas.TransactionUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a transaction"""
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Store old values for balance adjustment
    old_amount = transaction.amount
    old_type = transaction.transaction_type
    old_account_id = transaction.account_id
    
    # Update transaction
    for field, value in transaction_update.dict(exclude_unset=True).items():
        setattr(transaction, field, value)
    
    # Handle account balance changes
    if (transaction_update.amount is not None or 
        transaction_update.transaction_type is not None or 
        transaction_update.account_id is not None):
        
        # Revert old transaction effect
        old_account = db.query(models.Account).filter(models.Account.id == old_account_id).first()
        if old_type == schemas.TransactionType.income:
            old_account.balance -= old_amount
        elif old_type == schemas.TransactionType.expense:
            old_account.balance += old_amount
        
        # Apply new transaction effect
        new_account = db.query(models.Account).filter(models.Account.id == transaction.account_id).first()
        if transaction.transaction_type == schemas.TransactionType.income:
            new_account.balance += transaction.amount
        elif transaction.transaction_type == schemas.TransactionType.expense:
            new_account.balance -= transaction.amount
    
    db.commit()
    db.refresh(transaction)
    
    return transaction


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a transaction"""
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Revert account balance
    account = db.query(models.Account).filter(models.Account.id == transaction.account_id).first()
    if transaction.transaction_type == schemas.TransactionType.income:
        account.balance -= transaction.amount
    elif transaction.transaction_type == schemas.TransactionType.expense:
        account.balance += transaction.amount
    
    db.delete(transaction)
    db.commit()
    
    return {"message": "Transaction deleted successfully"}


@router.get("/summary/", response_model=schemas.TransactionSummary)
async def get_transaction_summary(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get transaction summary for a date range"""
    query = db.query(models.Transaction).filter(models.Transaction.user_id == current_user.id)
    
    if start_date:
        query = query.filter(models.Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(models.Transaction.transaction_date <= end_date)
    
    transactions = query.all()
    
    total_income = sum(t.amount for t in transactions if t.transaction_type == schemas.TransactionType.income)
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == schemas.TransactionType.expense)
    
    return schemas.TransactionSummary(
        total_income=total_income,
        total_expenses=total_expenses,
        net_income=total_income - total_expenses,
        transaction_count=len(transactions)
    )


@router.get("/analytics/wealth-insights")
async def get_wealth_insights(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    period_days: int = Query(30, ge=7, le=365)
):
    """Advanced wealth analytics - FinanceFlow proprietary insights"""
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=period_days)
    
    # Get transactions for the period
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.transaction_date >= cutoff_date
    ).all()
    
    if not transactions:
        return {"message": "No transactions found for analysis period"}
    
    # Calculate metrics
    total_income = sum(t.amount for t in transactions if t.transaction_type == schemas.TransactionType.income)
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == schemas.TransactionType.expense)
    
    # Category analysis
    expense_by_category = {}
    for t in transactions:
        if t.transaction_type == schemas.TransactionType.expense:
            category = db.query(models.Category).filter(models.Category.id == t.category_id).first()
            cat_name = category.name if category else "Uncategorized"
            expense_by_category[cat_name] = expense_by_category.get(cat_name, 0) + t.amount
    
    # Financial health score (0-100)
    savings_rate = (total_income - total_expenses) / total_income if total_income > 0 else 0
    diversification_score = min(len(expense_by_category) * 10, 100)  # More categories = better diversification
    consistency_score = 100 - (len(set(t.amount for t in transactions)) / len(transactions) * 100) if transactions else 0
    
    wealth_score = int((savings_rate * 40 + diversification_score * 0.3 + consistency_score * 0.3))
    
    return {
        "analysis_period": f"{period_days} days",
        "financial_health_score": max(0, min(100, wealth_score)),
        "total_income": float(total_income),
        "total_expenses": float(total_expenses),
        "net_wealth_change": float(total_income - total_expenses),
        "savings_rate_percent": round(savings_rate * 100, 2),
        "spending_distribution": {
            category: {
                "amount": float(amount),
                "percentage": round(amount / total_expenses * 100, 2) if total_expenses > 0 else 0
            }
            for category, amount in expense_by_category.items()
        },
        "insights": {
            "top_expense_category": max(expense_by_category, key=expense_by_category.get) if expense_by_category else None,
            "average_transaction": float(sum(t.amount for t in transactions) / len(transactions)),
            "transaction_frequency": len(transactions) / period_days,
            "recommendation": "Great savings rate!" if savings_rate > 0.2 else "Consider reducing expenses to improve savings."
        }
    }


@router.get("/analytics/spending-patterns")
async def analyze_spending_patterns(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """AI-powered spending pattern analysis - Nabhi's custom algorithm"""
    from datetime import datetime, timedelta
    from collections import defaultdict
    import calendar
    
    # Get last 90 days of data
    cutoff_date = datetime.utcnow() - timedelta(days=90)
    
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.transaction_date >= cutoff_date,
        models.Transaction.transaction_type == schemas.TransactionType.expense
    ).all()
    
    if not transactions:
        return {"message": "Insufficient data for pattern analysis"}
    
    # Weekly patterns
    weekly_spending = defaultdict(float)
    for t in transactions:
        weekday = calendar.day_name[t.transaction_date.weekday()]
        weekly_spending[weekday] += t.amount
    
    # Monthly patterns 
    monthly_spending = defaultdict(float)
    for t in transactions:
        month_key = t.transaction_date.strftime("%Y-%m")
        monthly_spending[month_key] += t.amount
    
    # Detect anomalies (spending 2x above average)
    avg_transaction = sum(t.amount for t in transactions) / len(transactions)
    high_spending_days = [
        {
            "date": t.transaction_date.isoformat(),
            "amount": float(t.amount),
            "description": t.description or "No description"
        }
        for t in transactions if t.amount > avg_transaction * 2
    ]
    
    return {
        "analysis_summary": "FinanceFlow Pattern Recognition Engine v2.1",
        "data_period": "Last 90 days",
        "weekly_patterns": {
            day: {
                "total_spent": float(amount),
                "avg_per_week": float(amount / 13)  # ~13 weeks in 90 days
            }
            for day, amount in weekly_spending.items()
        },
        "monthly_trends": {
            month: float(amount) for month, amount in sorted(monthly_spending.items())
        },
        "anomaly_detection": {
            "high_spending_threshold": float(avg_transaction * 2),
            "anomalous_transactions": high_spending_days[:10],  # Top 10
            "total_anomalies": len(high_spending_days)
        },
        "recommendations": [
            "Consider setting daily spending limits",
            "Review high-spending days for optimization opportunities",
            "Your spending patterns show good consistency" if len(high_spending_days) < 5 else "High variability detected in spending"
        ]
    }
