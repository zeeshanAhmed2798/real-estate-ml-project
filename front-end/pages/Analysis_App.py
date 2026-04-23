import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(page_title="Analytics", layout="wide")

st.title("📊 Analytics")

# -------------------- LOAD DATA --------------------
@st.cache_data
def load_map_data():
    df = pd.read_csv("flats_df_with_coords_v2.csv")
    df.columns = df.columns.str.strip().str.lower()
    return df

@st.cache_data
def load_wc_data():
    df = pd.read_csv("flats_df_with_coords.csv")
    df.columns = df.columns.str.strip().str.lower()
    return df

df_map = load_map_data()   # 👉 for map
df_wc = load_wc_data()     # 👉 for wordcloud

# -------------------- MAP --------------------
def plot_map(df):
    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        color="price",
        size="area_sqft",   # this exists in v2
        hover_name="society",
        hover_data=["price", "bedrooms", "area_sqft"],
        zoom=10,
        height=500,
        color_continuous_scale="Plasma"
    )

    fig.update_layout(
        mapbox_style="carto-darkmatter",
        mapbox=dict(
            center={"lat": 31.5204, "lon": 74.3587},
            zoom=10
        ),
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
    )

    return fig


# -------------------- WORDCLOUD --------------------
def generate_wordcloud(data):

    clean_features = []

    for row in data['features'].dropna():
        parts = str(row).split('|')

        row_features = set()

        for p in parts:
            p = p.strip().lower()

            if ':' in p:
                continue
            if 'nearby' in p:
                continue
            if 'distance' in p:
                continue
            if 'building' in p:
                continue
            if 'other' in p:
                continue

            row_features.add(p)

        clean_features.extend(row_features)

    clean_text = " ".join(clean_features)

    wc = WordCloud(
        width=800,
        height=800,
        background_color='white',
        colormap='viridis',
        collocations=False
    ).generate(clean_text)

    return wc


# -------------------- MAP DISPLAY --------------------
st.subheader("📍 Property Map")
fig = plot_map(df_map)
st.plotly_chart(fig, use_container_width=True)

# -------------------- WORDCLOUD --------------------
st.subheader("☁️ Features WordCloud")

societies = sorted(df_wc['society'].dropna().unique().tolist())
selected_society = st.selectbox("Select Society", ["All"] + societies)

# filter for wordcloud
if selected_society != "All":
    filtered_df = df_wc[df_wc['society'] == selected_society]
else:
    filtered_df = df_wc

# display
if 'features' in df_wc.columns:
    wc = generate_wordcloud(filtered_df)

    fig_wc, ax = plt.subplots(figsize=(10,6))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')

    st.pyplot(fig_wc)
else:
    st.warning("⚠️ 'features' column not found in dataset")
    
    
    
# -------------------- SCATTER PLOT --------------------
st.subheader("📈 Area vs Price (Scatter Plot)")

def plot_scatter(df):

    # ensure numeric
    df['area'] = pd.to_numeric(df['area'], errors='coerce')
    df['price'] = pd.to_numeric(df['price'], errors='coerce')

    df = df.dropna(subset=['area', 'price'])

    fig = px.scatter(
        df,
        x="area",
        y="price",
        color="society",
        size="bedrooms",
        hover_data=["bedrooms", "baths"],
        title="Area vs Price"
    )

    fig.update_layout(
        xaxis_title="Area",
        yaxis_title="Price",
        height=500
    )

    return fig


# apply same filter as wordcloud
scatter_fig = plot_scatter(df_map)

st.plotly_chart(scatter_fig, use_container_width=True)


st.subheader("Distribution of Bedrooms")

bedroom_counts = df_map['bedrooms'].value_counts().reset_index()
bedroom_counts.columns = ['bedrooms', 'count']

fig = px.pie(
    bedroom_counts,
    names='bedrooms',
    values='count'
    # title="Distribution of Bedrooms"
)

st.plotly_chart(fig, use_container_width=True)


# -------------------- BOXPLOT --------------------
st.subheader("📦 BHK Price Range (Boxplot)")

def plot_box(df):

    # clean data
    df['bedrooms'] = pd.to_numeric(df['bedrooms'], errors='coerce')
    df['price'] = pd.to_numeric(df['price'], errors='coerce')

    df = df.dropna(subset=['bedrooms', 'price'])

    # limit to reasonable BHK
    df = df[df['bedrooms'] <= 4]

    fig = px.box(
        df,
        x="bedrooms",
        y="price",
        color="bedrooms",
        title="BHK Price Range"
    )

    fig.update_layout(
        xaxis_title="Bedrooms (BHK)",
        yaxis_title="Price",
        height=500
    )

    return fig


