from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from database import Base, engine
from routers import users, incomes, expense, budgets, budgets1,settings, summaries
import traceback

Base.metadata.create_all(engine)
app = FastAPI(
    title="Quản lý chi tiêu cá nhân",
    version="1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(incomes.router)
app.include_router(expense.router)
app.include_router(settings.router)
app.include_router(summaries.router)

app.include_router(budgets.router)
app.include_router(budgets1.router)

@app.get("/")
def read_root():
    return {"message": "Xin chào đến với trang Quản lý chi tiêu cá nhân 💰"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

@app.exception_handler(Exception)
async def debug_exception_handler(request, exc):
    print("🔥 DEBUG ERROR:", traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"error_type": str(type(exc).__name__), "error_detail": str(exc)}
    )

