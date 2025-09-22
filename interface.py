# interface.py

import gradio as gr

def create_interface(handlers):
    """Creates and returns the Gradio web interface."""

    css = """
    body { font-family: 'Arial', sans-serif; background: linear-gradient(135deg, #000000 0%, #000000 100%); color: #ffffff; }
    .gr-block { background-color: rgba(255, 255, 255, 0.1) !important; border-radius: 12px !important; box-shadow: 0 4px 12px rgba(255, 105, 180, 0.3) !important; padding: 20px !important; border: 1px solid #ff69b4 !important; }
    h1, h2, h3 { text-align: center; color: #ff69b4 !important; margin-bottom: 10px !important; text-shadow: 0 0 10px rgba(255, 105, 180, 0.5); }
    .gr-button { background: linear-gradient(45deg, #ff69b4, #ff1493) !important; color: white !important; border: 1px solid #ffffff !important; border-radius: 8px !important; font-weight: bold !important; transition: all 0.3s !important; }
    .gr-button:hover { transform: translateY(-2px); box-shadow: 0 6px 14px rgba(255, 105, 180, 0.5) !important; }
    label { color: #ff69b4 !important; font-weight: bold !important; }
    """

    with gr.Blocks(css=css, theme=gr.themes.Default(primary_hue="pink")) as app:
        gr.Markdown("# 💖 Health Calculator Suite 💖")
        current_user_state = gr.State(None)
        session_data_state = gr.State({})

        # --- Login/Register View ---
        with gr.Column(visible=True) as login_view:
            with gr.Tabs():
                with gr.TabItem("Login"):
                    login_user_input = gr.Textbox(label="Username")
                    login_password_input = gr.Textbox(label="Password", type="password")
                    login_button = gr.Button("Login")
                    login_status_message = gr.Markdown("")
                with gr.TabItem("Register"):
                    reg_user_input = gr.Textbox(label="Username")
                    reg_password_input = gr.Textbox(label="Password", type="password")
                    reg_confirm_password_input = gr.Textbox(label="Confirm Password", type="password")
                    register_button = gr.Button("Register")
                    register_status_message = gr.Markdown("")

        # --- Main App View ---
        with gr.Column(visible=False) as main_app_view:
            welcome_message = gr.Markdown("Welcome!")
            logout_button = gr.Button("Logout")
            with gr.Tabs() as tabs:
                with gr.TabItem("My Profile"):
                    profile_height_input = gr.Number(label="Height (cm)", value=170)
                    profile_weight_input = gr.Number(label="Latest Weight (kg)", value=70)
                    profile_age_input = gr.Slider(label="Age", minimum=10, maximum=100, value=25, step=1)
                    profile_gender_input = gr.Radio(choices=["Male", "Female"], label="Gender", value="Male")
                    activity_level_profile = gr.Dropdown(choices=["Sedentary", "Lightly active", "Moderately active", "Very active", "Extremely active"], label="Activity Level", value="Moderately active")
                    save_profile_button = gr.Button("Save Profile")
                    profile_status_message = gr.Markdown()
                
                with gr.TabItem("Log Weight / BMI"):
                    weight_input_bmi = gr.Number(label="Current Weight (kg)", value=70)
                    calculate_bmi_button = gr.Button("Log New Weight")
                    bmi_output = gr.Textbox(label="BMI Value", interactive=False)
                    category_output = gr.Textbox(label="Category", interactive=False)

                with gr.TabItem("Metabolic Rate Calculator"):
                    calculate_bmr_button = gr.Button("Calculate My Current Metabolic Rate")
                    bmr_info_text = gr.Markdown()
                    bmr_output_display = gr.Textbox(label="BMR", interactive=False)
                    tdee_output_display = gr.Textbox(label="TDEE", interactive=False)
                    loss_output = gr.Textbox(label="For Weight Loss", interactive=False)
                    maintenance_output = gr.Textbox(label="For Maintenance", interactive=False)
                    gain_output = gr.Textbox(label="For Weight Gain", interactive=False)

                with gr.TabItem("Food Tracker"):
                    food_item_input = gr.Textbox(label="Food Item", placeholder="e.g., Banana")
                    calories_input = gr.Number(label="Calories", value=0, precision=0)
                    log_button = gr.Button("Add Food Entry")
                    food_log_df = gr.DataFrame(headers=["Date", "Food", "Calories"], label="Your Food Log", interactive=False)

                with gr.TabItem("Historical Graphs"):
                    bmi_history_plot = gr.LinePlot(x="Date", y="BMI", title="BMI Over Time", tooltip=['Date', 'BMI', 'Weight'])
                    calorie_status_plot = gr.BarPlot(x="Date", y="Actual Calorie Intake", color="Status", color_map={"Over Goal": "red", "Under/On Goal": "green"}, title="Calorie Intake vs. Daily Goal", y_lim=[0, 4000])

        # --- Component Connections ---
        # Note: The 'fn' argument now points to functions passed in via the 'handlers' dictionary.
        register_button.click(fn=handlers['register'], inputs=[reg_user_input, reg_password_input, reg_confirm_password_input], outputs=[register_status_message])
        
        login_outputs = [current_user_state, session_data_state, login_view, main_app_view, login_status_message, 
                         food_log_df, bmi_history_plot, calorie_status_plot, profile_height_input, 
                         profile_weight_input, profile_age_input, profile_gender_input, activity_level_profile]
        login_button.click(fn=handlers['login'], inputs=[login_user_input, login_password_input], outputs=login_outputs)
        
        logout_outputs = [current_user_state, session_data_state, login_view, main_app_view, login_status_message, 
                          food_log_df, bmi_history_plot, calorie_status_plot, profile_height_input, 
                          profile_weight_input, profile_age_input, profile_gender_input, activity_level_profile, 
                          weight_input_bmi, food_item_input, calories_input, bmi_output, category_output, 
                          bmr_output_display, tdee_output_display, loss_output, maintenance_output, gain_output, 
                          bmr_info_text, profile_status_message]
        logout_button.click(fn=handlers['logout'], inputs=None, outputs=logout_outputs)
        
        save_profile_button.click(fn=handlers['save_profile'], inputs=[profile_height_input, profile_weight_input, profile_age_input, profile_gender_input, activity_level_profile, current_user_state, session_data_state], outputs=[profile_status_message, session_data_state])
        
        calculate_bmi_button.click(fn=handlers['update_bmi'], inputs=[weight_input_bmi, current_user_state, session_data_state], outputs=[bmi_output, category_output, bmi_history_plot, calorie_status_plot, profile_weight_input, session_data_state])
        
        log_button.click(fn=handlers['add_food'], inputs=[food_item_input, calories_input, current_user_state, session_data_state], outputs=[food_log_df, calorie_status_plot, session_data_state])
        
        calculate_bmr_button.click(fn=handlers['calculate_bmr_tdee_display'], inputs=[current_user_state, session_data_state], outputs=[bmr_output_display, tdee_output_display, loss_output, maintenance_output, gain_output, bmr_info_text])

    return app
