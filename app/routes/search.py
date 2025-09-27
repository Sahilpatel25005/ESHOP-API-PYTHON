from app.database import get_db_connection
from app.models.search_model import searchAI
from fastapi import APIRouter
import logging
import google.generativeai as genai
import json


genai.configure(api_key="AIzaSyBZsPu8e8DF-7bqvCZBTMrI3ckUui7lO7o")
model = genai.GenerativeModel("gemini-1.5-flash")

search_router = APIRouter(prefix="", tags=['/search'])

@search_router.post('/search')
def search(search: searchAI):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
       
        prompt = f"""You are an assistant that extracts structured data from a user's product search query.

                Only return valid raw JSON (no explanations, no markdown, no code blocks like ```json). Your output must be pure JSON.

                Example input: "Find some watch under 2000"
                Expected output:
                {{
                "category": "Smartwatch",
                "max_price": 2000
                }}

                Rules:
                - JSON must have three keys: "category", "min_price" and "max_price". 
                - Valid categories: "Smartwatch", "Headphones", or "All".
                - If the query does not mention price or category, use defaults: category = "All", max_price = 1000000.
                - If user search give me items or name of specific item between or in range 2000 to 4000 than that time give min_price = 2000 and max_price = 4000.
                - By defult min_price = 0.
                - Infer the category from common product keywords. For example, "airpods", "buds", "earphones" → "Headphones", and "watch", "fitbit", "band" → "Smartwatch".

                Now extract from this search: "{search.query}"
                Return only the JSON object, nothing else.
                """
                
        res = model.generate_content(prompt)
        print(f"Response from AI: {res.text}")

        data = json.loads(res.text)

        print(f"Response from AI: {data}")

        category = data.get("category")
        max_price = data.get("max_price")
        min_price = data.get("min_price")
        

        if not category :
            return {"error": "Missing category or max_price in AI response."}

        cur.execute(
            "select p.* from product p join category c on p.categoryid = c.categoryid where lower(c.name) like lower(%s) and p.price between %s and %s",
            (f"%{category}%", min_price, max_price)
        )

        rows = cur.fetchall()
        
        ids = []
        for row in rows:
            ids.append(row[0]) #give product id that is filter by search query
        return ids

    except Exception as e:
        logging.error(f"Error search item: {e}")
        return {"error": "Failed to search item"}
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()