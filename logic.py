# logic.py

import pandas as pd
import numpy as np
import hashlib

def hash_password(password):
    """Hashes the password using SHA-256 for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def calculate_bmi(height, weight):
    """Calculates BMI and returns the value and its category."""
    if not isinstance(height, (int, float)) or not isinstance(weight, (int, float)) or height <= 0:
        return "0.0", "N/A"
    
    bmi = weight / ((height / 100) ** 2)
    
    if bmi < 18.5: category = "Underweight"
    elif 18.5 <= bmi < 24.9: category = "Normal"
    elif 25 <= bmi < 29.9: category = "Overweight"
    else: category = "Obese"
    
    return f"{bmi:.1f}", category

def calculate_tdee(profile, weight):
    """Calculates TDEE and BMR based on profile data and a specific weight."""
    age = profile.get('age', 25)
    gender = profile.get('gender', 'Male')
    height = profile.get('height', 170)
    activity_level = profile.get('activity_level', 'Moderately active')

    if gender == "Male":
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
        
    activity_multipliers = {
        "Sedentary": 1.2, "Lightly active": 1.375, 
        "Moderately active": 1.55, "Very active": 1.725, "Extremely active": 1.9
    }
    tdee = bmr * activity_multipliers.get(activity_level, 1.2)
    return round(bmr), round(tdee)

def prepare_calorie_status_data(bmi_history_df, food_log_df):
    """Prepares data for the calorie status bar plot."""
    if bmi_history_df.empty and food_log_df.empty:
        return pd.DataFrame(columns=['Date', 'Actual Calorie Intake', 'Status'])

    # Prepare TDEE history
    tdee_history = bmi_history_df[['Date', 'TDEE']].copy()
    tdee_history.rename(columns={'TDEE': 'TDEE (Goal)'}, inplace=True)

    # Prepare calorie intake
    if food_log_df.empty:
        calorie_intake = pd.DataFrame(columns=['Date', 'Actual Calorie Intake'])
    else:
        food_log = food_log_df.copy()
        food_log['Date'] = pd.to_datetime(food_log['Date']).dt.date.astype(str)
        daily_calories = food_log.groupby('Date')['Calories'].sum().reset_index()
        daily_calories.columns = ['Date', 'Actual Calorie Intake']
        calorie_intake = daily_calories.sort_values(by='Date')

    # Merge and calculate status
    comparison_df = pd.merge(tdee_history, calorie_intake, on='Date', how='outer').sort_values(by='Date').fillna(0)
    comparison_df['TDEE (Goal)'] = comparison_df['TDEE (Goal)'].replace(0, np.nan).ffill()
    comparison_df.fillna({'TDEE (Goal)': 2000}, inplace=True) # Default TDEE if none is logged
    
    comparison_df['Status'] = np.where(
        (comparison_df['Actual Calorie Intake'] > comparison_df['TDEE (Goal)']) & (comparison_df['TDEE (Goal)'] > 0),
        'Over Goal', 'Under/On Goal'
    )
    
    # Return only days where calories were actually logged
    result_df = comparison_df[comparison_df['Actual Calorie Intake'] > 0]
    return result_df[['Date', 'Actual Calorie Intake', 'Status']]
