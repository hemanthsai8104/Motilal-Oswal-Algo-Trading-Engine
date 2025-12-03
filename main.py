# main.py
import uvicorn
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from models import MotilalInput, OrderInput, ModifyOrderInput, CancelOrderInput, GenericRequest
from backend import MotilalBackend

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MOFSL_App")

# Global Store
MOFSL_SESSIONS = {} 

app = FastAPI(title="Motilal Oswal Integration (Modular)")

@app.post("/validate_motilal")
async def login(data: MotilalInput):
    try:
        backend = MotilalBackend(data.api_key, data.userId, data.pin, data.totp_key, data.dob)
        
        token = await backend.login()
        await backend.load_instruments()
        funds = await backend.get_funds(token)
        
        MOFSL_SESSIONS[data.userId] = {"backend": backend, "token": token}
        
        return {"status": True, "message": "Login Successful", "data": {"userId": data.userId, "token": token, "funds": funds}}
    except Exception as e:
        logger.error(str(e))
        return JSONResponse(status_code=500, content={"status": False, "message": str(e)})

@app.post("/place_order_motilal")
async def place_order(data: OrderInput):
    try:
        session = MOFSL_SESSIONS.get(data.userId)
        if not session: raise HTTPException(status_code=401, detail="Session expired")
        return await session["backend"].place_order(session["token"], data)
    except Exception as e:
        logger.error(f"Order Error: {str(e)}")
        status = 400 if hasattr(e, 'detail') else 500
        return JSONResponse(status_code=status, content={"status": False, "message": str(e) if not hasattr(e, 'detail') else e.detail})

@app.post("/modify_order_motilal")
async def modify_order(data: ModifyOrderInput):
    session = MOFSL_SESSIONS.get(data.userId)
    if not session: return {"status": False, "message": "Session expired"}
    return await session["backend"].modify_order(session["token"], data)

@app.post("/cancel_order_motilal")
async def cancel_order(data: CancelOrderInput):
    session = MOFSL_SESSIONS.get(data.userId)
    if not session: return {"status": False, "message": "Session expired"}
    return await session["backend"].cancel_order(session["token"], data)

@app.post("/get_order_book")
async def get_order_book(user_id: str):
    session = MOFSL_SESSIONS.get(user_id)
    if not session: return {"status": False, "message": "Session expired"}
    return await session["backend"].get_generic_report(session["token"], "/rest/book/v2/getorderbook")

@app.post("/get_trade_book")
async def get_trade_book(user_id: str):
    session = MOFSL_SESSIONS.get(user_id)
    if not session: return {"status": False, "message": "Session expired"}
    return await session["backend"].get_generic_report(session["token"], "/rest/book/v1/gettradebook")

@app.post("/get_positions")
async def get_positions(user_id: str):
    session = MOFSL_SESSIONS.get(user_id)
    if not session: return {"status": False, "message": "Session expired"}
    return await session["backend"].get_generic_report(session["token"], "/rest/book/v1/getposition")

@app.post("/get_holdings")
async def get_holdings(user_id: str):
    session = MOFSL_SESSIONS.get(user_id)
    if not session: return {"status": False, "message": "Session expired"}
    return await session["backend"].get_generic_report(session["token"], "/rest/report/v1/getdpholding")

@app.post("/get_margin_summary")
async def get_margin_summary(user_id: str):
    session = MOFSL_SESSIONS.get(user_id)
    if not session: return {"status": False, "message": "Session expired"}
    return await session["backend"].get_generic_report(session["token"], "/rest/report/v1/getreportmarginsummary")

@app.post("/get_ltp")
async def get_ltp(req: GenericRequest):
    session = MOFSL_SESSIONS.get(req.userId)
    if not session: return {"status": False, "message": "Session expired"}
    if not req.exchange or not req.symbol: return {"status": False, "message": "Exchange and Symbol required"}
    return await session["backend"].get_ltp(session["token"], req.exchange, req.symbol)

@app.post("/get_brokerage")
async def get_brokerage(req: GenericRequest):
    session = MOFSL_SESSIONS.get(req.userId)
    if not session: return {"status": False, "message": "Session expired"}
    if not req.exchange: return {"status": False, "message": "Exchange required"}
    return await session["backend"].get_brokerage(session["token"], req.exchange)

@app.post("/logout_motilal")
async def logout(user_id: str):
    if user_id in MOFSL_SESSIONS:
        session = MOFSL_SESSIONS.pop(user_id)
        try:
            await session["backend"].logout(session["token"])
        except: pass
        return {"status": True, "message": "Logged out"}
    return {"status": False, "message": "User not logged in"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)