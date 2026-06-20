import streamlit as st
import pandas as pd
import re

# ---------------- PAGE ----------------

st.set_page_config(
    page_title="AI Food Recommendation System",
    layout="wide"
)

st.title("🍲 AI Food Recommendation System")

st.write(
    "Enter ingredients separated by spaces"
)

# ---------------- LOAD DATA ----------------

@st.cache_data
def load_data():

    df = pd.read_csv(
        "cleaned_recipes.csv"
    )

    return df


df = load_data()

# ---------------- SHOW COLUMNS ----------------

st.write(
    "CSV Columns Found:"
)

st.write(
    df.columns.tolist()
)

# ---------------- NORMALIZE ----------------

synonyms = {

    "aloo":"potato",

    "batata":"potato",

    "pyaz":"onion",

    "kanda":"onion",

    "tamatar":"tomato",

    "chawal":"rice",

    "tandul":"rice",

    "mirchi":"green chilli"

}


def normalize(text):

    words = text.lower().split()

    result = []

    for w in words:

        result.append(

            synonyms.get(

                w,

                w

            )

        )

    return " ".join(result)


# ---------------- RECOMMEND ----------------

def recommend(user_input):

    ingredient_col = None

    possible_columns = [

        "Cleaned-Ingredients",

        "TranslatedIngredients",

        "ingredients",

        "Ingredients"

    ]

    for col in possible_columns:

        if col in df.columns:

            ingredient_col = col

            break

    if ingredient_col is None:

        st.error(

            "Ingredient column not found."

        )

        return pd.DataFrame()

    user_words = set(

        user_input.lower().split()

    )

    scores = []

    for _, row in df.iterrows():

        recipe_words = set(

            str(

                row[ingredient_col]

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

    temp = df.copy()

    temp["score"] = scores

    temp = temp.sort_values(

        by="score",

        ascending=False

    )

    return temp.head(10)


# ---------------- INPUT ----------------

user_input = st.text_input(

    "Ingredients",

    placeholder="rice tomato potato"

)

if st.button(

    "Get Recipes"

):

    if user_input:

        user_input = normalize(

            user_input

        )

        st.write(

            "Input:",

            user_input

        )

        results = recommend(

            user_input

        )

        if len(results) > 0:

            st.write(

                results

            )

    else:

        st.warning(

            "Please enter ingredients."

        )
