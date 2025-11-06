from sqlalchemy.orm import Session
from sqlalchemy import func
from models import User, Income, Expense, Budget, CategoryType, Category, Settings, MonthlySummary, Currency, Theme, Language, ChartType
from auth import get_password_hash, verify_password, create_access_token
from datetime import date, datetime
import calendar

from routers import expense


#---- USER ----
# Lọc người dùng theo tên
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# Lọc người dùng theo email
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# Lưu(tạo) người dùng trg csdl
def create_user(db: Session, username: str, email: str, password: str, confirm_password: str):
    print(">>> DEBUG password type:", type(password))
    print(">>> DEBUG password value:", repr(password))

    if not username or not email or not password:
        return {"error": "Username, email và password là bắt buộc."}

    if len(password) < 6:
        return {"error": "Mật khẩu phải có ít nhất 6 ký tự."}
    for ch in password:
        if not (ch.islower() or ch.isdigit()):
            return {"error": "Mật khẩu chỉ được chứa chữ thường và số, không có ký tự đặc biệt hoặc chữ hoa."}

    if password != confirm_password:
        return {"error": "Mật khẩu xác nhận không khớp."}
    if get_user_by_username(db, username):
        return {"error": "Username đã tồn tại."}
    if get_user_by_email(db, email):
        return {"error": "Email đã được đăng ký."}

    new_user = User(username=username, email=email, password_hash=get_password_hash(password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Kiểm tra phiên đăng nhập của người dùng
def verify_login(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None

    # Đưa ra token
    token_data = {"user_id": user.user_id}
    access_token = create_access_token(data=token_data)
    return {
        "user": user,
        "access_token": access_token
    }

# Đăng xuất
def logout_user(db: Session, user_id: int):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        return {"error": "🚫 Không tìm thấy người dùng!"}
    return {"message": f"👋 Người dùng {user.username} đã đăng xuất thành công!"}

# Cập nhật thông tin người dùng.
"""
def update_user(db: Session, user_id: int, username: str = None, email: str = None, password: str = None):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "Không tìm thấy người dùng."}
    if username:
        user.username = username
    if email:
        # kiểm tra email mới có bị trùng hay không
        existing = db.query(User).filter(User.email == email, User.id != user_id).first()
        if existing:
            return {"error": "Email này đã được sử dụng."}
        user.email = email
    if password:
        user.password_hash = get_password_hash(password)
    db.commit()
    db.refresh(user)
    return {"message": "Cập nhật thông tin thành công!", "user": {"id": user.id, "username": user.username, "email": user.email}}
"""

# Xóa tài khoản
def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        return None
    db.delete(user)
    db.commit()
    return user

#--------------------------
#---- INCOME ----
# Lưu(tạo) khoản thu trg csdl
def create_income(db: Session, user_id: int, category_name: str,  amount: float, date_: date, note: str = None):
    if not category_name or amount <=0:
        return {"error": "❌ Tên danh mục và số tiền phải hợp lệ."}
    category = db.query(Category).filter(
        func.lower(Category.name) == category_name.lower(),
        Category.type == CategoryType.income
    ).first()          # lọc xem để ktra danh mục đã tồn tại chưa

    # Nếu chưa thì tạo mới
    if not category:
        category = Category(
            name=category_name,
            type=CategoryType.income,
            description="Danh mục tự thêm",
        )
        db.add(category)
        db.commit()
        db.refresh(category)
    existing_income = db.query(Income).filter(
        Income.user_id == user_id,
        Income.category_id == category.category_id,
        Income.date == date_
    ).first()

    # Ktra xem khoản thu này đã đc tạo trc đó chưa
    if existing_income:
        return {
            "error": "⚠️ Đã có khoản thu trong cùng ngày và danh mục này! Nếu bạn muốn sửa, vui lòng vào mục cập nhật."}

    # Nếu chưa thì tạo mới
    income = Income(
        user_id=user_id,
        category_id=category.category_id,
        amount=amount,
        date = date_,
        note=note
    )
    db.add(income)
    db.commit()
    db.refresh(income)
    return {
        "message": "✅ Đã thêm khoản thu thành công!",
        "income_id": income.income_id,
        "category_id": category.category_id,
        "category_name": category_name,
        "amount": income.amount,
        "date": income.date,
        "note": income.note
    }

def get_incomes_by_user(db: Session, user_id: int):

    incomes = db.query(Income).filter(Income.user_id == user_id).all()
    return [
        {
            "income_id": i.income_id,
            "username": i.user.username,
            "category_name": i.category.name,
            "amount": float(i.amount),
            "date": i.date,
            "note": i.note,
        }
        for i in incomes
    ]

def get_incomes_by_month(db: Session, user_id: int, year: int, month: int):
    last_day = calendar.monthrange(year, month)[1]
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)

    incomes = db.query(Income).filter(
        Income.user_id == user_id,
        Income.date >= start_date,
        Income.date <= end_date,
    ).order_by(Income.date.desc()).all()
    return [
        {
            "income_id": i.income_id,
            "username": i.user.username,
            "category_name": i.category.name,
            "amount": float(i.amount),
            "date": i.date,
            "note": i.note,
        }
        for i in incomes
    ]

def get_incomes_by_year(db: Session, user_id: int, year: int):
    start = date(year, 1, 1)
    end = date(year, 12, 31)
    incomes = db.query(Income).filter(
        Income.user_id == user_id,
        Income.date >= start,
        Income.date <= end,
    ).order_by(Income.date.desc()).all()
    return [
        {
            "income_id": i.income_id,
            "username": i.user.username,
            "category_name": i.category.name,
            "amount": float(i.amount),
            "date": i.date,
            "note": i.note,
        }
        for i in incomes
    ]

def update_income(db: Session, income_id: int, category_name: str, amount: float = None, date_: date = None, note: str = None):
    income = db.query(Income).filter(Income.income_id == income_id).first()
    if not income:
        return None
    category = db.query(Category).filter(
        func.lower(Category.name) == category_name.lower(),
        Category.type == CategoryType.income).first()

    if not category:
        category = Category(
            name=category_name,
            type=CategoryType.income,
            description="Danh mục tự thêm",
        )
        db.add(category)
        db.commit()
        db.refresh(category)

    income.category_id = category.category_id
    if amount is not None:
        income.amount = amount
    if date_ is not None:
        income.date = date_
    if note is not None:
        income.note = note

    db.commit()
    db.refresh(income)

    return {
        "message": "✅ Cập nhật khoản thu thành công!",
        "income_id": income.income_id,
        "category_id": category.category_id,
        "category_name": category.name,
        "amount": float(income.amount),
        "date": income.date,
        "note": income.note
    }

def delete_income(db: Session, income_id: int):
    income = db.query(Income).filter(Income.income_id == income_id).first()
    if not income:
        return None
    db.delete(income)
    db.commit()
    return income

#-------------------------
#---- EXPENSE ----
def create_expense(db: Session, user_id: int, category_name: str, amount: float, date_: date, note: str = None):
    if not category_name or amount <=0:
        return {"error": "Tên danh mục và số tiền phải hợp lệ."}
    category = db.query(Category).filter(
        func.lower(Category.name) == category_name.lower(),
        Category.type == CategoryType.expense
    ).first()

    if not category:
        category = Category(
            name=category_name,
            type=CategoryType.expense,
            description="Danh mục tự thêm",
        )
        db.add(category)
        db.commit()
        db.refresh(category)
    existing_expense = db.query(Expense).filter(
        Expense.user_id == user_id,
        Expense.category_id == category.category_id,
        Expense.date == date_
    ).first()

    if existing_expense:
        return {
            "error": "⚠️ Đã có khoản chi trong cùng ngày và danh mục này! Nếu bạn muốn sửa, vui lòng vào mục cập nhật."}
    expense = Expense(
        user_id=user_id,
        category_id=category.category_id,
        amount=amount,
        date = date_,
        note=note
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return {
        "message": "💰 Đã thêm khoản chi thành công.",
        "expense_id": expense.expense_id,
        "category_id": category.category_id,
        "category_name": category_name,
        "amount": float(expense.amount),
        "date": expense.date,
        "note": expense.note
    }

def get_expenses_by_user(db: Session, user_id: int):
    expenses = db.query(Expense).filter(Expense.user_id == user_id).all()
    return [
        {
            "expense_id": e.expense_id,
            "username": e.user.username,
            "category_name": e.category.name,
            "amount": float(e.amount),
            "date": e.date,
            "note": e.note,
        }
        for e in expenses
    ]

def get_expenses_by_month(db: Session, user_id: int, year: int, month: int):
    last_day = calendar.monthrange(year, month)[1]
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)

    expenses = db.query(Expense).filter(
        Expense.user_id == user_id,
        Expense.date >= start_date,
        Expense.date <= end_date,
    ).order_by(Expense.date.desc()).all()

    return [
        {
            "expense_id": e.expense_id,
            "username": e.user.username,
            "category_name": e.category.name,
            "amount": float(e.amount),
            "date": e.date,
            "note": e.note,
        }
        for e in expenses
    ]

def get_expenses_by_year(db: Session, user_id: int, year: int):
    start = date(year, 1, 1)
    end = date(year, 12, 31)
    expenses = db.query(Expense).filter(
        Expense.user_id == user_id,
        Expense.date >= start,
        Expense.date <= end,
    ).order_by(Expense.date.desc()).all()

    return [
        {
            "expense_id": e.expense_id,
            "username": e.user.username,
            "category_name": e.category.name,
            "amount": float(e.amount),
            "date": e.date,
            "note": e.note,
        }
        for e in expenses
    ]

def update_expense(db: Session, expense_id: int, category_name: str, amount: float = None, date_: date = None, note: str = None):
    expense = db.query(Expense).filter(Expense.expense_id == expense_id).first()
    if not expense:
        return None

    category = db.query(Category).filter(
        func.lower(Category.name) == category_name.lower(),
        Category.type == CategoryType.income).first()

    if not category:
        category = Category(
            name=category_name,
            type=CategoryType.income,
            description="Danh mục tự thêm",
        )
        db.add(category)
        db.commit()
        db.refresh(category)

    expense.category_id = category.category_id

    if category_name is not None:
        expense.category_name = category_name
    if amount is not None:
        expense.amount = amount
    if date_ is not None:
        expense.date = date_
    if note is not None:
        expense.note = note

    db.commit()
    db.refresh(expense)

    return {
        "message": "✅ Cập nhật khoản thu thành công!",
        "expense_id": expense.expense_id,
        "category_id": category.category_id,
        "category_name": category.name,
        "amount": float(expense.amount),
        "date": expense.date,
        "note": expense.note
    }

def delete_expense(db: Session, expense_id: int):
    expense = db.query(Expense).filter(Expense.expense_id == expense_id).first()
    if not expense:
        return None
    db.delete(expense)
    db.commit()
    return expense

#-----------------------
#---- BUDGET ----
def create_budget(db: Session, user_id: int, category_id: int, amount: float, month: str):
    if amount <= 0:
        return {"error": "⚠️ Ngân sách phải lớn hơn 0."}
    try:
        if "-" in month:
            part = month.split("-")
            if len(part) != 2:
                raise ValueError

            if int(part[0]) <= 12 and int(part[1]) > 12:
                month_num, year = map(int, month.split("-"))
            else:
                year, month_num = map(int, month.split("-"))
        else:
            month_num = int(month)
            year = datetime.now().year
        if month_num < 1 or month_num > 12:
            return {"error": "⚠️ Tháng không hợp lệ! Vui lòng nhập từ 1 đến 12."}

        month_str = f"{year}-{month_num:02d}"

    except ValueError:
        return {"error": "⚠️ Định dạng tháng không hợp lệ! Hãy nhập theo dạng YYYY-MM hoặc số tháng (1-12)."}
    existing_budget = db.query(Budget).filter(
        Budget.user_id == user_id,
        Budget.category_id == category_id,
        Budget.month == month
    ).first()

    if existing_budget:
        return {
            "error": "⚠️ Đã có ngân sách trong cùng tháng và danh mục này! Nếu bạn muốn sửa, vui lòng vào mục cập nhật."}

    budget = Budget(
        user_id=user_id,
        category_id=category_id,
        amount=amount,
        month=month_str,
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    category = db.query(Category).filter(Category.category_id == category_id).first()
    budget.category_name = category.name if category else "❗ Không xác định"
    return budget

def get_budgets_by_user_and_month(db: Session, user_id: int, month: str):
    try:
        if "-" in month:
            part = month.split("-")
            if len(part) != 2:
                raise ValueError

            if int(part[0]) <= 12 and int(part[1]) > 12:
                month_num, year = map(int, month.split("-"))
            else:
                year, month_num = map(int, month.split("-"))
        else:
            month_num = int(month)
            year = datetime.now().year
        if month_num < 1 or month_num > 12:
            return {"error": "⚠️ Tháng không hợp lệ! Vui lòng nhập từ 1 đến 12."}

        month_str = f"{year}-{month_num:02d}"

    except ValueError:
        return {"error": "⚠️ Định dạng tháng không hợp lệ! Hãy nhập theo dạng YYYY-MM hoặc số tháng (1-12)."}

    return (
        db.query(
            Budget.budget_id,
            Budget.category_id,
            Budget.amount,
            Budget.month,
            Category.name.label("category_name")
        )
        .join(Category, Budget.category_id == Category.category_id, isouter=True)
        .filter(Budget.user_id == user_id, Budget.month == month_str)
        .all()
    )


def update_budget(db: Session, budget_id: int, category_id, amount: float = None, month: str = None):
    budget = db.query(Budget).filter(Budget.budget_id == budget_id).first()
    if not budget:
        return None
    if amount is not None:
        if amount <= 0:
            return {"error": "⚠️ Ngân sách phải lớn hơn 0."}
        budget.amount = amount
    if month is not None:
        try:
            if "-" in month:
                part = month.split("-")
                if len(part) != 2:
                    raise ValueError
                if int(part[0]) <= 12 and int(part[1]) > 12:
                    month_num, year = map(int, month.split("-"))
                else:
                    year, month_num = map(int, month.split("-"))
            else:
                month_num = int(month)
                year = datetime.now().year
            if month_num < 1 or month_num > 12:
                return {"error": "⚠️ Tháng không hợp lệ! Vui lòng nhập từ 1 đến 12."}

            budget.month = f"{year}-{month_num:02d}"
        except ValueError:
            return {"error": "⚠️ Định dạng tháng không hợp lệ! Hãy nhập theo dạng YYYY-MM hoặc số tháng (1-12)."}
    if category_id is not None:
        budget.category_id = category_id

    db.commit()
    db.refresh(budget)

    category = db.query(Category).filter(Category.category_id == category_id).first()
    budget.category_name = category.name if category else "❗ Không xác định"
    return {
        "message": f"✅ Ngân sách cho danh mục {budget.category_name} của tháng {budget.month} đã được cập nhật: {budget.amount}₫",
        "data": {
            "budget_id": budget.budget_id,
            "category_id": budget.category_id,
            "category_name": budget.category_name,
            "amount": budget.amount,
        }
    }

def delete_budget(db: Session, budget_id: int, category_id: int):
    budget = db.query(Budget).filter(Budget.budget_id == budget_id).first()
    if not budget:
        return None

    db.delete(budget)
    db.commit()
    category = db.query(Category).filter(Category.category_id == category_id).first()
    budget.category_name = category.name if category else "❗ Không xác định"
    return budget

def check_budget_exceeded(db: Session, user_id: int, category_id: int, year: int, month: int):
    if not (1 <= month <= 12):
        return {"error": "⚠️ Tháng không hợp lệ! Vui lòng nhập giá trị từ 1 đến 12."}
    if year <= 0:
        return {"error": "⚠️ Năm không hợp lệ! Vui lòng nhập năm dương lịch hợp lệ."}

    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    total_expense = (
            db.query(func.sum(Expense.amount))
            .filter(
                Expense.user_id == user_id,
                Expense.category_id == category_id,
                Expense.date >= start_date,
                Expense.date < end_date,
            )
            .scalar()  # để lấy giá trị duy nhất
            or 0
    )
    month_str = f"{year}-{month:02d}"
    budget = db.query(Budget).filter(
        Budget.user_id == user_id,
        Budget.category_id == category_id,
        Budget.month == month_str
    ).first()

    category = db.query(Category).filter(
        Category.category_id == category_id,
    ).first()
    category_name = category.name if category else "Không xác định"
    if not budget:
        return {
            "exceeded": False,
            "message": f"⚠️ Bạn chưa đặt ngân sách cho danh mục {category_name} tháng {month:02d}/{year}."
        }
    if total_expense > budget.amount:
        over = total_expense - budget.amount
        return {
            "exceeded": True,
            "message": f"🚨 Bạn đã vượt ngân sách {category_name} {over:,.0f}₫ trong tháng {month:02d}/{year}!"
        }
    remaining = budget.amount - total_expense
    return {
        "exceeded": False,
        "message": f"✅ Bạn còn {remaining:,.0f}₫ trong ngân sách {category_name} tháng {month:02d}/{year}."
    }

def get_budget_summary_for_month(db: Session, user_id:int, year: int, month: int):
    if not (1 <= month <= 12):
        return {"error": "⚠️ Tháng không hợp lệ! Vui lòng nhập giá trị từ 1 đến 12."}
    if year <= 0:
        return {"error": "⚠️ Năm không hợp lệ! Vui lòng nhập năm dương lịch hợp lệ."}

    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year+1, 1, 1)
    else:
        end_date = date(year, month+1, 1)
    month_str = f"{year}-{month:02d}"

    categories = (
        db.query(Category).filter(Category.type == CategoryType.expense).all()
    )

    kq = []
    for category in categories:
        category_name = category.name
        total_expense = (
                db.query(func.sum(Expense.amount))
                .filter(
                    Expense.user_id == user_id,
                    Expense.category_id == category.category_id,
                    Expense.date >= start_date,
                    Expense.date < end_date,
                )
                .scalar()  # để lấy giá trị duy nhất
                or 0
        )
        budget = (
            db.query(Budget)
            .filter(
            Budget.user_id == user_id,
            Budget.category_id == category.category_id,
            Budget.month == month_str
        )
        .first()
        )

        if not budget or total_expense == 0:
            continue

        if not budget:
            kq.append({
                "category_id": category.category_id,
                "category_name": category_name,
                "budget": 0,
                "expense": total_expense,
                "trang_thai": "⚠️ Chưa đặt ngân sách",
                "Canh_bao": False
            })
            continue     # bỏ qua phần phía dưới
        if total_expense > budget.amount:
            over = total_expense - budget.amount
            kq.append({
                "category_id": category.category_id,
                "category_name": category_name,
                "budget": budget.amount,
                "expense": total_expense,
                "exceeded": over,
                "trang_thai": f"🚨 Vượt ngân sách {over:,.0f}₫",
                "Canh_bao": True
            })
        else:
            remaining = budget.amount - total_expense
            kq.append({
                "category_id": category.category_id,
                "category_name": category_name,
                "budget": budget.amount,
                "expense": total_expense,
                "exceeded": remaining,
                "trang_thai": f"✅ Còn lại {remaining:,.0f}₫",
                "Canh_bao": False
            })
    if not kq:
        return {"message": "⚠️ Không tìm thấy danh mục nào có dữ liệu ngân sách hoặc chi tiêu."}
    return kq
#---------------------
#---- SETTINGS ----
def create_setting(db: Session, user_id: int):
    new_setting = Settings(user_id=user_id)
    db.add(new_setting)
    db.commit()
    db.refresh(new_setting)
    return new_setting

def get_setting_by_user(db: Session, user_id: int):
    return db.query(Settings).filter(Settings.user_id == user_id).first()

def update_setting(db: Session, setting_id: int, currency: Currency = None, saving_ratio: float = None, language: Language = None, theme: Theme = None, chart_type: ChartType = None):
    setting = db.query(Settings).filter(Settings.setting_id == setting_id).first()
    if not setting:
        return {"error": "⚠️ Cài đặt không tồn tại."}
    if currency is not None:
        setting.currency = currency
    if saving_ratio is not None:
        if saving_ratio < 0 or saving_ratio > 1:
            return {"error": "❌ Tỷ lệ tiết kiệm phải nằm trong khoảng 0–1 (ví dụ: 0.2 = 20%)."}
        setting.saving_ratio = saving_ratio
    if language is not None:
        setting.language = language
    if theme is not None:
        setting.theme = theme
    if chart_type is not None:
        setting.chart_type = chart_type

    db.commit()
    db.refresh(setting)
    return {"message": "✅ Cập nhật cài đặt thành công."}

def delete_setting(db: Session, setting_id: int):
    setting = db.query(Settings).filter(Settings.setting_id == setting_id).first()
    if not setting:
        return None
    db.delete(setting)
    db.commit()
    return {"message": f"✅ Đã xóa thành công cài đặt."}

#---------------------
#---- MONTHLY SUMMARY ----
def create_monthly_summary(db: Session, user_id: int, year: int, month: int):
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year+1, 1, 1)
    else:
        end_date = date(year, month+1, 1)
    total_income = (
        db.query(func.sum(Income.amount)).filter(
            Income.user_id == user_id,
            Income.date >= start_date,
            Income.date < end_date,
        ).scalar() or 0
    )
    total_expense = (
            db.query(func.sum(Expense.amount)).filter(
                Expense.user_id == user_id,
                Expense.date >= start_date,
                Expense.date < end_date,
            ).scalar() or 0
    )
    balance = total_income - total_expense
    month_str = f"{year}-{month:02d}"
    summary = (
        db.query(MonthlySummary).filter(
            MonthlySummary.user_id == user_id,
            MonthlySummary.month == month_str,
        ).first()
    )

    if summary:
        summary.total_income = total_income
        summary.total_expense = total_expense
        summary.balance = balance
    else:
        summary=MonthlySummary(
            user_id=user_id,
            month=month_str,
            total_income=total_income,
            total_expense=total_expense,
            balance=balance,
        )
        db.add(summary)

    db.commit()
    db.refresh(summary)
    return summary

def get_summary_by_user_and_month(db: Session, user_id: int, year: int, month: str):
    month_str = f"{year}-{month:02d}"
    return db.query(MonthlySummary).filter(
        MonthlySummary.user_id == user_id,
        MonthlySummary.month == month_str,
    ).all()