from typing import Optional, Dict
from src.config import get_supabase
from datetime import datetime

class pay_d:
    def __init__(self):
        pass

    def _sb(self):
        return get_supabase()

    def create_pending_payment(self, order_id: int, total_amount: float) -> Optional[Dict]:
        payload = {
            'order_id': order_id,
            'amount': total_amount,
            'status': 'Pending',
            'created_at': datetime.now()
        }
        resp = self._sb().table('payments').insert(payload).execute()
        return resp.data[0] if resp.data else None
    
    def process_payment(self, payment_id: int, method: str) -> Optional[Dict]:
        payload = {
            'status': 'Paid',
            'method': method,
            'updated_at': datetime.now()
        }
        self._sb().table('payments').update(payload).eq('payment_id', payment_id).execute()
        resp = self._sb().table('payments').select('*').eq('payment_id', payment_id).execute()
        return resp.data[0] if resp.data else None

    def refund_payment(self, payment_id: int) -> Optional[Dict]:
        payload = {
            'status': 'Refunded',
            'updated_at': datetime.now()
        }
        self._sb().table('payments').update(payload).eq('payment_id', payment_id).execute()
        resp = self._sb().table('payments').select('*').eq('payment_id', payment_id).execute()
        return resp.data[0] if resp.data else None

    def get_payment_by_order_id(self, order_id: int) -> Optional[Dict]:
        resp = self._sb().table('payments').select('*').eq('order_id', order_id).execute()
        return resp.data[0] if resp.data else None