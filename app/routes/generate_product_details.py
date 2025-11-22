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

        # Get categories
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT name FROM category")
        categories_row = cur.fetchall()

        if not categories_row:
            raise HTTPException(status_code=500, detail="No categories found in database")

        categories = [row[0] for row in categories_row]

        product_data = ""  # default fallback

        # --- Try Gemini AI ---
        try:
            response = model.generate_content([
                f"""
                You are an assistant that generates e-commerce product data.

                Task:
                - Look at the given image.
                - Generate:
                    1. A short product title.
                    2. A 2–3 sentence product description.
                    3. Select the most relevant category from: {categories}.
                - Return only JSON.
                """,
                {"mime_type": image.content_type, "data": img_bytes}
            ])

            raw_text = response.text.strip()

            # Extract JSON
            match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if match:
                json_text = match.group(0)
                product_data = json.loads(json_text)
            else:
                product_data = ""  # fallback if JSON not found

        except Exception as gemini_error:
            # ❗ Don’t raise error — still return categories
            product_data = ""

        # FINAL MANDATORY RESPONSE
        return {
            "product_data": product_data if product_data else "",
            "categories": categories
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    finally:
        cur.close()
        conn.close()

    