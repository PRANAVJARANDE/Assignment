import pandas as pd
import random
import numpy as np

def generate_mock_data():
    """Generates mock vehicle registration data for a dashboard."""
    mock_data = []
    manufacturers = {
        '2W': ['HERO MOTOCORP LTD', 'HONDA MOTORCYCLE & SCOOTER INDIA (P) LTD', 'TVS MOTOR COMPANY LTD', 'BAJAJ AUTO LTD'],
        '3W': ['BAJAJ AUTO LTD', 'PIAGGIO VEHICLES PVT. LTD.', 'MAHINDRA & MAHINDRA LTD'],
        '4W': ['MARUTI SUZUKI INDIA LTD', 'HYUNDAI MOTOR INDIA LTD', 'TATA MOTORS LTD', 'MAHINDRA & MAHINDRA LTD']
    }
    base_registrations = {
        '2W': 1500000, '3W': 300000, '4W': 800000
    }

    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    years = ['2023', '2024']

    for year in years:
        for quarter in quarters:
            for cat, manuf_list in manufacturers.items():
                for manuf in manuf_list:
                    random_factor = random.uniform(0.8, 1.2)
                    seasonal_factor = 1.0
                    if quarter == 'Q4':
                        seasonal_factor = 1.15
                    elif quarter == 'Q2':
                        seasonal_factor = 0.95
                    
                    year_growth_factor = 1.05 if year == '2024' else 1.0
                    
                    count = int(base_registrations[cat] / len(manuf_list) * random_factor * seasonal_factor * year_growth_factor)
                    
                    mock_data.append({
                        'year': year,
                        'quarter': quarter,
                        'category': cat,
                        'manufacturer': manuf,
                        'registrations': count
                    })

    return mock_data

def calculate_growth_metrics(df, year, category, manufacturer):
    """
    Calculates key growth metrics (total, YoY, QoQ) for the dashboard.
    """
    df['year'] = df['year'].astype(str)
    
    # Filter data
    current_year_df = df[df['year'] == year].copy()
    previous_year_df = df[df['year'] == str(int(year) - 1)].copy()

    if category != 'All':
        current_year_df = current_year_df[current_year_df['category'] == category]
        previous_year_df = previous_year_df[previous_year_df['category'] == category]
    
    if manufacturer != 'All':
        current_year_df = current_year_df[current_year_df['manufacturer'] == manufacturer]
        previous_year_df = previous_year_df[previous_year_df['manufacturer'] == manufacturer]

    # Calculate total registrations
    current_total = current_year_df['registrations'].sum()
    previous_total = previous_year_df['registrations'].sum()
    
    # Calculate YoY Growth
    yoy_growth = 0
    if previous_total > 0:
        yoy_growth = ((current_total - previous_total) / previous_total) * 100
        yoy_growth = f"{yoy_growth:.1f}%"
    else:
        yoy_growth = "N/A"
        
    # Calculate QoQ Growth
    qoq_growth = 0
    q4_current_year_df = current_year_df[current_year_df['quarter'] == 'Q4']
    q3_current_year_df = current_year_df[current_year_df['quarter'] == 'Q3']

    q4_total = q4_current_year_df['registrations'].sum()
    q3_total = q3_current_year_df['registrations'].sum()
    
    if q3_total > 0:
        qoq_growth = ((q4_total - q3_total) / q3_total) * 100
        qoq_growth = f"{qoq_growth:.1f}%"
    else:
        qoq_growth = "N/A"

    return {
        'total_registrations': current_total,
        'yoy_growth': yoy_growth,
        'qoq_growth': qoq_growth
    }

def get_manufacturer_data(df, year, category):
    """
    Prepares a DataFrame for manufacturer-specific charts.
    """
    df['year'] = df['year'].astype(str)
    
    manuf_list = df[df['category'] == category]['manufacturer'].unique()
    
    manuf_data = []
    for manuf in manuf_list:
        current_total = df[(df['year'] == year) & (df['category'] == category) & (df['manufacturer'] == manuf)]['registrations'].sum()
        prev_total = df[(df['year'] == str(int(year) - 1)) & (df['category'] == category) & (df['manufacturer'] == manuf)]['registrations'].sum()
        
        yoy_growth = 0
        if prev_total > 0:
            yoy_growth = ((current_total - prev_total) / prev_total) * 100
            
        current_q4_total = df[(df['year'] == year) & (df['category'] == category) & (df['manufacturer'] == manuf) & (df['quarter'] == 'Q4')]['registrations'].sum()
        current_q3_total = df[(df['year'] == year) & (df['category'] == category) & (df['manufacturer'] == manuf) & (df['quarter'] == 'Q3')]['registrations'].sum()
        
        qoq_growth = 0
        if current_q3_total > 0:
            qoq_growth = ((current_q4_total - current_q3_total) / current_q3_total) * 100

        manuf_data.append({
            'manufacturer': manuf,
            'yoy_growth': yoy_growth,
            'qoq_growth': qoq_growth
        })
        
    return pd.DataFrame(manuf_data)
