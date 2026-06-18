import requests
import re
import base64
import os
from PIL import Image
from flask import Flask, render_template, request, jsonify,flash
from openai import OpenAI
from dotenv import load_dotenv
from openai import OpenAI
import json
from nutrition_data import nutrition_db
from nutrition_data import recommendation_db
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app=Flask(__name__)
app.secret_key = "nutrition-coach-secret"
usda_cache={}


def input_image_process(image):
    print("DEBUG image type:", type(image))
    print("DEBUG image value:", image)

    if image is None:
        raise ValueError("No file uploaded")

    if isinstance(image, str):
        print("DEBUG: image is already a string")
        return image

    if hasattr(image, "getvalue"):
        print("DEBUG: using getvalue()")
        data = image.getvalue()

    elif hasattr(image, "read"):
        print("DEBUG: using read()")
        data = image.read()

    else:
        raise TypeError(f"Unsupported image type: {type(image)}")

    if not data:
        raise ValueError("Uploaded file is empty")

    encoded = base64.b64encode(data).decode("utf-8")
    return encoded

def generate_model_response(image,user_query,assistant_prompt):
    try:
     response_model= client.responses.create(
         model="gpt-4.1-mini",
         temperature=0.2,
         max_output_tokens=1000,
         instructions=assistant_prompt,
         input=[
           {
            "role":"user",
            "content" : [
                {"type":"input_text", "text":user_query},
                {"type":"input_image","image_url": "data:image/jpeg;base64," + image}
                ]
            }
          ])
     return response_model.output_text
    except Exception as e:
        print(f"Error generating response {e}")
        return "An error occurred"

def parse_food_json(response):
    try:
        food_item= json.loads(response)
        return food_item
    
    except json.JSONDecodeError:
        cleaned_text= response.strip()
        cleaned_text = cleaned_text.replace("```json", "")
        cleaned_text = cleaned_text.replace("```", "")
        cleaned_text = cleaned_text.strip()

        try:
            food_item=json.load(cleaned_text)
            return food_item
        
        except json.JSONDecodeError:
            match= re.search(r"\[.*\]", cleaned_text, re.DOTALL)

            if match:
                food_items = json.loads(match.group(0))
                return food_items

            return []

def find_food_path(food_name):
    food_name = food_name.lower().strip()

    if food_name in nutrition_db:
        return food_name, nutrition_db[food_name]
    
    for db_food_name ,data in nutrition_db.items():
        if db_food_name in food_name or food_name in db_food_name:
            return db_food_name, data
        
    return None,None

def nutrition_calculator(food_items):
    calculated=[]
    unknown=[]

    totals={
        "calories":0,
        "protein":0,
        "carbs":0,
        "fat":0,
                }
    
    for items in food_items:
        food_name= items.get("food_name","").lower().strip()
        estimated_grams = items.get("estimated_grams",0)
        confidence= items.get("confidence","unknown")


        try:
            estimated_grams=float(estimated_grams)
        except ValueError:
            estimated_grams=0

        matched_name,food_data, source = find_food_data(food_name)

        if food_data is None or estimated_grams <= 0:
            unknown.append({
            "food_name": food_name,
            "confidence":confidence,
            "estimated_grams":estimated_grams,
                                    })
            continue

        factor= estimated_grams/100

        calories = food_data["calories_per_100g"] * factor
        protein = food_data["protein_per_100g"] * factor
        carbs = food_data["carbs_per_100g"] * factor
        fat = food_data["fat_per_100g"] * factor

        calculated.append({
            "detected_name": food_name,
            "matched_name": matched_name,
            "source":source,
            "grams": round(estimated_grams, 1),
            "confidence": confidence,
            "calories": round(calories, 1),
            "protein": round(protein, 1),
            "carbs": round(carbs, 1),
            "fat": round(fat, 1)
        })

        totals["calories"] += calories
        totals["protein"] += protein
        totals["carbs"] += carbs
        totals["fat"] += fat

        totals = {
        "calories": round(totals["calories"], 1),
        "protein": round(totals["protein"], 1),
        "carbs": round(totals["carbs"], 1),
        "fat": round(totals["fat"], 1)
        }

    return {
        "items": calculated,
        "unknown_items": unknown,
        "totals": totals
    }

def get_float_form_value(field_name):
    value = request.form.get(field_name)

    if value is None or value == "":
        return None

    try:
        return float(value)
    except ValueError:
        return None
    
def calculate_remaining_target(total, target):
    remaining={}

    for key in ["calories", "protein", "carbs", "fat"]:
        if target.get(key) is not None:
            remaining[key]= round(target[key]- total[key],1)
        else:
            remaining[key]=None

    return remaining

def recomended_food(remaining, diet_type):
    recommendations=[]

    protein_left=remaining.get("protein")
    calories_left=remaining.get("calories")

    if protein_left is None and calories_left is None:
        return recommendations
    
    for food in recommendation_db:
        tags = food["diet_tags"]

        if diet_type == "vegetarian" and "non_veg" in tags:
            continue

        if diet_type == "vegetarian_no_egg" and ("non_veg" in tags or "egg" in tags):
            continue

        if calories_left is not None and food["calories"] > calories_left + 150:
            continue

        score = 0

        if protein_left is not None:
            if protein_left >= 25 and food["protein"] >= 20:
                score += 3
            elif protein_left >= 10 and food["protein"] >= 10:
                score += 2

        if calories_left is not None:
            if calories_left < 400 and food["calories"] <= 350:
                score += 2
            elif calories_left >= 400:
                score += 1

        if score > 0:
            recommendations.append({
                "name": food["name"],
                "serving": food["serving"],
                "calories": food["calories"],
                "protein": food["protein"],
                "carbs": food["carbs"],
                "fat": food["fat"],
                "reason": food["reason"],
                "score": score
            })

    recommendations = sorted(
        recommendations,
        key=lambda item: item["score"],
        reverse=True
    )

    return recommendations[:4]
assistant_prompt = """
You are a food image recognition assistant.

Your job:
- Identify visible food items in the image.
- Estimate the portion size in grams for each food item.
- Return ONLY valid JSON.
- Do not include markdown.
- Do not include explanations outside the JSON.

Return format:
[
  {
    "food_name": "rice",
    "estimated_grams": 150,
    "confidence": "medium"
  }
]

Important:
- Use simple food names where possible.
- If unsure, still estimate but use confidence "low".
- Do not calculate calories.
- Only identify food and estimate grams.
"""

def search_usda_dataset(food_name):
    usda_api_key = os.getenv("USDA_API_KEY")

    if not usda_api_key:
        raise ValueError("cant find key")
    
    url="https://api.nal.usda.gov/fdc/v1/foods/search"

    params={
        "api_key": usda_api_key,
        "query":food_name,
        "pageSize":5
    }

    response=requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f" API ERROR : {response.status_code}")
    
    data= response.json()

    foods= data.get("foods", [])

    if not foods:
        return None
    
    avoid_words = [
        "dressing",
        "chips",
        "sauce",
        "souffle",
        "salad",
        "fried",
        "canned",
        "pickled",
        "with salt",
        "prepared"
    ]

    prefer_words = [
        "raw",
        "fresh",
        "whole",
        "fruit",
        "vegetable"
    ]

    best_food = None
    best_score = -999

    for food in foods:
        description = food.get("description", "").lower()

        score = 0

        if food_name.lower() in description:
            score += 5

        for word in prefer_words:
            if word in description:
                score += 3

        for word in avoid_words:
            if word in description:
                score -= 5

        if score > best_score:
            best_score = score
            best_food = food

    if best_food is None:
        return None

    fdc_id = best_food.get("fdcId")

    if not fdc_id:
        return None

    detail_url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}"

    detail_params = {
        "api_key": usda_api_key
    }

    detail_response = requests.get(detail_url, params=detail_params)

    if detail_response.status_code != 200:
        raise Exception(f"USDA detail API error: {detail_response.status_code}")

    return detail_response.json()

