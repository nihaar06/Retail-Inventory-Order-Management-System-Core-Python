from typing import Optional, List, Dict
from src.dao.orders_dao import o_d

class OrderError(Exception):
    pass

class o_s:
    def __init__(self):
        self.od = o_d()

    def create_order(self, customer_id: int, products: List[Dict]) -> Dict:
        if not products:
            raise OrderError("Cannot create an order with no products.")

        try:
            return self.od.create_order(customer_id, products)
        except ValueError as e:
            raise OrderError(str(e))

    def get_order_details(self, order_id: int) -> Optional[Dict]:
        return self.od.fetch_details(order_id)

    def get_customer_orders(self, customer_id: int) -> List[Dict]:
        return self.od.list_orders(customer_id)

    def cancel_order(self, order_id: int) -> Dict:
        try:
            return self.od.cancel_order(order_id)
        except ValueError as e:
            raise OrderError(str(e))

    def complete_order(self, order_id: int) -> Dict:
        try:
            return self.od.complete_order(order_id)
        except ValueError as e:
            raise OrderError(str(e))