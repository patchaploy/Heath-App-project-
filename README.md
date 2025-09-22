
# 💖 Health Calculator Suite 💖

A web-based health tracking application built with Python, Gradio, and Firebase. It allows users to register, log in, and track their health metrics like BMI, TDEE, and daily calorie intake.

## Features

-   **User Authentication**: Secure user registration and login system.
-   **Profile Management**: Save and update personal data like height, weight, age, and activity level.
-   **BMI Tracking**: Log daily weight to calculate and visualize BMI over time.
-   **Calorie Counter**: Track daily food intake and compare it against your TDEE (Total Daily Energy Expenditure) goal.
-   **Metabolic Rate Calculator**: Calculates BMR and TDEE based on your profile.
-   **Data Persistence**: All user data is securely stored online using Google Firebase Firestore.

## Project Structure

The project is organized into several modules for better maintainability:

-   `main.py`: The main entry point of the application. It initializes all components and runs the Gradio app.
-   `interface.py`: Defines the entire user interface using the Gradio library.
-   `logic.py`: Contains all the business logic, such as calculations for BMI, TDEE, and data processing for plots.
-   `datamanager.py`: Handles all interactions with the Firebase Firestore database.
-   `requirements.txt`: A list of all the Python packages required to run the project.

## 🚀 Getting Started

### Prerequisites

-   Python 3.8 or newer
-   A Google Firebase project

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd health-app
    ```

2.  **Set up a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Firebase Credentials:**
    -   Go to your Firebase project console.
    -   Navigate to `Project settings` > `Service accounts`.
    -   Click on "Generate new private key" to download a JSON file.
    -   **Rename this file to `firebase_credentials.json`** and place it in the root directory of this project (`health-app/`).

5.  **Run the application:**
    ```bash
    python main.py
    ```

The application will now be running and accessible at a local URL (e.g., `http://127.0.0.1:7860`).
