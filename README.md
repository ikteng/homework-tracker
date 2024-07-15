# Homework Tracker
This Homework Tracker program is a Flask-based web application designed to help users manage their assignments. Here's an overview of its key features and components:

## Backend Components
1. Flask App Setup:
- The app uses Flask as its web framework and SQLite for the database.
- Flask-Bcrypt is used for password hashing.

2. Database:
- users Table: Stores user data, including username, password hash, and optional email.
- assignments Table: Stores assignments linked to users, including subject, description, due date, due time, and completion status.

3. Database Operations:
- Create Tables: Initializes the users and assignments tables if they don’t already exist.
- CRUD Operations: Functions to create, read, update, and delete assignments, as well as user registration and login.

4. Authentication:
- Registration: Users can create accounts with unique usernames and hashed passwords.
- Login/Logout: Users can log in and log out, with session management to keep track of logged-in users.

5. Assignment Management:
- Add Assignment: Allows users to add new assignments.
- Edit Assignment: Users can update details of existing assignments.
- Toggle Status: Updates the completion status of assignments.
- Delete Assignment: Removes assignments from the database.

6. Settings:
- Users can update their username, password, and email in the settings page.

## Frontend Components:
1. HTML Templates:
- Index Page: Displays the user’s assignments and a calendar view. Includes search functionality and assignment management (add, edit, delete, mark completed).
   ![image](https://github.com/user-attachments/assets/eefa7f59-0133-448f-b68b-b5e092008bbc)
  
- Login Page: Allows users to log in.
 ![image](https://github.com/user-attachments/assets/3c8ba3a8-96f5-47af-8b20-50044628f4eb)
  
- Register Page: Allows new users to register.
   ![image](https://github.com/user-attachments/assets/9fac4f0c-7dbf-41de-b87e-ebad5dea8df0)
  
- Settings Page: Provides options for updating user details.
  ![image](https://github.com/user-attachments/assets/b2fa115f-8c92-4e9b-af0f-00cf2d3cc0ad)

2. CSS and JavaScript:
- Styling: The pages use CSS files for styling.
- FullCalendar Integration: Displays assignments on a calendar view, allowing users to see due dates and times.
- Modals: Used for adding and editing assignments.
  ![image](https://github.com/user-attachments/assets/7e9a688a-4c10-44e5-b795-209b353f9333)

- Dark Mode: Users can toggle between light and dark modes with localStorage persistence.
  ![image](https://github.com/user-attachments/assets/bb4f1851-8ff8-4dbe-96b8-61fc9d591b34)


3. Functional Details:
- Search Functionality: Allows users to filter assignments based on subject or description.
  ![image](https://github.com/user-attachments/assets/dca268b2-f1d5-468e-83bb-3b032bb1987c)

- Calendar Integration: Uses FullCalendar to visually manage assignments based on their due dates and times.
  ![image](https://github.com/user-attachments/assets/7d2e5dc9-c3a8-41f0-86ea-9ea4b22fd757)

- Dynamic Updates: Uses JavaScript to dynamically update assignment statuses, handle modals, and search results without reloading the page.

## Creating the requirements.txt
1. create the virtual environment by opening the Command Palette (Ctrl + Shift + P)
   - choose Python: Select Interpreter (make sure you already have python downloaded)
   - choose +create new environment, create a new .venv, choose python + version
   - you may need to activate the virtual environment (source .venv/bin/activate)
2. install requirement packages using pip install
3. generate the requirements.txt file (pip freeze > requirements.txt)
4. verify installation (pip list)

## Creating Desktop application
I used pywebview & threading to create this desktop application with a webview that can display my Flask application.

## Creating Executable File
I used PyInstaller to create the executable.
1. install pyinstaller: pip install pyinstaller
2. create a .spec file & the executable : pyinstaller --onefile app.py or pyinstaller --onefile --add-data "templates;templates" --add-data "static;static" app.py
The executable is placed in the dist directory. 
