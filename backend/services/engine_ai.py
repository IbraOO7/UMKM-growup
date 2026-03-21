import numpy as np
import logging
from typing import List, Dict, Union
from decimal import Decimal, ROUND_HALF_UP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScoringException(Exception):
    pass

class CreditScoringAI:
    BASE_SCORE = 40.0
    MAX_SCORE = 100.0
    VOLUME_THRESHOLD = 10_000_000  
    FREQUENCY_THRESHOLD = 30       
    
    WEIGHT_VOLUME = 0.6
    WEIGHT_FREQUENCY = 0.4

    @classmethod
    def calculate_score(cls, transactions: List[any]) -> float:
        try:
            if not transactions:
                logger.info("No transactions found. Returning base score.")
                return cls.BASE_SCORE
            amounts = [float(t.amount) for t in transactions if hasattr(t, 'amount')]
            
            if not amounts:
                raise ScoringException("Transactions found but no valid amount data present.")

            total_volume = sum(amounts)
            transaction_count = len(amounts)
            volume_score = min((total_volume / cls.VOLUME_THRESHOLD) * 100, 100)
            frequency_score = min((transaction_count / cls.FREQUENCY_THRESHOLD) * 100, 100)
            final_score = (volume_score * cls.WEIGHT_VOLUME) + (frequency_score * cls.WEIGHT_FREQUENCY)
            final_score = max(min(final_score, cls.MAX_SCORE), 0)

            logger.info(f"Score calculated: {final_score} for {transaction_count} transactions.")
            return float(Decimal(str(final_score)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

        except Exception as e:
            logger.error(f"Critical error in AI Scoring Engine: {str(e)}")
            return cls.BASE_SCORE

    @staticmethod
    def get_recommendation(score: float) -> Dict[str, Union[str, float]]:
        if score >= 80:
            result = {"tier": "Platinum", "status": "Sangat Layak", "interest_rate_estimate": "low"}
        elif score >= 60:
            result = {"tier": "Gold", "status": "Layak", "interest_rate_estimate": "medium-low"}
        elif score >= 40:
            result = {"tier": "Silver", "status": "Perlu Pendampingan", "interest_rate_estimate": "medium"}
        else:
            result = {"tier": "Bronze", "status": "Risiko Tinggi", "interest_rate_estimate": "N/A"}
        
        return result