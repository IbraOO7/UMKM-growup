from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from databases.config import get_db, Base, engine
from databases.models import models
from services.engine_ai import CreditScoringAI
from pydantic import BaseModel
from services.backgroundtasks.tasks import calculate_ai_score_task

Base.metadata.create_all(bind=engine)

app = FastAPI(title="UMKM Grow-Up API")

class TransactionCreate(BaseModel):
    merchant_id: int
    amount: float

@app.get("/")
def home():
    return {"message": "Welcome to UMKM Grow-Up API - DIGDAYA 2026"}

@app.post("/transactions/")
def create_transaction(data: TransactionCreate, db: Session = Depends(get_db)):
    new_trans = models.Transaction(amount=data.amount, merchant_id=data.merchant_id)
    db.add(new_trans)
    db.commit()
    return {"status": "success", "message": "Transaksi QRIS berhasil dicatat"}

@app.get("/scoring/{merchant_id}")
def get_merchant_score(merchant_id: int, db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).filter(models.Transaction.merchant_id == merchant_id).all()
    ai_engine = CreditScoringAI()
    score = ai_engine.calculate_score(transactions)
    recommendation = ai_engine.get_recommendation(score)
    
    return {
        "merchant_id": merchant_id,
        "credit_score": score,
        "total_transactions": len(transactions),
        "status": recommendation,
        "next_step": "Tingkatkan transaksi harian untuk skor lebih tinggi!"
    }

@app.post("/api/v1/scoring/trigger/{merchant_id}")
async def trigger_scoring(merchant_id: int):
    task = calculate_ai_score_task.delay(merchant_id)
    return {"task_id": task.id, "status": "Processing AI Scoring in Background"}

@app.get("/api/v1/scoring/status/{task_id}")
async def get_task_status(task_id: str):
    from services.backgroundtasks.make_celery import celery_app
    task_result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }