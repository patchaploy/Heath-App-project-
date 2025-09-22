# main.py

import gradio as gr
import pandas as pd
import datetime

# Import our separated modules
from datamanager import DataManager, df_to_list, list_to_df
import logic
from interface import create_interface

# --- Initialize Data Manager ---
db_manager = DataManager()

# --- Handler Functions (The "glue" between UI and backend) ---
def register_user(username, password, confirm_password):
    """Handles user registration logic."""
    if not db_manager.db: return "Database not connected."
    if not username or not password or not confirm_password:
        return "Username and password cannot be empty."
    if password != confirm_password:
        return "Passwords do not match."
    if db_manager.user_exists(username):
        return "Username already exists. Please choose another one."

    hashed_password = logic.hash_password(password)
    db_manager.create_user(username, hashed_password)
    return f"✅ Registration successful for **{username}**! You can now log in."

def login_user(username, password):
    """Handles user login logic."""
    empty_df = pd.DataFrame()
    default_profile = (170, 70, 25, "Male", "Moderately active")
    error_return = (None, None, gr.update(), gr.update(), "❌ Invalid username or password.", empty_df, empty_df, empty_df, *default_profile)

    if not db_manager.db:
        return (None, None, gr.update(), gr.update(), "Database not connected.", empty_df, empty_df, empty_df, *default_profile)
    if not username or not password:
        return (None, None, gr.update(), gr.update(), "Please enter username and password.", empty_df, empty_df, empty_df, *default_profile)

    user_data = db_manager.get_user_data(username)
    if not user_data or user_data.get('password') != logic.hash_password(password):
        return error_return

    # --- Login Successful ---
    profile = user_data.get('profile', {})
    bmi_history_df = list_to_df(user_data.get('bmi_history', []), columns=['Date', 'BMI', 'Weight', 'TDEE'])
    food_log_df = list_to_df(user_data.get('food_log', []), columns=['Date', 'Food', 'Calories'])
    
    # Add today's TDEE entry if it doesn't exist
    today = datetime.date.today().strftime("%Y-%m-%d")
    if bmi_history_df.empty or today not in bmi_history_df['Date'].values:
        bmi_val_str, _ = logic.calculate_bmi(profile.get('height', 0), profile.get('weight', 0))
        _, tdee_val = logic.calculate_tdee(profile, profile.get('weight', 0))
        new_entry = pd.DataFrame({
            'Date': [today], 'BMI': [float(bmi_val_str)],
            'Weight': [profile.get('weight', 0)], 'TDEE': [tdee_val]
        })
        bmi_history_df = pd.concat([bmi_history_df, new_entry], ignore_index=True)
        db_manager.update_user_data(username, {'bmi_history': df_to_list(bmi_history_df)})

    calorie_status_data = logic.prepare_calorie_status_data(bmi_history_df, food_log_df)
    session_data = {'profile': profile, 'bmi_history': bmi_history_df, 'food_log': food_log_df}
    
    return (
        username, session_data, gr.update(visible=False), gr.update(visible=True), f"👋 Welcome back, **{username}**!",
        food_log_df, bmi_history_df, calorie_status_data,
        profile.get('height', 170), profile.get('weight', 70), profile.get('age', 25),
        profile.get('gender', 'Male'), profile.get('activity_level', 'Moderately active')
    )

def save_profile(height, weight, age, gender, activity_level, current_user, session_data):
    """Saves user's profile information."""
    if not current_user: return "Please log in first.", session_data
    
    session_data['profile'] = {
        'height': height, 'weight': weight, 'age': age,
        'gender': gender, 'activity_level': activity_level
    }
    db_manager.update_user_data(current_user, {'profile': session_data['profile']})
    return f"{current_user}'s profile has been saved!", session_data

def update_bmi(current_weight, current_user, session_data):
    """Calculates and logs BMI and TDEE."""
    if not current_user: return None, "Please log in first.", pd.DataFrame(), pd.DataFrame(), 0, session_data
    
    profile = session_data['profile']
    height = profile.get('height', 0)
    bmi_val_str, category = logic.calculate_bmi(height, current_weight)
    _, tdee_val = logic.calculate_tdee(profile, current_weight)
    session_data['profile']['weight'] = current_weight
    
    today = datetime.date.today().strftime("%Y-%m-%d")
    new_entry = pd.DataFrame({'Date': [today], 'BMI': [float(bmi_val_str)], 'Weight': [current_weight], 'TDEE': [tdee_val]})
    
    history_df = session_data['bmi_history']
    updated_history = pd.concat([history_df, new_entry], ignore_index=True).drop_duplicates(subset=['Date'], keep='last').sort_values(by='Date')
    session_data['bmi_history'] = updated_history
    
    db_manager.update_user_data(current_user, {
        'profile.weight': current_weight,
        'bmi_history': df_to_list(updated_history)
    })
    
    calorie_status_data = logic.prepare_calorie_status_data(updated_history, session_data['food_log'])
    return bmi_val_str, category, updated_history, calorie_status_data, current_weight, session_data

def add_food(food, calories, current_user, session_data):
    """Logs a food item."""
    if not current_user: return pd.DataFrame(), pd.DataFrame(), session_data
    
    today = datetime.date.today().strftime("%Y-%m-%d")
    new_entry = pd.DataFrame({'Date': [today], 'Food': [food], 'Calories': [int(calories)]})
    
    food_log_df = session_data['food_log']
    updated_food_log = pd.concat([food_log_df, new_entry], ignore_index=True)
    session_data['food_log'] = updated_food_log
    
    db_manager.update_user_data(current_user, {'food_log': df_to_list(updated_food_log)})
    
    calorie_status_data = logic.prepare_calorie_status_data(session_data['bmi_history'], updated_food_log)
    return updated_food_log, calorie_status_data, session_data

def calculate_bmr_tdee_for_display(current_user, session_data):
    """Calculates BMR/TDEE for display."""
    if not current_user: return "N/A", "N/A", "N/A", "N/A", "N/A", "Please log in first."
    
    profile = session_data.get('profile', {})
    bmr, tdee = logic.calculate_tdee(profile, profile.get('weight', 0))
    info_text = f"Calculated based on: Age {profile.get('age', 'N/A')}, Height {profile.get('height', 'N/A')} cm, Weight {profile.get('weight', 'N/A')} kg, Gender {profile.get('gender', 'N/A')}"
    
    return (f"{bmr} cal/day", f"{tdee} cal/day", f"{tdee - 500} cal/day", f"{tdee} cal/day", f"{tdee + 500} cal/day", info_text)

def logout():
    """Handles user logout and UI reset."""
    return (None, None, gr.update(visible=True), gr.update(visible=False), "", pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 170, 70, 25, "Male", "Moderately active", 70, "", 0, "", "", "", "", "", "", "", "", "Profile saved successfully!")


# --- Main Execution ---
if __name__ == "__main__":
    if db_manager.db:
        # A dictionary to pass all handler functions to the interface
        app_handlers = {
            "register": register_user,
            "login": login_user,
            "logout": logout,
            "save_profile": save_profile,
            "update_bmi": update_bmi,
            "add_food": add_food,
            "calculate_bmr_tdee_display": calculate_bmr_tdee_for_display,
        }
        
        app = create_interface(app_handlers)
        app.launch(debug=True)
    else:
        print("Could not start the application due to a database connection failure.")
