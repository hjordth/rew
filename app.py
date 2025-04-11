
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

# Page config – MUST be first Streamlit command
st.set_page_config(page_title="Mælaborð Suðurnesja", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("lidanargogn_sudurnes_gervi.csv")
    return df

df = load_data()

# Load logo
logo = Image.open("OIP.jpg")

# Custom color palette (example from logo style)
PRIMARY_COLOR = "#2D3A3F"  # deep grey-blue
df_palette = {
    'Líðan': '#2D3A3F',
    'Kvíði': '#5D6D74',
    'Einmanaleiki': '#99A8AC',
    'Skjástund': '#CCD4D6',
    'Tengsl við kennara': '#88999F',
    'Ánægja með skólann': '#A9B8BB'
}

# Sidebar filters
st.sidebar.image(logo, use_container_width=True)
st.sidebar.title("Valmöguleikar")
skolar = df['Skóli'].unique()
valinn_skoli = st.sidebar.selectbox("Veldu skóla", sorted(skolar))
valin_ar = st.sidebar.multiselect("Veldu ár", sorted(df['Ár'].unique()), default=sorted(df['Ár'].unique()))

# Optional background variables (now using selectbox/dropdown instead of multiselect)
if all(col in df.columns for col in ['Kyn', 'Bakgrunnur', 'Fjárhagsstaða', 'Bekkur']):
    kyn = st.sidebar.selectbox("Kyn", ['Allir'] + list(df['Kyn'].unique()))
    bakgrunnur = st.sidebar.selectbox("Bakgrunnur", ['Allir'] + list(df['Bakgrunnur'].unique()))
    fj = st.sidebar.selectbox("Fjárhagsstaða", ['Allir'] + list(df['Fjárhagsstaða'].unique()))
    bekking = st.sidebar.selectbox("Árganga", ['Allir'] + sorted(df['Bekkur'].unique()))
else:
    kyn = bakgrunnur = fj = bekking = None

# Filter data
filtered_df = df[(df['Skóli'] == valinn_skoli) & (df['Ár'].isin(valin_ar))]
if kyn and kyn != 'Allir':
    filtered_df = filtered_df[filtered_df['Kyn'] == kyn]
if bakgrunnur and bakgrunnur != 'Allir':
    filtered_df = filtered_df[filtered_df['Bakgrunnur'] == bakgrunnur]
if fj and fj != 'Allir':
    filtered_df = filtered_df[filtered_df['Fjárhagsstaða'] == fj]
if bekking and bekking != 'Allir':
    filtered_df = filtered_df[filtered_df['Bekkur'] == bekking]

st.image(logo, width=100)
st.title("Mælaborð um líðan barna á Suðurnesjum")
st.markdown(f"### Skóli: {valinn_skoli}")

# Show summary statistics
st.subheader("Meðaltal velferðarþátta")
try:
    meðaltöl = filtered_df.groupby(['Ár'])[["Líðan", "Kvíði", "Einmanaleiki", "Skjástund", "Tengsl við kennara", "Ánægja með skólann"]].mean().round(2)
    st.dataframe(meðaltöl)
except ValueError:
    st.warning("Engin gögn fundust fyrir valið. Vinsamlegast prófaðu aðra samsetningu af síum.")

# Top 3 strengths and challenges per school
st.subheader("Top 3 styrkleikar og áskoranir")
for school in df['Skóli'].unique():
    school_data = df[df['Skóli'] == school]
    strengths = school_data[['Líðan', 'Kvíði', 'Einmanaleiki', 'Skjástund', 'Tengsl við kennara', 'Ánægja með skólann']].mean().nlargest(3)
    challenges = school_data[['Líðan', 'Kvíði', 'Einmanaleiki', 'Skjástund', 'Tengsl við kennara', 'Ánægja með skólann']].mean().nsmallest(3)
    st.markdown(f"**{school}:**")
    st.markdown(f"  - **Styrkleikar**: {', '.join([f'{x}: {strengths[x]:.2f}' for x in strengths.index])}")
    st.markdown(f"  - **Áskoranir**: {', '.join([f'{x}: {challenges[x]:.2f}' for x in challenges.index])}")
    
# Samanburður milli skóla eða hópa
st.subheader("Samanburður milli skóla")
# Group by school and calculate means
comparison_data = df.groupby('Skóli')[["Líðan", "Kvíði", "Einmanaleiki", "Skjástund", "Tengsl við kennara", "Ánægja með skólann"]].mean()
st.dataframe(comparison_data)

# Plotting trendline comparison across schools
st.subheader("Þróun yfir ár")
valinn_thattur = st.selectbox("Veldu velferðarbreytu til að skoða", ['Líðan', 'Kvíði', 'Einmanaleiki', 'Skjástund', 'Tengsl við kennara', 'Ánægja með skólann'])

trend_data = df.groupby(['Ár', 'Skóli'])[['Líðan', 'Kvíði', 'Einmanaleiki', 'Skjástund', 'Tengsl við kennara', 'Ánægja með skólann']].mean().reset_index()
fig, ax = plt.subplots(figsize=(10, 6))
for school in trend_data['Skóli'].unique():
    school_data = trend_data[trend_data['Skóli'] == school]
    ax.plot(school_data['Ár'], school_data[valinn_thattur], label=school)

ax.set_xlabel("Ár")
ax.set_ylabel("Meðaltal")
ax.set_title(f"Þróun yfir ár fyrir {valinn_thattur}")
ax.legend()
st.pyplot(fig)

st.markdown("---")
st.caption("© Samband sveitarfélaga á Suðurnesjum – Mælaborð fyrir farsæld barna og ungmenna")