def extract_usda_nutrients(usda_food):
    if usda_food is None:
        return None

    nutrients = usda_food.get("foodNutrients", [])

    extracted = {
        "description": usda_food.get("description", "Unknown food"),
        "fdc_id": usda_food.get("fdcId"),
        "calories_per_100g": None,
        "protein_per_100g": None,
        "carbs_per_100g": None,
        "fat_per_100g": None
    }

    for item in nutrients:
        nutrient_info = item.get("nutrient", {})

        nutrient_id = nutrient_info.get("id") or item.get("nutrientId")
        nutrient_name = (
            nutrient_info.get("name")
            or item.get("nutrientName")
            or ""
        ).lower()

        unit_name = (
            nutrient_info.get("unitName")
            or item.get("unitName")
            or ""
        ).lower()

        value = item.get("amount") or item.get("value")

        if value is None:
            continue

        if nutrient_id == 1008 or ("energy" in nutrient_name and unit_name == "kcal"):
            extracted["calories_per_100g"] = value

        elif nutrient_id == 1003 or nutrient_name == "protein":
            extracted["protein_per_100g"] = value

        elif nutrient_id == 1005 or "carbohydrate" in nutrient_name:
            extracted["carbs_per_100g"] = value

        elif nutrient_id == 1004 or "total lipid" in nutrient_name or "fat" in nutrient_name:
            extracted["fat_per_100g"] = value

    return extracted


def find_food_data(food_name):
    food_name=food_name.lower().strip()
    print("LOOKING", food_name)

    if food_name in nutrition_db:
        print("founbd", food_name)
        return food_name,nutrition_db[food_name],"local"
    
    for db_food_name, data in nutrition_db.items():
        if db_food_name in food_name or food_name in db_food_name:
            print("local_mathc")
            return db_food_name,data, "local"
        
    if food_name in usda_cache:
       print("USING USDA CACHE:", food_name)
       return usda_cache[food_name]

    print("SEARCHING USDA:", food_name)
    usda_food = search_usda_dataset(food_name)

    if usda_food is None:
        print("USDA NOTHING")
        return None,None,None
    
    usda_nutrients= extract_usda_nutrients(usda_food)
    if usda_nutrients is None:
        print("couldnot extract nutriend")
        return None,None,None
    
    required_keys = [
        "calories_per_100g",
        "protein_per_100g",
        "carbs_per_100g",
        "fat_per_100g"
    ]

    for key in required_keys:
        if usda_nutrients.get(key) is None:
            print("USDA missing key:", key, "for", food_name)
            print("USDA nutrients found:", usda_nutrients)
            return None, None, None

    matched_name = usda_nutrients["description"]

    print("USDA matched:", usda_nutrients["description"])

    food_data = {
        "calories_per_100g": usda_nutrients["calories_per_100g"],
        "protein_per_100g": usda_nutrients["protein_per_100g"],
        "carbs_per_100g": usda_nutrients["carbs_per_100g"],
        "fat_per_100g": usda_nutrients["fat_per_100g"]
    }
    usda_cache[food_name] = (matched_name, food_data, "usda")

    return matched_name, food_data, "usda"
    


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    raw_model_output = None

    if request.method == "POST":
        try:
            uploaded_file = request.files.get("file")
            user_query = request.form.get("user_query")

            if not user_query:
                user_query = "Identify the food items in this image and estimate portion sizes in grams."

            encoded_image = input_image_process(uploaded_file)

            raw_model_output = generate_model_response(
                encoded_image,
                user_query,
                assistant_prompt
            )

            detected_food_items = parse_food_json(raw_model_output)

            nutrition_result = nutrition_calculator(detected_food_items)

            targets = {
                "calories": get_float_form_value("target_calories"),
                "protein": get_float_form_value("target_protein"),
                "carbs": get_float_form_value("target_carbs"),
                "fat": get_float_form_value("target_fat")
            }

            remaining = calculate_remaining_target(
                nutrition_result["totals"],
                targets
            )

            diet_type = request.form.get("diet_type", "any")

            recommendations = recomended_food(
                remaining,
                diet_type
            )

            result = {
                "detected_food_items": detected_food_items,
                "nutrition": nutrition_result,
                "targets": targets,
                "remaining": remaining,
                "recommendations": recommendations,
                "diet_type": diet_type
            }

        except Exception as e:
            print(f"Error: {e}")
            flash(f"Something went wrong: {e}", "danger")

    return render_template(
        "index.html",
        result=result,
        raw_model_output=raw_model_output


    )


if __name__ == "__main__":
    app.run(debug=True)






