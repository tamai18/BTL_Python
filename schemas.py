from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import date
from enum import Enum
from typing import Optional

class CategoryType(str, Enum):
    income = "income"
    expense = "expense"

class Currency(str, Enum):
    VND = "VND"
    USD = "USD"

class Theme(str, Enum):
    light = "light"
    dark = "dark"

class Language(str, Enum):
    en = "en"
    vi = "vi"

class ChartType(str, Enum):
    pie = "pie"
    bar = "bar"

#---- USER ----
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6,max_length=72)
    confirm_password: str = Field(..., min_length=6,max_length=72)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserLogout(BaseModel):
    message: str

class UserResponse(UserBase):
    user_id: int
    model_config = ConfigDict(from_attributes=True)

#---- CATEGORIES ----
class CategoryBase(BaseModel):
    name: str
    type: CategoryType
    description: Optional[str] = None

class CategoryResponse(CategoryBase):
    category_id: int
    model_config = ConfigDict(from_attributes=True)

#---- INCOME ----
class IncomeBase(BaseModel):
    amount: float
    date: date
    note: Optional[str] = None

class IncomeCreate(IncomeBase):
    category_name: str

class IncomeUpdate(IncomeBase):
    category_name: str

#---- EXPENSE ----
class ExpenseBase(BaseModel):
    amount: float
    date: date
    note: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    category_name: str

class ExpenseUpdate(ExpenseBase):
    category_name: str

#---- BUDGET ----
class BudgetBase(BaseModel):
    amount: float
    month: str
    category_id: int

class BudgetCreate(BudgetBase):
    category_id: int

#---- SETTINGS ----
class SettingsBase(BaseModel):
    currency: Currency = Currency.VND
    theme: Theme = Theme.light
    language: Language = Language.vi
    chart_type: ChartType = ChartType.pie

class SettingsCreate(SettingsBase):
    user_id: int

class SettingsUpdate(SettingsBase):
    pass

class SettingsResponse(SettingsBase):
    settings_id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)

#---- MONTHLY SUMMARY ----
class MonthlySummaryBase(BaseModel):
    month: str
    total_income: float = 0
    total_expense: float = 0
    balance: float = 0

class MonthlySummaryResponse(MonthlySummaryBase):
    summary_id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)

