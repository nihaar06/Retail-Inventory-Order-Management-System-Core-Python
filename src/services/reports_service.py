from typing import List, Dict
from src.dao.reports_dao import r_d

class ReportError(Exception):
    pass

class r_s:
    def __init__(self):
        self.rd = r_d()

    def get_top_selling_products(self, limit: int = 5) -> List[Dict]:
        try:
            return self.rd.get_top_selling_products(limit)
        except Exception as e:
            raise ReportError(f"Failed to retrieve top selling products: {e}")

    def get_monthly_revenue(self) -> float:
        try:
            return self.rd.get_total_revenue_last_month()
        except Exception as e:
            raise ReportError(f"Failed to calculate monthly revenue: {e}")

    def get_total_orders_by_customer(self) -> List[Dict]:
        try:
            return self.rd.get_total_orders_by_customer()
        except Exception as e:
            raise ReportError(f"Failed to get orders by customer: {e}")

    def get_customers_with_multiple_orders(self) -> List[Dict]:
        try:
            return self.rd.get_customers_with_multiple_orders()
        except Exception as e:
            raise ReportError(f"Failed to get customers with multiple orders: {e}")