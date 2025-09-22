from src.config import get_supabase
from typing import Optional
# Create a new customer with details → name, email, phone, city.
# Validate that email must be unique.
# If email already exists, show an error.
# Update a customer’s phone or city.
# Delete a customer:
# Allow deletion only if the customer has no orders.
# If orders exist, block deletion with an error message.
# List all customers.
# Search customer by email or city.

class c_d:

    def __init__(self):
        pass

    def _sb(self):
        return get_supabase()
    
    def create_customer(self,name: str,email: str,phone: str,city: str):
        payload={'name':name,'email':email,'phone':phone,'city':city}
        if self._sb().table('customers').select('*').eq('email',email).execute().data:
            raise ValueError('Error! Email already exists')
        self._sb().table('customers').insert(payload).execute()
        resp=self._sb().table('customers').select('*').execute()
        return resp.data[0] if resp.data else None
    
    def update_customer(self,name:str,phone: Optional[str] ,city:Optional[str]):
        d={}
        if city is not None:
            d['city']=city
        if phone is not None:
            d['phone']=phone
        if d:
            res=self._sb().table('customers').select('*').eq('name',name).execute()
            if not res.data:
                return ValueError(f"Customer {name} does not exist")
            self._sb().table('customers').update(d).eq('name',name).execute()

    def delete_customer(self,name:str):
        res=self._sb().table('customers').select('cust_id').eq('name',name).execute()
        if not res.data:
            raise ValueError("Customer doesn't exist")
        cust_id=res.data[0]['cust_id']
        resp=self._sb().table('orders').select('*').eq('cust_id',cust_id).execute()
        if resp.data:
           raise ValueError("Cannot delete customer , Existing orders found")
        self._sb().table('customers').delete().eq('cust_id',cust_id).execute()
        print(f"Customer {name} deleted successfully")

    def list_customers(self):
        resp=self._sb().table('customers').select('*').execute()
        return resp.data
    
    def search_customer(self,email: Optional[str],city:Optional[str]):
        resp=self._sb().table('customers').select("*")
        if email is not None:
            resp=resp.eq('email',email)
        if city is not None:
            resp=resp.eq('city',city)
        f=resp.execute()
        return f.data if f.data else None
