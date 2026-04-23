# -------------------- IMPORTS --------------------
import streamlit as st
import pandas as pd
import numpy as np
import joblib

st.set_page_config(page_title="Price Predictor", layout="wide")

st.title("🏠 Flats Price Predictor")

# -------------------- LOAD DATA --------------------
df = joblib.load('flats_df.pkl')
model = joblib.load('flats_final_pipeline.pkl')

# -------------------- SHOW DATA --------------------
# st.dataframe(df.head())

st.header("Enter your inputs")

# -------------------- INPUTS --------------------
df['bedrooms'] = df['bedrooms'].round()
bedrooms = float(st.selectbox('Bedrooms', sorted(df['bedrooms'].unique().tolist())))
baths = float(st.selectbox('Bathrooms', sorted(df['baths'].unique().tolist())))
floors = float(st.selectbox('Floors in Building', sorted(df['floors_in_building'].unique().tolist())))

area_sqft = float(st.number_input('Area (sqft)', min_value=100.0))

servant_quarters = float(st.selectbox('Servant Quarters', [0.0, 1.0]))
kitchens = float(st.selectbox('Kitchens', sorted(df['kitchens'].unique().tolist())))
store_rooms = float(st.selectbox('Store Rooms', sorted(df['store_rooms'].unique().tolist())))
drawing_room = int(st.selectbox('Drawing Room', [0, 1]))

agePossession = st.selectbox(
    'Property Age',
    sorted(df['agePossession'].unique().tolist())
)

luxury_category = st.selectbox(
    'Luxury Category',
    sorted(df['luxury_category'].unique().tolist())
)

floor_category = st.selectbox(
    'Floor Category',
    sorted(df['floor_category'].unique().tolist())
)

furnishing_type = st.selectbox(
    'Furnishing Type',
    sorted(df['furnishing_type'].unique().tolist())
)

# -------------------- PREDICT --------------------
if st.button("Predict Price"):

    data = [[
        bedrooms,
        baths,
        floors,
        area_sqft,
        servant_quarters,
        kitchens,
        store_rooms,
        drawing_room,
        agePossession,
        luxury_category,
        floor_category,
        furnishing_type
    ]]

    columns = [
        'bedrooms',
        'baths',
        'floors_in_building',
        'area_sqft',
        'servant_quarters',
        'kitchens',
        'store_rooms',
        'drawing_room',
        'agePossession',
        'luxury_category',
        'floor_category',
        'furnishing_type'
    ]

    one_df = pd.DataFrame(data, columns=columns)

    # prediction (log → actual)
    pred = model.predict(one_df)
    pred = np.expm1(pred)[0]

    # range (optional)
    low = pred - 0.22
    high = pred + 0.22

    # st.success(f"Estimated Price: {round(pred, 2)} Crore 💰")
    st.info(f"Range: {round(low,2)} Cr - {round(high,2)} Cr")