# 👉 use map dataset
box_fig = plot_box(df_map)

st.plotly_chart(box_fig, use_container_width=True)


# -------------------- PRICE vs AREA (TREND) --------------------
st.subheader("📉 Price vs Area Trend")

def plot_trend(df):

    # clean
    df['area_sqft'] = pd.to_numeric(df['area_sqft'], errors='coerce')
    df['price'] = pd.to_numeric(df['price'], errors='coerce')

    df = df.dropna(subset=['area_sqft', 'price'])
    df = df[df['area_sqft'] > 0]

    fig = px.scatter(
        df,
        x="area_sqft",
        y="price",
        trendline="ols",   # 🔥 regression line
        opacity=0.5,
        title="Price vs Area (with Trend)"
    )

    fig.update_layout(
        xaxis_title="Area (sqft)",
        yaxis_title="Price",
        height=500
    )

    return fig


trend_fig = plot_trend(df_map)

st.plotly_chart(trend_fig, use_container_width=True)


# -------------------- PRICE PER SQFT --------------------
st.subheader("💰 Price per Sqft Analysis")

def plot_price_per_sqft(df):

    # clean
    df['area_sqft'] = pd.to_numeric(df['area_sqft'], errors='coerce')
    df['price'] = pd.to_numeric(df['price'], errors='coerce')

    df = df.dropna(subset=['area_sqft', 'price'])
    df = df[df['area_sqft'] > 0]

    # create metric
    df['price_per_sqft'] = df['price'] / df['area_sqft']

    fig = px.box(
        df,
        x="society",
        y="price_per_sqft",
        title="Price per Sqft by Society"
    )

    fig.update_layout(
        xaxis_title="Society",
        yaxis_title="Price per Sqft",
        height=500
    )

    return fig


fig_pps = plot_price_per_sqft(df_map)

st.plotly_chart(fig_pps, use_container_width=True)



# -------------------- TOP SOCIETIES --------------------
st.subheader("🏙 Top Societies by Average Price")

def plot_top_societies(df):

    # clean
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df = df.dropna(subset=['price'])

    # average price per society
    avg_price = (
        df.groupby('society')['price']
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig = px.bar(
        avg_price,
        x="society",
        y="price",
        title="Top 10 Most Expensive Societies",
        text_auto=True
    )

    fig.update_layout(
        xaxis_title="Society",
        yaxis_title="Average Price",
        height=500
    )

    return fig


fig_top = plot_top_societies(df_map)

st.plotly_chart(fig_top, use_container_width=True)


# -------------------- HEATMAP (DENSITY) --------------------
st.subheader("🔥 Property Density (Area vs Price)")

def plot_density(df):

    # clean
    df['area_sqft'] = pd.to_numeric(df['area_sqft'], errors='coerce')
    df['price'] = pd.to_numeric(df['price'], errors='coerce')

    df = df.dropna(subset=['area_sqft', 'price'])
    df = df[df['area_sqft'] > 0]

    fig = px.density_heatmap(
        df,
        x="area_sqft",
        y="price",
        nbinsx=40,
        nbinsy=40,
        color_continuous_scale="Viridis"
    )

    fig.update_layout(
        xaxis_title="Area (sqft)",
        yaxis_title="Price",
        height=500
    )

    return fig


heatmap_fig = plot_density(df_map)

st.plotly_chart(heatmap_fig, use_container_width=True)

# -------------------- AFFORDABILITY --------------------
st.subheader("🏠 Affordability (Price per Bedroom)")

def plot_affordability(df):

    # clean
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['bedrooms'] = pd.to_numeric(df['bedrooms'], errors='coerce')

    df = df.dropna(subset=['price', 'bedrooms'])
    df = df[df['bedrooms'] > 0]

    # metric
    df['price_per_bedroom'] = df['price'] / df['bedrooms']

    # group by society
    avg_afford = (
        df.groupby('society')['price_per_bedroom']
        .mean()
        .sort_values()
        .head(10)   # most affordable
        .reset_index()
    )

    fig = px.bar(
        avg_afford,
        x="society",
        y="price_per_bedroom",
        title="Most Affordable Societies (per Bedroom)",
        text_auto=True
    )

    fig.update_layout(
        xaxis_title="Society",
        yaxis_title="Price per Bedroom",
        height=500
    )

    return fig


fig_afford = plot_affordability(df_map)
st.plotly_chart(fig_afford, use_container_width=True)