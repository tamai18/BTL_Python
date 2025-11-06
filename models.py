from sqlalchemy import Column, Integer, String, DECIMAL, Date, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
import enum
from datetime import datetime

class CategoryType(enum.Enum):
    income = "income"
    expense = "expense"

class Currency(enum.Enum):
    VND = "VND"
    USD = "USD"

class Theme(enum.Enum):
    light = "light"
    dark = "dark"

class Language(enum.Enum):
    en = "en"
    vi = "vi"

class ChartType(enum.Enum):
    pie = "pie"
    bar = "bar"

# ---- USER ----
class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)

    incomes = relationship('Income', back_populates='user', cascade='all, delete-orphan')
    expenses = relationship('Expense', back_populates='user', cascade='all, delete-orphan')
    budget = relationship('Budget', back_populates='user', cascade='all, delete-orphan')
    settings = relationship('Settings', back_populates='user', uselist=False, cascade='all, delete-orphan')
    summaries = relationship("MonthlySummary", back_populates="user", cascade="all, delete-orphan")


#---- CATEGORIES ----
class Category(Base):
    __tablename__ = 'categories'
    category_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    type = Column(Enum(CategoryType), nullable=False)
    description = Column(Text)

    incomes = relationship("Income", back_populates='category')
    expenses = relationship("Expense", back_populates='category')
    budget = relationship("Budget", back_populates='category')

#---- INCOME ----
class Income(Base):
    __tablename__ = 'incomes'
    income_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    category_id = Column(Integer, ForeignKey('categories.category_id'))
    amount = Column(DECIMAL(12, 2), nullable=False)
    date = Column(Date, nullable=False)
    note = Column(Text)

    user = relationship('User', back_populates='incomes')
    category = relationship('Category', back_populates='incomes')


# ---- EXPENSE ----
class Expense(Base):
    __tablename__ = 'expenses'
    expense_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    category_id = Column(Integer, ForeignKey('categories.category_id'))
    amount = Column(DECIMAL(12, 2), nullable=False)
    date = Column(Date, nullable=False)
    note = Column(Text)

    user = relationship('User', back_populates='expenses')
    category = relationship('Category', back_populates='expenses')

#---- BUDGETS ----
class Budget(Base):
    __tablename__ = 'budget'
    budget_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    category_id = Column(Integer, ForeignKey('categories.category_id'))
    amount = Column(DECIMAL(12, 2), nullable=False)
    month = Column(String(20), nullable=False)

    user = relationship('User', back_populates='budget')
    category = relationship('Category', back_populates='budget')

#---- SETTINGS ----
class Settings(Base):
    __tablename__ = 'settings'
    setting_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), unique=True)
    currency = Column(Enum(Currency), default=Currency.VND, nullable=False)
    saving_ratio = Column(DECIMAL(5, 2), default=0.20)  # Tỷ lệ tiết kiệm mặc định 20%
    language = Column(Enum(Language), default=Language.vi)
    theme = Column(Enum(Theme), default=Theme.light)
    chart_type = Column(Enum(ChartType), default=ChartType.pie)

    user = relationship('User', back_populates='settings')

#---- MONTHLY SUMMARY (Thống kê tổng hợp tháng) ----
class MonthlySummary(Base):
    __tablename__ = 'monthly_summary'
    summary_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    month = Column(String(20), nullable=False)
    total_income = Column(DECIMAL(12, 2), default=0, nullable=False)
    total_expense = Column(DECIMAL(12, 2), default=0, nullable=False)
    balance = Column(DECIMAL(12, 2), default=0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now())

    user = relationship('User', back_populates='summaries')

