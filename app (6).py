import streamlit as st
import numpy as np
import pandas as pd

from sklearn.metrics.pairwise import cosine_similarity
from deep_translator import GoogleTranslator
import re
from gtts import gTTS
import os

# --- Data Loading and Model Initialization ---
@st.cache_resource
def load_model_and_data():

    df = pd.read_csv("cleaned_recipes.csv")

    nutrition_df = pd.read_csv("food.csv.zip")

    nutrition_df = nutrition_df[[
        "Description",
        "Data.Kilocalories",
        "Data.Protein",
        "Data.Carbohydrate",
        "Data.Fat.Total Lipid"
    ]]

    nutrition_df.columns = [
        "food_name",
        "calories",
        "protein",
        "carbs",
        "fat"
    ]

    nutrition_df["food_name"] = (
        nutrition_df["food_name"]
        .astype(str)
        .str.lower()
        .str.replace(",", " ")
    )

    return df, nutrition_df


df, nutrition_df = load_model_and_data()

# --- Helper Functions ---

# Synonyms for ingredient normalization
synonyms = {
    "aloo":"potato", "batata":"potato", # Potato
    "pyaz":"onion", "kanda":"onion",     # Onion
    "tamatar":"tomato",                  # Tomato
    "chawal":"rice", "tandul":"rice", "tandool":"rice", # Rice
    "capsicum":"bell pepper", "shimla":"bell pepper", "shimla mirch":"bell pepper", # Bell Pepper
    "hari mirch":"green chilli", "mirchi":"green chilli" # Green Chilli
}

def translate_to_english(text):
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(text)
        return translated
    except:
        return text

def normalize_ingredients(text):
    text = text.lower()
    words = text.split()
    result = []
    for word in words:
        if word in synonyms:
            result.append(synonyms[word])
        else:
            result.append(word)
    return " ".join(result)

def short_steps(text):
    text = str(text)
    steps = text.split(".")
    short = []
    for i in range(min(4, len(steps))):
        if steps[i].strip() != "":
            short.append(f"{i+1}. {steps[i].strip()}")
    return "\n".join(short)

def ingredient_analysis(user_input, recipe_ingredients):
    user_set = set(re.findall(r'\\w+', user_input.lower()))
    recipe_set = set(re.findall(r'\\w+', str(recipe_ingredients).lower()))
    matched = user_set.intersection(recipe_set)
    missing = recipe_set - user_set
    return matched, missing

def nutrition_estimate(user_input_ingredients, nutrition_df):
    ingredients = user_input_ingredients.lower().split() # Assuming user_input_ingredients is already normalized/translated
    total_cal = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    found = []

    for ing in ingredients:
        match = nutrition_df[nutrition_df["food_name"].str.contains(ing, case=False, na=False)]
        if len(match) > 0:
            row = match.iloc[0]
            found.append(ing)
            total_cal += row["calories"]
            total_protein += row["protein"]
            total_carbs += row["carbs"]
            total_fat += row["fat"]

    st.write(f"Matched Foods: {', '.join(found)}")
    st.write(f"🔥 Calories: {round(total_cal, 2)}")
    st.write(f"💪 Protein: {round(total_protein, 2)} g")
    st.write(f"🍞 Carbs: {round(total_carbs, 2)} g")
    st.write(f"🥑 Fat: {round(total_fat, 2)} 
    
    def recommend(user_input):

    user_words = set(
        user_input.lower().split()
    )

    scores = []

    for _, row in df.iterrows():

        recipe_words = set(
            str(row["Cleaned-Ingredients"])
            .lower()
            .replace(",", " ")
            .split()
        )

        score = len(
            user_words.intersection(
                recipe_words
            )
        )

        scores.append(score)

    temp_df = df.copy()

    temp_df["score"] = scores

    temp_df = temp_df.sort_values(
        by="score",
        ascending=False
    )

    return temp_df.head(10)

# --- Streamlit Application Logic ---
st.set_page_config(page_title="AI Food Assistant", layout="wide")

st.title("🍲 AI Food Recommendation System")
st.markdown("Enter ingredients in English, Hindi, or Marathi.")

user_input = st.text_input("Ingredients", placeholder="e.g., rice tomato onion")

if st.button("Get Recipes"):
    if user_input:
        translated_input = translate_to_english(user_input)
        normalized_input = normalize_ingredients(translated_input)

        st.subheader(f"🌐 Processed Input: {normalized_input}")
        st.write("---")

        results = recommend(normalized_input)

        for i, row in results.iterrows():
            st.markdown(f"### 🍲 {row['recipe_name']}")
            st.write(f"🍛 Cuisine: {row['cuisine']}")
            st.write(f"⏱ Cooking Time: {row['TotalTimeInMins']} minutes")

            matched, missing = ingredient_analysis(normalized_input, row["ingredients"])
            st.write(f"✅ You Have: {', '.join(list(matched))}")
            st.write(f"❌ Missing: {', '.join(list(missing)[:6])}") # Limit missing to 6 for display

            st.write("👨‍🍳 Short Steps:")
            st.markdown(short_steps(row["instructions"]))

            st.write(f"📊 Match Score: {round(row['score'], 3)}")

            st.write("🖼 Food Image:")
            try:
                st.image(row["image-url"], caption=row["recipe_name"], width=300)
            except Exception as e:
                st.write(f"Image not available or failed to load: {e}")

            st.write("🔊 Listen to the recipe name:")
            tts_text = f"You can make {row['recipe_name']}."
            tts = gTTS(text=tts_text, lang='en')
            tts_filename = f"recipe_{i}.mp3"
            tts.save(tts_filename)
            st.audio(tts_filename)

            st.write("---")

            st.subheader("🔥 Estimated Nutrition:")
            nutrition_estimate(normalized_input, nutrition_df)
            st.write("---")

            # Clean up generated audio files to prevent accumulation
            if os.path.exists(tts_filename):
                os.remove(tts_filename)

    else:
        st.warning("Please enter some ingredients to get recommendations.")
