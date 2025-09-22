import pandas as pd
from typing import List, Dict
from src.config import get_supabase
from datetime import datetime, timedelta

class r_d:
    def __init__(self):
        pass

    def _sb(self):
        return get_supabase()

    def get_top_selling_products(self, limit: int = 5) -> List[Dict]:
        order_items_df = pd.DataFrame(self._sb().from_('order_items').select('prod_id, quantity').execute().data)
        products_df = pd.DataFrame(self._sb().table('products').select('prod_id, name, sku').execute().data)

        product_sales = order_items_df.groupby('prod_id')['quantity'].sum().reset_index()
        product_sales = product_sales.sort_values(by='quantity', ascending=False).head(limit)
        
        report_df = product_sales.merge(products_df, on='prod_id', how='left')
        report_df = report_df.rename(columns={'quantity': 'total_quantity_sold'})
        return report_df.to_dict('records')

    def get_total_revenue_last_month(self) -> float:
        orders_df = pd.DataFrame(self._sb().table('orders').select('order_date, total_amount').execute().data)
        
        orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        recent_orders = orders_df[orders_df['order_date'] >= thirty_days_ago]
        total_revenue = recent_orders['total_amount'].sum()
        return total_revenue

    def get_total_orders_by_customer(self) -> List[Dict]:
        orders_df = pd.DataFrame(self._sb().table('orders').select('cust_id').execute().data)
        customers_df = pd.DataFrame(self._sb().table('customers').select('cust_id, name').execute().data)
        
        order_counts = orders_df.groupby('cust_id').size().reset_index(name='order_count')
        
        report_df = order_counts.merge(customers_df, on='cust_id', how='left')
        report_df = report_df.rename(columns={'name': 'customer_name'})
        return report_df.to_dict('records')

    def get_customers_with_multiple_orders(self, min_orders: int = 2) -> List[Dict]:
        orders_df = pd.DataFrame(self._sb().table('orders').select('cust_id').execute().data)
        customers_df = pd.DataFrame(self._sb().table('customers').select('cust_id, name').execute().data)
        
        order_counts = orders_df.groupby('cust_id').size().reset_index(name='order_count')
        
        multiple_orders = order_counts[order_counts['order_count'] > min_orders]
        
        report_df = multiple_orders.merge(customers_df, on='cust_id', how='left')
        report_df = report_df.rename(columns={'name': 'customer_name'})
        return report_df.to_dict('records')