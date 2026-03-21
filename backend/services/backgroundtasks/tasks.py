import time
from engine_ai import CreditScoringAI
from databases.config import SessionLocal
from databases.models import models
from .make_celery import celery_app

@celery_app.task(name="calculate_ai_score_task")
def calculate_ai_score_task(merchant_id: int):
    db = SessionLocal()
    try:
        transactions = db.query(models.Transaction).filter(
            models.Transaction.merchant_id == merchant_id
        ).all()
        time.sleep(2) 
        ai_engine = CreditScoringAI()
        score = ai_engine.calculate_score(transactions)
        recommendation = ai_engine.get_recommendation(score)
        # merchant = db.query(models.Merchant).filter(models.Merchant.id == merchant_id).first()
        # merchant.last_score = score
        # db.commit()
        
        return {
            "merchant_id": merchant_id,
            "score": score,
            "status": recommendation
        }
    finally:
        db.close()