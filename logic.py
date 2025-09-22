import pandas as pd
import numpy as np
import datetime
import gradio as gr
from datamanager import user_health_data, save_data, _hash_password

# --- Helper Functions ---
def calculate_tdee(profile, weight):
    """Calculates TDEE and BMR based on profile data and a specific weight."""
    age, gender, height, activity_level = profile['age'], profile['gender'], profile['height'], profile['activity_level']

    if gender == "Male":
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

    activity_multipliers = {"Sedentary": 1.2, "Lightly active": 1.375, "Moderately active": 1.55, "Very active": 1.725, "Extremely active": 1.9}
    tdee = bmr * activity_multipliers.get(activity_level, 1.2)
    return round(bmr), round(tdee)

def get_daily_calories(current_user):
    """Aggregates calories by day for plotting."""
    if not current_user or user_health_data[current_user]['food_log'].empty:
        return pd.DataFrame(columns=['Date', 'Actual Intake'])

    food_log = user_health_data[current_user]['food_log'].copy()
    food_log['Date'] = pd.to_datetime(food_log['Date']).dt.date.astype(str)
    daily_calories = food_log.groupby('Date')['Calories'].sum().reset_index()
    daily_calories.columns = ['Date', 'Actual Intake']
    return daily_calories.sort_values(by='Date')

def prepare_calorie_status_data(current_user):
    """Prepares data for a single-bar calorie plot with conditional coloring."""
    if not current_user:
        return pd.DataFrame(columns=['Date', 'Actual Calorie Intake', 'Status'])

    tdee_history = user_health_data[current_user]['bmi_history'][['Date', 'TDEE']].copy()
    tdee_history.rename(columns={'TDEE': 'TDEE (Goal)'}, inplace=True)

    calorie_intake = get_daily_calories(current_user)
    calorie_intake.rename(columns={'Actual Intake': 'Actual Calorie Intake'}, inplace=True)

    comparison_df = pd.merge(tdee_history, calorie_intake, on='Date', how='outer').sort_values(by='Date').fillna(0)

    comparison_df['TDEE (Goal)'] = comparison_df['TDEE (Goal)'].replace(0, np.nan).ffill()
    comparison_df.fillna({'TDEE (Goal)': 2000}, inplace=True) # Default goal if none is ever set

    comparison_df['Status'] = np.where(
        (comparison_df['Actual Calorie Intake'] > comparison_df['TDEE (Goal)']) & (comparison_df['TDEE (Goal)'] > 0),
        'Over Goal',
        'Under/On Goal'
    )

    result_df = comparison_df[comparison_df['Actual Calorie Intake'] > 0]
    return result_df[['Date', 'Actual Calorie Intake', 'Status']]

def calculate_bmi(height, weight):
    """Pure BMI calculation."""
    if height > 0:
        bmi = weight / ((height / 100) ** 2)
    else:
        bmi = 0

    category = "Underweight"
    if 18.5 <= bmi < 24.9:
        category = "Normal"
    elif 25 <= bmi < 29.9:
        category = "Overweight"
    elif bmi >= 30:
        category = "Obese"
    return f"{bmi:.1f}", category

# --- Core Functions (Authentication & Data Handling) ---
def register_user(username, password, confirm_password):
    """Handles user registration."""
    if not username or not password or not confirm_password:
        return "Username and password cannot be empty."
    if password != confirm_password:
        return "Passwords do not match."
    if username in user_health_data:
        return "Username already exists. Please choose another one."

    hashed_password = _hash_password(password)
    user_health_data[username] = {
        'password': hashed_password,
        'profile': {'height': 170, 'weight': 70, 'age': 25, 'gender': 'Male', 'activity_level': 'Moderately active'},
        'bmi_history': pd.DataFrame(columns=['Date', 'BMI', 'Weight', 'TDEE']),
        'food_log': pd.DataFrame(columns=['Date', 'Food', 'Calories'])
    }
    save_data(user_health_data)
    return f"✅ Registration successful for **{username}**! You can now log in."

