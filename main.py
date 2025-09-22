from interface import app

# This is the main entry point of the application.
# It imports the 'app' object from the interface file and launches it.
if __name__ == "__main__":
    # The datamanager.py file handles mounting Google Drive,
    # so we just need to launch the UI here.
    app.launch(share=True)
