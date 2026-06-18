import streamlit as st

from app import (
    input_image_process,
    generate_model_response,
    parse_food_json,
    calculate_remaining_target,
    nutrition_calculator,
    recomended_food,
    assistant_prompt
)


# -----------------------------
# Assistant prompt for GPT vision
# -----------------------------

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
  },
  {
    "food_name": "paneer",
    "estimated_grams": 100,
    "confidence": "medium"
  }
]

Important:
- Use simple food names where possible.
- If unsure, still estimate but use confidence "low".
- Do not calculate calories.
- Only identify food and estimate grams.
"""


# -----------------------------
# Streamlit page setup
# -----------------------------

st.set_page_config(
    page_title="AI Nutrition Coach",
    page_icon="🥗",
    layout="wide"
)

st.title("🥗 AI Nutrition Coach")

st.write(
    "Upload a food image, estimate nutrition using GPT vision, "
    "calculate macros from your dataset, and get food recommendations."
)


# -----------------------------
# User inputs
# -----------------------------

uploaded_file = st.file_uploader(
    "Upload your food image",
    type=["jpg", "jpeg", "png"]
)

user_query = st.text_input(
    "Your question",
    value="Identify the food items in this image and estimate portion sizes in grams."
)

st.subheader("Daily Macro Targets")

col1, col2, col3, col4 = st.columns(4)

with col1:
    target_calories = st.number_input(
        "Calories",
        min_value=0,
        value=1900
    )

with col2:
    target_protein = st.number_input(
        "Protein (g)",
        min_value=0,
        value=130
    )

with col3:
    target_carbs = st.number_input(
        "Carbs (g)",
        min_value=0,
        value=200
    )

with col4:
    target_fat = st.number_input(
        "Fat (g)",
        min_value=0,
        value=55
    )

diet_type = st.selectbox(
    "Diet preference",
    ["any", "vegetarian", "vegetarian_no_egg"]
)


# -----------------------------
# Analyze button
# -----------------------------

if st.button("Analyze Meal"):
    if uploaded_file is None:
        st.error("Please upload a food image first.")

    else:
        try:
            with st.spinner("Analyzing meal..."):
                # Reset file pointer before reading
                uploaded_file.seek(0)

                # Convert image to base64
                encoded_image = input_image_process(uploaded_file)

                # Reset again so Streamlit can display the image
                uploaded_file.seek(0)

                # Ask GPT to detect food items
                raw_model_output = generate_model_response(
                    encoded_image,
                    user_query,
                    assistant_prompt
                )

                # Convert GPT JSON text into Python list
                detected_food_items = parse_food_json(raw_model_output)

                if not detected_food_items:
                    st.error("GPT did not return valid food JSON.")
                    st.subheader("Raw GPT Output")
                    st.code(raw_model_output)
                    st.stop()

                # Calculate nutrition using local dataset
                nutrition_result = nutrition_calculator(detected_food_items)

                # Create user target dictionary
                targets = {
                    "calories": target_calories,
                    "protein": target_protein,
                    "carbs": target_carbs,
                    "fat": target_fat
                }

                # Calculate remaining daily targets
                remaining = calculate_remaining_target(
                    nutrition_result["totals"],
                    targets
                )

                # Recommend foods
                recommendations = recomended_food(
                    remaining,
                    diet_type
                )

            # -----------------------------
            # Display uploaded image
            # -----------------------------

            st.subheader("Uploaded Image")
            st.image(uploaded_file, width='stretch')


            # -----------------------------
            # Display detected food items
            # -----------------------------

            st.subheader("Detected Food Items")

            st.caption("Nutrition values are calculated using local data first, with USDA FoodData Central as fallback.")

            if nutrition_result["items"]:
                st.dataframe(
                    nutrition_result["items"],
                    width='stretch'
                )
            else:
                st.warning("No detected foods matched your nutrition dataset.")


            # -----------------------------
            # Display total meal nutrition
            # -----------------------------

            st.subheader("Total Meal Nutrition")

            m1, m2, m3, m4 = st.columns(4)

            with m1:
                st.metric(
                    "Calories",
                    nutrition_result["totals"]["calories"]
                )

            with m2:
                st.metric(
                    "Protein",
                    f'{nutrition_result["totals"]["protein"]}g'
                )

            with m3:
                st.metric(
                    "Carbs",
                    f'{nutrition_result["totals"]["carbs"]}g'
                )

            with m4:
                st.metric(
                    "Fat",
                    f'{nutrition_result["totals"]["fat"]}g'
                )


            # -----------------------------
            # Display remaining macros
            # -----------------------------

            st.subheader("Remaining Daily Targets")

            r1, r2, r3, r4 = st.columns(4)

            with r1:
                st.metric(
                    "Calories Left",
                    remaining["calories"]
                )

            with r2:
                st.metric(
                    "Protein Left",
                    f'{remaining["protein"]}g'
                )

            with r3:
                st.metric(
                    "Carbs Left",
                    f'{remaining["carbs"]}g'
                )

            with r4:
                st.metric(
                    "Fat Left",
                    f'{remaining["fat"]}g'
                )


            # -----------------------------
            # Display recommendations
            # -----------------------------

            st.subheader("Recommended Foods")

            if recommendations:
                for food in recommendations:
                    with st.container(border=True):
                        st.write(f'### {food["name"]}')
                        st.write(food["serving"])

                        st.write(
                            f'{food["calories"]} kcal | '
                            f'{food["protein"]}g protein | '
                            f'{food["carbs"]}g carbs | '
                            f'{food["fat"]}g fat'
                        )

                        st.caption(food["reason"])
            else:
                st.info("No recommendations found. Try adding or changing your macro targets.")


            # -----------------------------
            # Display unknown dataset items
            # -----------------------------

            if nutrition_result["unknown_items"]:
                st.subheader("Items Not Found in Dataset")
                st.dataframe(
                    nutrition_result["unknown_items"],
                    width='stretch'
                )


            # -----------------------------
            # Disclaimer
            # -----------------------------

            st.subheader("Disclaimer")

            st.warning(
                "The nutritional information and calorie estimates provided are approximate "
                "and are based on general food data. Actual values may vary depending on "
                "portion size, ingredients, preparation methods, and individual variation. "
                "For precise dietary advice or medical guidance, consult a qualified "
                "nutritionist or healthcare provider."
            )


            # -----------------------------
            # Raw GPT output for debugging
            # -----------------------------

            with st.expander("Raw GPT Output"):
                st.code(raw_model_output)

        except Exception as e:
            st.error(f"Something went wrong: {e}")