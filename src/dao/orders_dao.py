from typing import Optional, List, Dict
from src.config import get_supabase
from datetime import date

class o_d:
    def __init__(self):
        pass

    def _sb(self):
        return get_supabase()

    def create_order(self, customer_id: int, prods: List[Dict]) -> Optional[Dict]:
        customer_check = self._sb().table('customers').select('*').eq('cust_id', customer_id).execute()
        if not customer_check.data:
            raise ValueError("Customer not found")

        total_amount = 0
        products_to_update = []
        order_items_payload = []

        for item in prods:
            prod_id = item['prod_id']
            qty = item['qty']
            
            product_data = self._sb().table('products').select('price, stock').eq('prod_id', prod_id).execute()
            if not product_data.data:
                raise ValueError(f"Product with ID {prod_id} not found")
            
            product = product_data.data[0]
            if product['stock'] < qty:
                raise ValueError(f"Insufficient stock for product {prod_id}. Available: {product['stock']}, Requested: {qty}")
            
            new_stock = product['stock'] - qty
            price = product['price']
            total_amount += price * qty
            
            products_to_update.append({'prod_id': prod_id, 'new_stock': new_stock})
            order_items_payload.append({'prod_id': prod_id, 'quantity': qty, 'price': price})
        
        # Deduct stock
        for update in products_to_update:
            self._sb().table('products').update({'stock': update['new_stock']}).eq('prod_id', update['prod_id']).execute()

        # Insert into orders table
        order_payload = {
            'cust_id': customer_id,
            'order_date': date.today(),
            'status': 'Placed',
            'total_amount': total_amount
        }
        resp = self._sb().table('orders').insert(order_payload).execute()
        order = resp.data[0] if resp.data else None
        
        if order:
            order_id = order['order_id']
            # Insert into order_items table
            for item in order_items_payload:
                item['order_id'] = order_id
            self._sb().table('order_items').insert(order_items_payload).execute()
            
            return self.fetch_details(order_id)
        
        return None

    def fetch_details(self, order_id: int) -> Optional[Dict]:
        order_resp = self._sb().table('orders').select('*').eq('order_id', order_id).execute()
        if not order_resp.data:
            return None
        
        order_info = order_resp.data[0]
        customer_id = order_info['cust_id']
        
        customer_resp = self._sb().table('customers').select('*').eq('cust_id', customer_id).execute()
        order_items_resp = self._sb().table('order_items').select('*').eq('order_id', order_id).execute()
        
        details = {
            'order_info': order_info,
            'customer_info': customer_resp.data[0] if customer_resp.data else None,
            'order_items': order_items_resp.data if order_items_resp.data else []
        }
        return details

    def list_orders(self, customer_id: int) -> List[Dict]:
        orders_resp = self._sb().table('orders').select('*').eq('cust_id', customer_id).execute()
        if not orders_resp.data:
            return []
            
        all_orders_details = []
        for order in orders_resp.data:
            details = self.fetch_details(order['order_id'])
            if details:
                all_orders_details.append(details)
        return all_orders_details

    def cancel_order(self, order_id: int) -> Optional[Dict]:
        order_resp = self._sb().table('orders').select('*').eq('order_id', order_id).execute()
        if not order_resp.data:
            raise ValueError(f"Order {order_id} not found")
        
        order = order_resp.data[0]
        if order['status'] != 'Placed':
            raise ValueError(f"Cannot cancel order with status '{order['status']}'")

        order_items_resp = self._sb().table('order_items').select('*').eq('order_id', order_id).execute()
        if not order_items_resp.data:
            return None
        
        # Restore product stock
        for item in order_items_resp.data:
            prod_id = item['prod_id']
            qty = item['quantity']
            
            product_resp = self._sb().table('products').select('stock').eq('prod_id', prod_id).execute()
            if product_resp.data:
                current_stock = product_resp.data[0]['stock']
                new_stock = current_stock + qty
                self._sb().table('products').update({'stock': new_stock}).eq('prod_id', prod_id).execute()

        # Update order status to CANCELLED
        self._sb().table('orders').update({'status': 'Cancelled'}).eq('order_id', order_id).execute()
        
        return self.fetch_details(order_id)
        
    def complete_order(self, order_id: int) -> Optional[Dict]:
        order_resp = self._sb().table('orders').select('*').eq('order_id', order_id).execute()
        if not order_resp.data:
            raise ValueError(f"Order {order_id} not found")
        
        order = order_resp.data[0]
        if order['status'] != 'Placed':
            raise ValueError(f"Cannot complete order with status '{order['status']}'")

        self._sb().table('orders').update({'status': 'Completed'}).eq('order_id', order_id).execute()
        return self.fetch_details(order_id)