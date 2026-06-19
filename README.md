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

##Installation Instructions
#1. Clone the Repository
git clone https://github.com/Sane1204/AI_NUTRITION_COACH.git
cd AI_NUTRITION_COACH
#2. Create a Virtual Environment
python -m venv .venv
#3. Activate the Virtual Environment

##For Windows:

.venv\Scripts\activate

##For Mac/Linux:

source .venv/bin/activate
#4. Install Required Packages
pip install -r requirements.txt
#5. Set Up Environment Variables

Create a .env file in the project root folder.

OPENAI_API_KEY=your_openai_api_key_here
USDA_API_KEY=your_usda_api_key_here

You can use .env.example as a reference.

#6. Run the Streamlit App
streamlit run interface.py
#7. Open the App

After running the command, Streamlit will open the app in your browser.

If it does not open automatically, go to:

http://localhost:8501
