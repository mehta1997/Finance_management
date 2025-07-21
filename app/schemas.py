from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AccountType(str, Enum):
    checking = "checking"
    savings = "savings"
    credit = "credit"
    investment = "investment"


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"
    transfer = "transfer"


class CategoryType(str, Enum):
    income = "income"
    expense = "expense"


# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Account schemas
class AccountBase(BaseModel):
    name: str
    account_type: AccountType


class AccountCreate(AccountBase):
    balance: Optional[float] = 0.0


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    account_type: Optional[AccountType] = None
    balance: Optional[float] = None


class Account(AccountBase):
    id: int
    balance: float
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Category schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    category_type: CategoryType


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int

    class Config:
        from_attributes = True


# Transaction schemas
class TransactionBase(BaseModel):
    amount: float
    description: Optional[str] = None
    transaction_date: datetime
    transaction_type: TransactionType
    account_id: int
    category_id: Optional[int] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    transaction_date: Optional[datetime] = None
    transaction_type: Optional[TransactionType] = None
    account_id: Optional[int] = None
    category_id: Optional[int] = None


class Transaction(TransactionBase):
    id: int
    user_id: int
    created_at: datetime
    account: Optional[Account] = None
    category: Optional[Category] = None

    class Config:
        from_attributes = True


# Budget schemas
class BudgetBase(BaseModel):
    name: str
    amount: float
    period: str
    category_id: int


class BudgetCreate(BudgetBase):
    pass


class Budget(BudgetBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Response schemas
class TransactionSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_income: float
    transaction_count: int


class CategorySummary(BaseModel):
    category_name: str
    total_amount: float
    transaction_count: int