def login_user(username, password):
    """Handles user login and data loading."""
    if not username or not password:
        return (None, gr.update(), gr.update(), "Please enter username and password.", pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 170, 70, 25, "Male", "Moderately active")

    if username not in user_health_data or user_health_data[username]['password'] != _hash_password(password):
        return (None, gr.update(), gr.update(), "❌ Invalid username or password.", pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 170, 70, 25, "Male", "Moderately active")

    welcome_msg = f"👋 Welcome back, **{username}**!"
    user_profile = user_health_data[username]['profile']
    user_food_log = user_health_data[username]['food_log']

    _, tdee_val = calculate_tdee(user_profile, user_profile['weight'])
    today = datetime.date.today().strftime("%Y-%m-%d")

    history_df = user_health_data[username]['bmi_history']
    if history_df.empty or today not in history_df['Date'].values:
        bmi_val_str, _ = calculate_bmi(user_profile['height'], user_profile['weight'])
        new_entry = pd.DataFrame({
            'Date': [today], 'BMI': [float(bmi_val_str)],
            'Weight': [user_profile['weight']], 'TDEE': [tdee_val]
        })
        updated_history = pd.concat([history_df, new_entry], ignore_index=True)
        user_health_data[username]['bmi_history'] = updated_history
        save_data(user_health_data)

    updated_history = user_health_data[username]['bmi_history']
    calorie_status_data = prepare_calorie_status_data(username)

    return (
        username, gr.update(visible=False), gr.update(visible=True), welcome_msg,
        user_food_log,
        updated_history, calorie_status_data,
        user_profile['height'], user_profile['weight'], user_profile['age'],
        user_profile['gender'], user_profile['activity_level']
    )

def logout():
    """Handles user logout and UI reset."""
    return (
        None, gr.update(visible=True), gr.update(visible=False), "",
        pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
        170, 70, 25, "Male", "Moderately active",
        70, "", 0, "", "",
        "", "", "", "", "", "",
        "Profile saved successfully!"
    )

def save_profile(height, weight, age, gender, activity_level, current_user):
    """Saves user's profile information."""
    if not current_user: return "Please log in first."

    user_health_data[current_user]['profile'] = {
        'height': height, 'weight': weight, 'age': age,
        'gender': gender, 'activity_level': activity_level
    }
    save_data(user_health_data)
    return f"{current_user}'s profile has been saved!"

def update_bmi(current_weight, current_user):
    """Calculates and logs BMI and TDEE, then updates all charts."""
    if not current_user: return None, "Please log in first.", pd.DataFrame(), pd.DataFrame(), 0

    profile = user_health_data[current_user]['profile']
    height = profile['height']

    bmi_val_str, category = calculate_bmi(height, current_weight)
    _, tdee_val = calculate_tdee(profile, current_weight)

    user_health_data[current_user]['profile']['weight'] = current_weight

    today = datetime.date.today().strftime("%Y-%m-%d")
    new_entry = pd.DataFrame({'Date': [today], 'BMI': [float(bmi_val_str)], 'Weight': [current_weight], 'TDEE': [tdee_val]})

    history_df = user_health_data[current_user]['bmi_history']
    updated_history = pd.concat([history_df, new_entry], ignore_index=True)
    updated_history = updated_history.drop_duplicates(subset=['Date'], keep='last').sort_values(by='Date')
    user_health_data[current_user]['bmi_history'] = updated_history
    save_data(user_health_data)

    calorie_status_data = prepare_calorie_status_data(current_user)

    return bmi_val_str, category, updated_history, calorie_status_data, current_weight

def add_food(food, calories, current_user):
    """Logs a food item and updates the comparison charts."""
    if not current_user: return pd.DataFrame(), pd.DataFrame()

    today = datetime.date.today().strftime("%Y-%m-%d")
    new_entry = pd.DataFrame({'Date': [today], 'Food': [food], 'Calories': [int(calories)]})

    user_health_data[current_user]['food_log'] = pd.concat(
        [user_health_data[current_user]['food_log'], new_entry], ignore_index=True)
    save_data(user_health_data)

    updated_food_log = user_health_data[current_user]['food_log']
    calorie_status_data = prepare_calorie_status_data(current_user)

    return updated_food_log, calorie_status_data

def calculate_bmr_tdee_for_display(current_user):
    """Calculates BMR/TDEE for display using current profile data."""
    if not current_user: return "N/A", "N/A", "N/A", "N/A", "N/A", "Please log in first."

    profile = user_health_data[current_user]['profile']
    bmr, tdee = calculate_tdee(profile, profile['weight'])

    info_text = f"Calculated based on: Age {profile['age']}, Height {profile['height']} cm, Weight {profile['weight']} kg, Gender {profile['gender']}"

    return (
        f"{bmr} calories/day", f"{tdee} calories/day",
        f"{tdee - 500} calories/day", f"{tdee} calories/day", f"{tdee + 500} calories/day",
        info_text
    )

