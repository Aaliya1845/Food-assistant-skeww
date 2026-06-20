import streamlit as st
import pandas as pd
import numpy as np
from gtts import gTTS
import re
import os

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="AI Food Assistant",
    layout="wide"
)

# ---------------- LOAD DATA ----------------

@st.cache_data
def load_data():

    df = pd.read_csv("cleaned_recipes.csv")

    nutrition_df = pd.read_csv("food.csv.zip")

    nutrition_df = nutrition_df[
        [
            "Description",
            "Data.Kilocalories",
            "Data.Protein",
            "Data.Carbohydrate",
            "Data.Fat.Total Lipid"
        ]
    ]

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


df, nutrition_df = load_data()

# ---------------- SYNONYMS ----------------

synonyms = {

    "aloo": "potato",

    "batata": "potato",

    "pyaz": "onion",

    "kanda": "onion",

    "tamatar": "tomato",

    "chawal": "rice",

    "tandul": "rice",

    "tandool": "rice",

    "capsicum": "bell pepper",

    "shimla": "bell pepper",

    "shimla mirch": "bell pepper",

    "hari mirch": "green chilli",

    "mirchi": "green chilli"

}

# ---------------- TRANSLATE ----------------

def translate_to_english(text):

    return text



# ---------------- NORMALIZE ----------------

def normalize_ingredients(text):

    words = text.lower().split()

    result = []

    for word in words:

        result.append(

            synonyms.get(word, word)

        )

    return " ".join(result)


# ---------------- SHORT STEPS ----------------

def short_steps(text):

    text = str(text)

    steps = text.split(".")

    short = []

    for i in range(

        min(4, len(steps))

    ):

        if steps[i].strip() != "":

            short.append(

                f"{i+1}. {steps[i].strip()}"

            )

    return "\n".join(short)


# ---------------- INGREDIENT ANALYSIS ----------------

def ingredient_analysis(

        user_input,

        recipe_ingredients

):

    user_set = set(

        re.findall(

            r'\w+',

            user_input.lower()

        )

    )

    recipe_set = set(

        re.findall(

            r'\w+',

            str(recipe_ingredients).lower()

        )

    )

    matched = user_set.intersection(

        recipe_set

    )

    missing = recipe_set - user_set

    return matched, missing


# ---------------- NUTRITION ----------------

def nutrition_estimate(

        user_input,

        nutrition_df

):

    ingredients = user_input.lower().split()

    total_cal = 0

    total_protein = 0

    total_carbs = 0

    total_fat = 0

    found = []

    for ing in ingredients:

        match = nutrition_df[

            nutrition_df["food_name"]

            .str.contains(

                ing,

                case=False,

                na=False

            )

        ]

        if len(match) > 0:

            row = match.iloc[0]

            found.append(ing)

            total_cal += row["calories"]

            total_protein += row["protein"]

            total_carbs += row["carbs"]

            total_fat += row["fat"]

    st.write(

        "Matched Foods:",

        ", ".join(found)

    )

    st.write(

        f"🔥 Calories: {round(total_cal,2)}"

    )

    st.write(

        f"💪 Protein: {round(total_protein,2)} g"

    )

    st.write(

        f"🍞 Carbs: {round(total_carbs,2)} g"

    )

    st.write(

        f"🥑 Fat: {round(total_fat,2)} g"

    )


# ---------------- RECOMMEND ----------------

def recommend(user_input):

    user_words = set(

        user_input.lower().split()

    )

    scores = []

    for _, row in df.iterrows():

        recipe_words = set(

            str(

                row["Cleaned-Ingredients"]

            )

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


# ---------------- UI ----------------

st.title("🍲 AI Food Recommendation System")

st.write(

    "Enter ingredients in English, Hindi or Marathi."

)

user_input = st.text_input(

    "Ingredients",

    placeholder="rice tomato onion"

)

if st.button("Get Recipes"):

    if user_input:

        translated = translate_to_english(

            user_input

        )

        normalized = normalize_ingredients(

            translated

        )

        st.subheader(

            f"🌐 Processed Input: {normalized}"

        )

        st.write("---")

        results = recommend(

            normalized

        )

        for i, row in results.iterrows():

            st.markdown(

                f"### 🍲 {row['TranslatedRecipeName']}"

            )

            st.write(

                f"🍛 Cuisine: {row['Cuisine']}"

            )

            st.write(

                f"⏱ Time: {row['TotalTimeInMins']} mins"

            )

            matched, missing = ingredient_analysis(

                normalized,

                row["Cleaned-Ingredients"]

            )

            st.write(

                "✅ You Have:",

                ", ".join(list(matched))

            )

            st.write(

                "❌ Missing:",

                ", ".join(

                    list(missing)[:6]

                )

            )

            st.write("👨‍🍳 Short Steps:")

            st.text(

                short_steps(

                    row["TranslatedInstructions"]

                )

            )

            st.write(

                f"📊 Match Score: {row['score']}"

            )

            if pd.notna(

                row["image-url"]

            ):

                try:

                    st.image(

                        row["image-url"],

                        caption=row["TranslatedRecipeName"],

                        width=300

                    )

                except:

                    st.write(

                        "Image not available"

                    )

            tts_text = (

                f"You can make "

                f"{row['TranslatedRecipeName']}"

            )

            tts = gTTS(

                text=tts_text,

                lang='en'

            )

            filename = f"recipe_{i}.mp3"

            tts.save(filename)

            st.audio(filename)

            if os.path.exists(filename):

                os.remove(filename)

            st.subheader(

                "🔥 Estimated Nutrition"

            )

            nutrition_estimate(

                normalized,

                nutrition_df

            )

            st.write("---")

    else:

        st.warning(

            "Please enter ingredients."

                )
