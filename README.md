# BudgetBite
Senior Project
An app that can take a picture of what you have and come up with a meal idea.<br>
The goal is to keep it budget-friendly while recommending you healthy meals to make.

# Team Members and Our Roles
**Jorge Munoz:** Team Leader & AI Developer<br>
**Kevin Adkins:** Frontend Developer<br>
**Alvaro Gonzalez:** Database Developer<br>
**David Abundis:** Wireframe Developer<br>
**Eric Gerner:** Backend Developer<br>

# How to Run

## Prerequisites
Before running BudgetBite, make sure you have:
- Python 3.8 or higher installed
- pip (Python package manager)
- Git (for cloning the repository)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/KevinAdkins/BudgetBite.git
cd BudgetBite
```

### 2. Backend Setup

#### Install Python Dependencies
Navigate to the backend directory and install required packages:
```bash
cd backend
pip install -r requirements.txt
```

#### Initialize the Database
The database will be automatically created when you first run the app. To manually seed the database with sample data, run:
```bash
python (or py) seed.py
```

#### Start the Backend Server
```bash
python (or py) app.py
```

The backend API will start running at `http://localhost:5000`

You should see a message indicating the Flask server is running.

### 3. Test the API
You can test if the backend is working by visiting these endpoints in your browser:
- `http://localhost:5000/` - API information
- `http://localhost:5000/api/meals` - View all meals (pls let me know if it works)

### 4. Frontend Setup
*Coming soon - tbd*

## API Endpoints
The backend provides the following endpoints:
- **GET** `/api/meals` - Get all meals
- **GET** `/api/meals/<name>` - Get specific meal by name
- **GET** `/api/meals/search?name=<name>` - Search for meal (checks database and external API)
(In-progress haven't tested yet skeleton code)
- **POST** `/api/meals` - Add new meal
- **PUT** `/api/meals/<name>` - Update meal
- **PATCH** `/api/meals/<name>/instructions` - Update instructions only
- **DELETE** `/api/meals/<name>` - Delete meal

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, you can change it by modifying `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change to any available port
```

### Database Issues
Let me know if any arise but in the meantime. Delete the `backend/data/meals.db` file and restart the server. The database will be recreated automatically.

### Module Not Found Errors
Make sure you're in the `backend` directory and have activated your virtual environment (if using one). Then reinstall dependencies:
```bash
pip install -r requirements.txt
```

# Latest Docs
[Our Documents & Slides](https://github.com/KevinAdkins/BudgetBite/tree/main/docs)
