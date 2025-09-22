from typing import Optional, Dict
from src.dao.payments_dao import p_d
from src.services.order_service import o_s

class PaymentError(Exception):
    pass

class pay_s:
    def __init__(self):
        self.pd = p_d()
        self.os = o_s()

    def add_pending_payment(self, order_id: int, total_amount: float) -> Optional[Dict]:
        try:
            return self.pd.create_pending_payment(order_id, total_amount)
        except Exception as e:
            raise PaymentError(f"Failed to create pending payment: {e}")

    def process_order_payment(self, order_id: int, method: str) -> Dict:
        payment = self.pd.get_payment_by_order_id(order_id)
        if not payment:
            raise PaymentError(f"Payment record for order {order_id} not found.")
        
        try:
            processed_payment = self.pd.process_payment(payment['payment_id'], method)
            self.os.complete_order(order_id)
            return processed_payment
        except ValueError as e:
            raise PaymentError(str(e))
        except Exception as e:
            raise PaymentError(f"Failed to process payment: {e}")

    def refund_order_payment(self, order_id: int) -> Dict:
        payment = self.pd.get_payment_by_order_id(order_id)
        if not payment:
            raise PaymentError(f"Payment record for order {order_id} not found.")

        if payment['status'] == 'Refunded':
            raise PaymentError(f"Payment for order {order_id} is already refunded.")
        
        try:
            return self.pd.refund_payment(payment['payment_id'])
        except Exception as e:
            raise PaymentError(f"Failed to refund payment: {e}")