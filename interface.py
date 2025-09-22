import gradio as gr
import pandas as pd
from logic import (
    register_user, login_user, logout, save_profile, update_bmi,
    add_food, calculate_bmr_tdee_for_display
)

# --- UI and Styling ---
css = """
body { font-family: 'Arial', sans-serif; background: linear-gradient(135deg, #000000 0%, #00000 100%); color: #ffffff; }
.gr-block { background-color: rgba(255, 255, 255, 0.1) !important; border-radius: 12px !important; box-shadow: 0 4px 12px rgba(255, 105, 180, 0.3) !important; padding: 20px !important; border: 1px solid #ff69b4 !important; }
h1, h2, h3 { text-align: center; color: #ff69b4 !important; margin-bottom: 10px !important; text-shadow: 0 0 10px rgba(255, 105, 180, 0.5); }
.gr-button { background: linear-gradient(45deg, #ff69b4, #ff1493) !important; color: white !important; border: 1px solid #ffffff !important; border-radius: 8px !important; font-weight: bold !important; transition: all 0.3s !important; }
.gr-button:hover { transform: translateY(-2px); box-shadow: 0 6px 14px rgba(255, 105, 180, 0.5) !important; }
label { color: #ff69b4 !important; font-weight: bold !important; }
"""

def create_ui():
    with gr.Blocks(css=css, theme=gr.themes.Default(primary_hue="pink")) as app:
        gr.Markdown("# 💖 Health Calculator Suite 💖")
        current_user_state = gr.State(None)

        # --- LOGIN/REGISTER VIEW ---
        with gr.Column(visible=True) as login_view:
            with gr.Tabs():
                with gr.TabItem("Login"):
                    gr.Markdown("## Login to Your Account")
                    login_user_input = gr.Textbox(label="Username", placeholder="e.g., Alex")
                    login_password_input = gr.Textbox(label="Password", type="password")
                    login_button = gr.Button("Login")
                    login_status_message = gr.Markdown("")
                with gr.TabItem("Register"):
                    gr.Markdown("## Create a New Account")
                    reg_user_input = gr.Textbox(label="Username", placeholder="Choose a username")
                    reg_password_input = gr.Textbox(label="Password", type="password")
                    reg_confirm_password_input = gr.Textbox(label="Confirm Password", type="password")
                    register_button = gr.Button("Register")
                    register_status_message = gr.Markdown("")

        # --- MAIN APP VIEW ---
        with gr.Column(visible=False) as main_app_view:
            with gr.Row():
                welcome_message = gr.Markdown("Welcome!")
                logout_button = gr.Button("Logout")

            with gr.Tabs() as tabs:
                with gr.TabItem("My Profile"):
                    gr.Markdown("### Set Up Your Personal Profile")
                    with gr.Row():
                        with gr.Column():
                            profile_height_input = gr.Number(label="Height (cm)", value=170)
                            profile_weight_input = gr.Number(label="Latest Weight (kg)", value=70)
                            profile_age_input = gr.Slider(label="Age", minimum=10, maximum=100, value=25, step=1)
                            profile_gender_input = gr.Radio(choices=["Male", "Female"], label="Gender", value="Male")
                            activity_level_profile = gr.Dropdown(choices=["Sedentary", "Lightly active", "Moderately active", "Very active", "Extremely active"], label="Your Usual Activity Level", value="Moderately active")
                            save_profile_button = gr.Button("Save Profile")
                        with gr.Column():
                            profile_status_message = gr.Markdown("Profile saved successfully!")

                with gr.TabItem("Log Weight / BMI"):
                    gr.Markdown("### Log New Weight & BMI")
                    gr.Markdown("Enter your current weight here to update your TDEE goal on the comparison chart.")
                    weight_input_bmi = gr.Number(label="Current Weight (kg)", value=70)
                    calculate_bmi_button = gr.Button("Log New Weight")
                    bmi_output = gr.Textbox(label="BMI Value", interactive=False)
                    category_output = gr.Textbox(label="Category", interactive=False)

                with gr.TabItem("Metabolic Rate Calculator"):
                    gr.Markdown("### Daily Metabolic Rate Calculator")
                    gr.Markdown("This calculates your current metabolic rate based on your saved profile.")
                    with gr.Row():
                        with gr.Column():
                            calculate_bmr_button = gr.Button("Calculate My Current Metabolic Rate")
                            bmr_info_text = gr.Markdown()
                        with gr.Column():
                            gr.Markdown("### **Your Results**")
                            bmr_output_display = gr.Textbox(label="BMR (Basal Metabolic Rate)", interactive=False)
                            tdee_output_display = gr.Textbox(label="TDEE (Total Daily Energy Expenditure)", interactive=False)
                            gr.Markdown("### **Calorie Targets**")
                            loss_output = gr.Textbox(label="For Weight Loss", interactive=False)
                            maintenance_output = gr.Textbox(label="For Maintenance", interactive=False)
                            gain_output = gr.Textbox(label="For Weight Gain", interactive=False)

                with gr.TabItem("Food Tracker"):
                    gr.Markdown("### Log Food Calories")
                    with gr.Row():
                        with gr.Column(scale=2):
                            food_item_input = gr.Textbox(label="Food Item", placeholder="e.g., Banana")
                            calories_input = gr.Number(label="Calories", value=0, precision=0)
                            log_button = gr.Button("Add Food Entry")
                            food_log_df = gr.Dataframe(headers=["Date", "Food", "Calories"], label="Your Food Log", interactive=False)

                with gr.TabItem("Historical Graphs"):
                    gr.Markdown("## Your Progress Over Time")
                    gr.Markdown("### Daily BMI History")
                    bmi_history_plot = gr.LinePlot(x="Date", y="BMI", title="BMI Over Time", tooltip=['Date', 'BMI', 'Weight'])
                    gr.Markdown("### Daily Calorie Intake Status")
                    gr.Markdown("Green bars indicate intake was on or under your TDEE goal. Red bars indicate you went over.")
                    calorie_status_plot = gr.BarPlot(
                        x="Date", y="Actual Calorie Intake", color="Status",
                        color_map={"Over Goal": "red", "Under/On Goal": "green"},
                        title="Calorie Intake vs. Daily Goal", y_lim=[0, 4000]
                    )

        # --- Component Connections ---
        register_button.click(
            fn=register_user,
            inputs=[reg_user_input, reg_password_input, reg_confirm_password_input],
            outputs=[register_status_message]
        )

        login_button.click(
            fn=login_user, inputs=[login_user_input, login_password_input],
            outputs=[current_user_state, login_view, main_app_view, welcome_message,
                     food_log_df,
                     bmi_history_plot, calorie_status_plot,
                     profile_height_input, profile_weight_input, profile_age_input,
                     profile_gender_input, activity_level_profile]
        )

        logout_button.click(
            fn=logout, inputs=None,
            outputs=[
                current_user_state, login_view, main_app_view, login_status_message,
                food_log_df,
                bmi_history_plot, calorie_status_plot,
                profile_height_input, profile_weight_input, profile_age_input, profile_gender_input, activity_level_profile,
                weight_input_bmi,
                food_item_input, calories_input,
                bmi_output, category_output,
                bmr_output_display, tdee_output_display, loss_output, maintenance_output, gain_output, bmr_info_text,
                profile_status_message
            ]
        )

        save_profile_button.click(
            fn=save_profile,
            inputs=[profile_height_input, profile_weight_input, profile_age_input, profile_gender_input, activity_level_profile, current_user_state],
            outputs=[profile_status_message]
        )

        calculate_bmi_button.click(
            fn=update_bmi, inputs=[weight_input_bmi, current_user_state],
            outputs=[bmi_output, category_output,
                     bmi_history_plot, calorie_status_plot,
                     profile_weight_input]
        )

        log_button.click(
            fn=add_food, inputs=[food_item_input, calories_input, current_user_state],
            outputs=[food_log_df,
                     calorie_status_plot]
        )

        calculate_bmr_button.click(
            fn=calculate_bmr_tdee_for_display,
            inputs=[current_user_state],
            outputs=[bmr_output_display, tdee_output_display, loss_output, maintenance_output, gain_output, bmr_info_text]
        )
        return app

# Create the app instance by calling the function
app = create_ui()
