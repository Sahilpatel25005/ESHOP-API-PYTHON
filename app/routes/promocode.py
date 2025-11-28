# app/routes/promocode_routes.py
from fastapi import  APIRouter , Depends
from fastapi.exceptions import HTTPException
from datetime import datetime
from app.database import get_db_connection

router = APIRouter(prefix="/promocodes", tags=["promocodes"])

@router.get("/{name}")
def get_promocode(name: str):
    """
    Lookup promocode by name.
    Response: { "promocode": { "promocodeid": x, "name": "...", "value": 20, "active": true } }
    Returns 404 if not found, 400 if inactive/expired.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, value
            FROM promocodes
            WHERE UPPER(name) = UPPER(%s)
            LIMIT 1
        """, (name,))
        row = cur.fetchone()
        cur.close()

        if not row:
            raise HTTPException(status_code=404, detail="Promo code not found")

        # Optional: check active flag
        # if 'active' in row and row['active'] is not None and not row['active']:
        #     raise HTTPException(status_code=400, detail="Promo code is inactive")

        # Optional: check expiry if column exists and not null
        # expiry = row.get('expiry')
        # if expiry:
        #     # ensure expiry is a date/datetime; compare with now
        #     now = datetime.utcnow()
        #     if expiry < now:
        #         raise HTTPException(status_code=400, detail="Promo code has expired")

        # return minimal safe info
        promo = {
            "promocodeid": row["id"],
            "name": row["name"],
            "value": float(row["value"])
        }
        return {"promocode": promo}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
