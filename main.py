# health_app/main.py

from google.colab import drive
import data_manager
import logic
from app_interface import build_ui
def main():
    # --- Initial Setup ---
    # 1. Connect to Google Drive
    drive.mount('/content/drive')
    
    # 2. Ensure the data folder exists
    data_manager.setup_drive_folder()

    # 3. Build the UI and get components
    app, c = build_ui() # 'c' is the dictionary of components

    # --- Connect UI Components to Logic Functions ---

    # Registration
    c['register_button'].click(
        fn=logic.register_user,
        inputs=[c['reg_user_input'], c['reg_password_input'], c['reg_confirm_password_input']],
        outputs=[c['register_status_message']]
    )

    # Login
    c['login_button'].click(
        fn=logic.login_user,
        inputs=[c['login_user_input'], c['login_password_input']],
        outputs=[
            c['current_user_state'], c['login_view'], c['main_app_view'], c['login_status_message'],
            c['food_log_df'], c['bmi_history_plot'], c['calorie_status_plot'],
            c['profile_height_input'], c['profile_weight_input'], c['profile_age_input'],
            c['profile_gender_input'], c['activity_level_profile']
        ]
    )
    
    # Logout
    c['logout_button'].click(
        fn=logic.logout,
        inputs=None,
        outputs=[
            c['current_user_state'], c['login_view'], c['main_app_view'], c['login_status_message'],
            c['food_log_df'], c['bmi_history_plot'], c['calorie_status_plot'],
            c['profile_height_input'], c['profile_weight_input'], c['profile_age_input'],
            c['profile_gender_input'], c['activity_level_profile'],
            c['weight_input_bmi'], c['food_item_input'], c['calories_input'],
            c['bmi_output'], c['category_output'],
            c['bmr_output_display'], c['tdee_output_display'], c['loss_output'],
            c['maintenance_output'], c['gain_output'], c['bmr_info_text'],
            c['profile_status_message']
        ]
    )

    # Save Profile
    c['save_profile_button'].click(
        fn=logic.save_profile,
        inputs=[
            c['profile_height_input'], c['profile_weight_input'], c['profile_age_input'],
            c['profile_gender_input'], c['activity_level_profile'], c['current_user_state']
        ],
        outputs=[c['profile_status_message']]
    )

    # Log Weight / BMI
    c['calculate_bmi_button'].click(
        fn=logic.update_bmi,
        inputs=[c['weight_input_bmi'], c['current_user_state']],
        outputs=[
            c['bmi_output'], c['category_output'], c['bmi_history_plot'],
            c['calorie_status_plot'], c['profile_weight_input']
        ]
    )

    # Add Food Entry
    c['log_button'].click(
        fn=logic.add_food,
        inputs=[c['food_item_input'], c['calories_input'], c['current_user_state']],
        outputs=[c['food_log_df'], c['calorie_status_plot']]
    )

    # Calculate BMR/TDEE Display
    c['calculate_bmr_button'].click(
        fn=logic.calculate_bmr_tdee_for_display,
        inputs=[c['current_user_state']],
        outputs=[
            c['bmr_output_display'], c['tdee_output_display'], c['loss_output'],
            c['maintenance_output'], c['gain_output'], c['bmr_info_text']
        ]
    )
    
    return app

if __name__ == "__main__":
    health_app = main()
    health_app.launch()
