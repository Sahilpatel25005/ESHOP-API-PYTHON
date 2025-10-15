import json
import re
import os
from dotenv import load_dotenv
from fastapi import UploadFile, File, APIRouter, HTTPException
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPICallError
from app.database import get_db_connection


load_dotenv()

genai.configure(api_key=os.getenv("YOUR_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

generate_product_details_router = APIRouter(prefix="", tags=["/generate-product"])

@generate_product_details_router.post("/generate-product")
async def generate_product(image: UploadFile = File(...)):
    try:
        img_bytes = await image.read()
        
        # get product category from databse
        conn = get_db_connection()
        cur = conn.cursor()
        query = "select name from category"
        cur.execute(query)
        categories_row = cur.fetchall()
        if not categories_row:
            raise HTTPException(status_code=500, detail="No categories found in database")
          
        categories = [row[0] for row in categories_row]  

        response = model.generate_content([
            f"""
            You are an assistant that generates e-commerce product data.

            Task:
            - Look at the given image.
            - Generate:
                1. A short, catchy product title.
                2. A clear, engaging product description (2–3 sentences).
                3. Select the most relevant product category from this list: {categories}.
            - Return output strictly in JSON format only.

            Example:
            {{
            "title": "Trendy Black Aviator Sunglasses",
            "description": "Sleek and stylish aviators with UV protection, lightweight frame, and a modern edge.",
            "category": "Sunglasses"
            }}
            """,
            {"mime_type": image.content_type, "data": img_bytes}
        ])


        raw_text = response.text.strip()

        # 🔹 Extract JSON using regex (in case Gemini adds extra text)
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not match:
            raise HTTPException(status_code=500, detail="No valid JSON found in Gemini response")

        json_text = match.group(0)

        try:
            product_data = json.loads(json_text)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Gemini returned malformed JSON")

        return {'product_data': product_data, 'categories': categories}

    except GoogleAPICallError as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {e.message}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
      cur.close()
      conn.close()
    