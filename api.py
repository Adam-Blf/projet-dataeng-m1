from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import sqlite3
import jwt
from datetime import datetime, timedelta

app = FastAPI(title="Olist DataIngestion API")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Secret JWT
SECRET_KEY = "SECRET"

def generate_token(data: dict):
    payload = data.copy()
    payload.update({"exp": datetime.utcnow() + timedelta(minutes=10)})
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def authenticate_user(token: str = Depends(oauth2_scheme)):
    try:
        user = jwt.decode(token, SECRET_KEY, algorithms=["HS256"]).get("sub")
        if not user:
            raise HTTPException(401, "User inconnu")
        return user
    except:
        raise HTTPException(401, "Token Invalide / Expiré")

@app.post("/token")
def login(form: OAuth2PasswordRequestForm = Depends()):
    if form.username == "admin" and form.password == "admin":
        return {"access_token": generate_token({"sub": form.username}), "token_type": "bearer"}
    raise HTTPException(400, "Erreur credentials")

def run_db_query(query: str, params=()):
    conn = sqlite3.connect("datamart.db")
    conn.row_factory = sqlite3.Row
    res = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(ix) for ix in res]

@app.get("/sales/kpi", dependencies=[Depends(authenticate_user)])
def get_kpis(limit: int = 20, offset: int = 0):
    """Extraction des KPIs par État avec pagination"""
    query = f"SELECT * FROM kpi_state LIMIT {limit} OFFSET {offset}"
    data = run_db_query(query)
    return {"data": data, "limit": limit, "offset": offset, "count": len(data)}

@app.get("/sales/rankings", dependencies=[Depends(authenticate_user)])
def get_rankings(state: str = Query(None), limit: int = 50, offset: int = 0):
    """Extraction du ranking des acheteurs par État avec pagination"""
    query = "SELECT * FROM dim_rankings"
    args = ()
    if state:
        query += " WHERE customer_state = ?"
        args = (state,)
    query += f" LIMIT {limit} OFFSET {offset}"
    
    data = run_db_query(query, args)
    return {"data": data, "limit": limit, "offset": offset, "count": len(data)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
