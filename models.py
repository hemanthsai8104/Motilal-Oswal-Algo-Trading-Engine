# models.py
from typing import Optional
from pydantic import BaseModel

class MotilalInput(BaseModel):
    api_key: str
    secretKey: str = "" 
    redirectURL: str = "" 
    mobile: str      # userId / ClientCode
    pin: str         # The Password
    totp_key: str
    userId: str      # ClientCode
    dob: str         # Date of Birth (DD/MM/YYYY)

class OrderInput(BaseModel):
    userId: str
    symbol: str             # e.g. "RELIANCE", "GOLD", "SENSEX"
    exchange: str = "NSE"   # NSE, NSEFO, BSE, BSEFO, MCX, NSECD
    transaction_type: str   # BUY or SELL
    order_type: str         # LIMIT, MARKET, STOPLOSS
    quantity: int           # Total quantity
    price: Optional[float] = 0.0
    trigger_price: Optional[float] = 0.0
    product: str = "NORMAL" # MIS, CNC, NORMAL, DELIVERY
    validity: str = "DAY"   # DAY, IOC
    tag: Optional[str] = "OpenAlgo"
    is_amo: str = "N"       # Y or N

class ModifyOrderInput(BaseModel):
    userId: str
    unique_order_id: str
    new_order_type: str        
    new_quantity: int          
    new_price: float
    new_trigger_price: float = 0.0
    new_validity: str = "DAY"
    last_modified_time: Optional[str] = None 
    qty_traded_today: Optional[int] = 0
    exchange: str = "NSE"      

class CancelOrderInput(BaseModel):
    userId: str
    unique_order_id: str

class GenericRequest(BaseModel):
    userId: str
    exchange: Optional[str] = None
    scripcode: Optional[str] = None
    symbol: Optional[str] = None