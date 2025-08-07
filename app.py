import streamlit as st
import pandas as pd
import plotly.express as px
from data_processing import generate_mock_data, calculate_growth_metrics, get_manufacturer_data

# Set page configuration
st.set_page_config(
    page_title="Investor's Vehicle Registration Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    body {
        font-family: 'Poppins', sans-serif;
        background-color: #f0f2f6; /* Very light gray background */
    }

    .stApp {
        background-color: #f0f2f6;
    }

    .st-emotion-cache-1d391kg { /* Main container */
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    .st-emotion-cache-gh2j61 { /* Sidebar */
        background-color: #ffffff;
        padding-top: 2rem;
    }

    h1, h2, h3 {
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        color: #1e3a8a; /* Dark blue for headings */
    }

    .st-emotion-cache-6q9r41 { /* Main container */
        padding-top: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        padding-bottom: 2rem;
    }

    .st-emotion-cache-1629p8f { /* Metric card */
        background-color: #ffffff;
        border-left: 5px solid #10b981; /* Green accent */
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    }
    .st-emotion-cache-1wivf26 { /* Metric value */
        font-size: 2rem;
        font-weight: 700;
        color: #0b1c49;
    }
    .st-emotion-cache-5rimf7 { /* Metric label */
        font-size: 1rem;
        color: #6b7280;
    }
    .st-emotion-cache-1g8360 { /* Metric delta */
        font-size: 1.25rem;
        font-weight: 600;
        color: #16a34a; /* Green for positive growth */
    }
    .st-emotion-cache-s2s9y { /* Metric delta down */
        color: #dc2626; /* Red for negative growth */
    }

    .st-emotion-cache-1h50xni { /* Divider */
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
    }

    .st-emotion-cache-1r650k0 { /* Buttons */
        border-radius: 0.5rem;
        border-color: #1e3a8a;
        color: #1e3a8a;
    }
    </style>
""", unsafe_allow_html=True)


# Load data (WITHOUT CACHING for demonstration purposes)
def load_data():
    return generate_mock_data()

# Data loading and processing
raw_data = load_data()
df = pd.DataFrame(raw_data)

# Sidebar for filters
st.sidebar.header("Global Filters")

year = st.sidebar.selectbox("Select Year", sorted(df['year'].unique(), reverse=True))

vehicle_category = st.sidebar.selectbox("Select Vehicle Category", ['All'] + sorted(df['category'].unique()))

manufacturers_for_category = sorted(df[df['category'] == vehicle_category]['manufacturer'].unique()) if vehicle_category != 'All' else []
manufacturer = st.sidebar.selectbox("Select Manufacturer", ['All'] + manufacturers_for_category)

# Main dashboard title and intro
st.title("Investor's Vehicle Registration Dashboard ")
st.markdown("A quick overview of Indian vehicle registration data with key growth metrics for investor analysis.")

# --- Key Performance Indicators (KPIs) ---
st.header("Key Market Metrics")

kpi_data = calculate_growth_metrics(df, year, vehicle_category, manufacturer)
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Total Registrations", value=f"{kpi_data['total_registrations']:,}")
with col2:
    st.metric(label="Year-over-Year Growth", value=kpi_data['yoy_growth'], delta=kpi_data['yoy_growth'])
with col3:
    st.metric(label="Quarter-over-Quarter Growth", value=kpi_data['qoq_growth'], delta=kpi_data['qoq_growth'])

st.divider()

# --- Market Overview Trends ---
st.header("Market Registration Trends")
st.markdown("Analyze the overall market trajectory across different vehicle categories.")

if vehicle_category == 'All':
    market_df = df[df['year'] == year].groupby(['quarter', 'category'])['registrations'].sum().reset_index()
    fig = px.line(
        market_df,
        x="quarter",
        y="registrations",
        color="category",
        title=f"Quarterly Registrations in {year} by Category",
        markers=True,
        labels={"registrations": "Registrations", "quarter": "Quarter", "category": "Vehicle Category"},
        height=500
    )
    # Customize Plotly colors to match the theme
    fig.update_layout(
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        font_family='Poppins',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#e5e7eb'),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        title_font_size=20,
        title_x=0.5
    )
    fig.update_traces(line=dict(width=3))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Select 'All' in Vehicle Category to view market trends.")

st.divider()

# --- Manufacturer Deep-Dive ---
st.header("Manufacturer Performance Analysis")
st.markdown("Compare the performance of individual manufacturers.")

if vehicle_category != 'All':
    manuf_df = get_manufacturer_data(df, year, vehicle_category)
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        fig_yoy = px.bar(
            manuf_df.sort_values('yoy_growth'),
            x="yoy_growth",
            y="manufacturer",
            title=f"YoY Growth ({year}) - {vehicle_category}",
            orientation='h',
            labels={"yoy_growth": "YoY Growth (%)", "manufacturer": "Manufacturer"},
            height=400,
            color='yoy_growth',
            color_continuous_scale=['red', 'green'],
            color_continuous_midpoint=0
        )
        fig_yoy.update_layout(
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            font_family='Poppins',
            xaxis=dict(title_text='YoY Growth (%)', showgrid=True, gridcolor='#e5e7eb'),
            yaxis=dict(title_text=''),
            title_font_size=18,
            title_x=0.5,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_yoy, use_container_width=True)
        
    with col_chart2:
        fig_qoq = px.bar(
            manuf_df.sort_values('qoq_growth'),
            x="qoq_growth",
            y="manufacturer",
            title=f"QoQ Growth (Q4 vs Q3 {year}) - {vehicle_category}",
            orientation='h',
            labels={"qoq_growth": "QoQ Growth (%)", "manufacturer": "Manufacturer"},
            height=400,
            color='qoq_growth',
            color_continuous_scale=['red', 'green'],
            color_continuous_midpoint=0
        )
        fig_qoq.update_layout(
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            font_family='Poppins',
            xaxis=dict(title_text='QoQ Growth (%)', showgrid=True, gridcolor='#e5e7eb'),
            yaxis=dict(title_text=''),
            title_font_size=18,
            title_x=0.5,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_qoq, use_container_width=True)
else:
    st.warning("Please select a specific Vehicle Category to view Manufacturer data.")

st.divider()

# --- Bonus Investor Insight ---
st.header("Bonus Insight: The EV Inflection Point")
st.markdown(
    """
    A key surprising trend is the accelerated adoption rate of Electric Vehicles (EVs) in new vehicle sales,
    despite their low overall share in the total registered fleet. This signals a critical shift in consumer
    preference and presents significant growth potential for investments in EV manufacturing and infrastructure.
    """
)
