# backend.py
import hashlib
import logging
import io
import json
import requests
import pandas as pd
import pyotp
import httpx
from datetime import datetime
from fastapi import HTTPException

from config import BASE_URL, USER_AGENT, SOURCE_ID
from utils import get_public_ip, get_mac_address
from models import OrderInput, ModifyOrderInput, CancelOrderInput

# Setup Logger
logger = logging.getLogger("MOFSL_Backend")
logging.basicConfig(level=logging.INFO)

class MotilalBackend:
    def __init__(self, api_key, client_code, password, totp_key, dob):
        self.api_key = api_key
        self.client_code = client_code
        self.password = password
        self.totp_key = totp_key
        self.dob = dob
        
        self.public_ip = get_public_ip()
        self.mac_addr = get_mac_address()
        
        # Caches for Instruments
        self._equity_df = None  
        self._fno_df = None     
        self._bse_df = None     
        self._bsefo_df = None   
        self._mcx_df = None     
        self._nsecd_df = None   
        self._bsecd_df = None   

    def _get_headers(self, auth_token=None):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': USER_AGENT,
            'ApiKey': self.api_key,
            'ClientLocalIp': '127.0.0.1',
            'ClientPublicIp': self.public_ip,
            'MacAddress': self.mac_addr,
            'SourceId': SOURCE_ID,
            'vendorinfo': self.client_code, 
            'osname': 'Windows 10',
            'osversion': '10.0.19041',
            'devicemodel': 'AHV',
            'manufacturer': 'DELL',
            'productname': 'OpenAlgo',
            'productversion': '1.0.0',
            'browsername': 'Chrome',
            'browserversion': '120.0'
        }
        if auth_token:
            headers["Authorization"] = auth_token
        return headers

    def _generate_password_hash(self):
        raw = f"{self.password}{self.api_key}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def get_totp(self):
        try:
            return pyotp.TOTP(self.totp_key).now()
        except Exception:
            raise ValueError("Invalid TOTP Key")

    # --- 1. LOGIN ---
    async def login(self):
        url = f"{BASE_URL}/rest/login/v3/authdirectapi"
        payload = {
            "userid": self.client_code,
            "password": self._generate_password_hash(),
            "totp": self.get_totp(),
            "2FA": self.dob 
        }
        
        logger.info(f"Attempting login for {self.client_code}")
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self._get_headers())
            
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "SUCCESS":
                return data.get("AuthToken")
            else:
                raise ValueError(f"Login Failed: {data.get('message')}")
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    # --- 2. INSTRUMENT MAPPING ---
    async def load_instruments(self):
        try:
            def fetch_csv(name):
                logger.info(f"Downloading {name} Masters...")
                r = requests.get(f"{BASE_URL}/getscripmastercsv?name={name}")
                if r.status_code == 200:
                    df = pd.read_csv(io.StringIO(r.text))
                    df.columns = [c.strip().lower() for c in df.columns]
                    return df
                return None

            if self._equity_df is None: self._equity_df = fetch_csv("NSE")
            if self._fno_df is None: self._fno_df = fetch_csv("NSEFO")
            if self._bse_df is None: self._bse_df = fetch_csv("BSE")
            if self._mcx_df is None: self._mcx_df = fetch_csv("MCX")
            if self._bsefo_df is None: self._bsefo_df = fetch_csv("BSEFO")
            if self._nsecd_df is None: self._nsecd_df = fetch_csv("NSECD")

            logger.info("All Instruments loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to download instruments: {e}")

    def get_instrument_data(self, symbol, exchange):
        symbol = symbol.strip().upper()
        exchange = exchange.upper()
        
        if str(symbol).isdigit():
            return {"scripcode": int(symbol), "lotsize": 1}

        df = None
        if exchange == "NSE": df = self._equity_df
        elif exchange in ["NSEFO", "NFO"]: df = self._fno_df
        elif exchange == "BSE": df = self._bse_df
        elif exchange == "MCX": df = self._mcx_df
        elif exchange == "BSEFO": df = self._bsefo_df
        elif exchange in ["NSECD", "CDS"]: df = self._nsecd_df
        elif exchange == "BSECD": df = self._bsecd_df

        if df is None:
            raise ValueError(f"Instruments not loaded or Invalid Exchange {exchange}")

        res = df[df['scripshortname'] == symbol]
        if res.empty:
            res = df[df['scripname'] == symbol]
        if res.empty and exchange in ["NSE", "BSE"]:
            res = df[df['scripname'].str.contains(symbol, na=False)]

        if not res.empty:
            row = res.iloc[0]
            lot = row.get('marketlot', 1)
            if pd.isna(lot): lot = 1
            return {"scripcode": int(row['scripcode']), "lotsize": int(lot)}
            
        raise ValueError(f"Symbol {symbol} not found in {exchange}")

    # --- 3. FUNDS ---
    async def get_funds(self, auth_token):
        url = f"{BASE_URL}/rest/report/v1/getreportmargindetail"
        headers = self._get_headers(auth_token)
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={}, headers=headers)
        
        avail_cash = 0.0
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "SUCCESS":
                items = data.get("data", [])
                for item in items:
                    srno = item.get("srno")
                    amount = float(item.get("amount", 0))
                    if srno == 102:
                        avail_cash = amount
                        break
                    elif srno == 201 and avail_cash == 0:
                        avail_cash = amount
        return avail_cash

    # --- 4. PLACE ORDER ---
    def _map_product_type(self, product: str) -> str:
        p = product.upper()
        if p in ["MIS", "INTRADAY"]: return "NORMAL" 
        elif p in ["CNC", "DELIVERY"]: return "DELIVERY"
        elif p in ["NRML", "NORMAL", "CARRYFORWARD"]: return "NORMAL"
        elif p == "VALUEPLUS": return "VALUEPLUS"
        return "NORMAL"

    def _map_exchange(self, exchange: str) -> str:
        exc = exchange.upper()
        if exc == "NFO": return "NSEFO"
        if exc == "CDS": return "NSECD"
        return exc

    async def place_order(self, auth_token, data: OrderInput):
        exch = self._map_exchange(data.exchange)
        inst = self.get_instrument_data(data.symbol, exch)
        scrip_code = inst['scripcode']
        lot_size = inst['lotsize']
        
        actual_qty = data.quantity
        qty_in_lots = actual_qty
        
        if exch in ["NSEFO", "MCX", "NSECD", "BSEFO", "BSECD"]:
            if actual_qty % lot_size != 0:
                raise ValueError(f"Qty {actual_qty} must be multiple of Lot {lot_size}")
            qty_in_lots = int(actual_qty / lot_size)
        
        payload = {
            "clientcode": self.client_code,
            "exchange": exch,
            "symboltoken": scrip_code,
            "buyorsell": data.transaction_type.upper(),
            "ordertype": data.order_type.upper(),
            "producttype": self._map_product_type(data.product),
            "orderduration": data.validity.upper(),
            "price": float(data.price),
            "triggerprice": float(data.trigger_price),
            "quantityinlot": qty_in_lots,
            "disclosedquantity": 0,
            "amoorder": data.is_amo,
            "tag": data.tag
        }
        
        logger.info(f"Place Order: {payload}")
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BASE_URL}/rest/trans/v1/placeorder", json=payload, headers=self._get_headers(auth_token))
            
        res_data = response.json()
        if res_data.get("status") == "SUCCESS":
            return {"status": "success", "order_id": res_data.get("uniqueorderid"), "message": res_data.get("message")}
        else:
            msg = res_data.get("message", "Unknown Error")
            code = res_data.get("errorcode", "")
            raise HTTPException(status_code=400, detail=f"{msg} (Code: {code})")

    async def logout(self, auth_token):
        url = f"{BASE_URL}/rest/login/v1/logout"
        headers = self._get_headers(auth_token)
        payload = {"clientcode": self.client_code}
        async with httpx.AsyncClient() as client:
            await client.post(url, json=payload, headers=headers)

    # --- NEW METHODS ---
    async def modify_order(self, auth_token, data: ModifyOrderInput):
        last_mod_time = data.last_modified_time or datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        payload = {
            "clientcode": self.client_code,
            "uniqueorderid": data.unique_order_id,
            "newordertype": data.new_order_type,
            "neworderduration": data.new_validity,
            "newprice": data.new_price,
            "newtriggerprice": data.new_trigger_price,
            "newquantityinlot": data.new_quantity,
            "newdisclosedquantity": 0,
            "newgoodtilldate": "",
            "lastmodifiedtime": last_mod_time,
            "qtytradedtoday": data.qty_traded_today
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BASE_URL}/rest/trans/v2/modifyorder", json=payload, headers=self._get_headers(auth_token))
        return response.json()

    async def cancel_order(self, auth_token, data: CancelOrderInput):
        payload = {"clientcode": self.client_code, "uniqueorderid": data.unique_order_id}
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BASE_URL}/rest/trans/v1/cancelorder", json=payload, headers=self._get_headers(auth_token))
        return response.json()

    async def get_generic_report(self, auth_token, endpoint):
        payload = {"clientcode": self.client_code}
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BASE_URL}{endpoint}", json=payload, headers=self._get_headers(auth_token))
        return response.json()

    async def get_ltp(self, auth_token, exchange, symbol):
        exch = self._map_exchange(exchange)
        inst = self.get_instrument_data(symbol, exch)
        payload = {"clientcode": self.client_code, "exchange": exch, "scripcode": inst['scripcode']}
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BASE_URL}/rest/report/v1/getltpdata", json=payload, headers=self._get_headers(auth_token))
        return response.json()

    async def get_brokerage(self, auth_token, exchange, series="EQ"):
        payload = {"clientcode": self.client_code, "exchangename": self._map_exchange(exchange), "series": series}
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BASE_URL}/rest/report/v1/getbrokeragedetail", json=payload, headers=self._get_headers(auth_token))
        return response.json()