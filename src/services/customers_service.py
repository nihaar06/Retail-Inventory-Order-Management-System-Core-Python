from typing import Optional,Dict,List
from src.dao.customers_dao import c_d

class CustomerError(Exception):
    pass
class c_s:

    def __init__(self):
        self.cd=c_d()
    def add_customer(self,name: str,email: str,phone: str,city: str)->Dict:
        try:
            return self.cd.create_customer(name,email,phone,city)
        except ValueError as e:
            raise CustomerError(str(e))
    def modify_customer(self,name:str,phone: Optional[str] =None,city:Optional[str]=None)->None:
        try:
            self.cd.update_customer(name,phone,city)
        except ValueError as e:
            raise CustomerError(str(e))
    def remove_customer(self,name:str)->None:
        try:
            self.cd.delete_customer(name)
        except ValueError as e:
            raise CustomerError(str(e))
    
    def get_all_customers(self) -> List[Dict]:
        return self.cd.list_customers()

    def find_customer(self, email: Optional[str] = None, city: Optional[str] = None) -> List[Dict]:
        if not email and not city:
            raise CustomerError("Either email or city must be provided for a search.")
        
        result = self.cd.search_customer(email, city)
        return result if result is not None else []