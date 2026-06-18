# AI Nutrition Coach

## Overview
AI Nutrition Coach is a Streamlit web app that uses GPT vision to identify food items from meal images, estimates portion sizes, retrieves nutrition data from USDA FoodData Central, calculates calories/macros, and recommends foods based on the user's remaining daily targets.

## Features
- Food image upload
- GPT-powered food recognition
- Portion size estimation
- USDA nutrition database integration
- Local nutrition fallback dataset
- Calories, protein, carbs, and fat calculation
- Remaining macro target tracking
- Food recommendation engine
- Streamlit dashboard UI

## Tech Stack
Python, Streamlit, OpenAI API, USDA FoodData Central API, dotenv, requests

## Limitations
Food recognition and portion estimation are approximate. Nutrition values may vary based on preparation method, portion size, and USDA match quality.

## Future Improvements
- User accounts and daily food logging
- Barcode scanning
- Better portion estimation
- Weekly nutrition dashboard
- Persistent cache with SQLite
- Meal plan generation