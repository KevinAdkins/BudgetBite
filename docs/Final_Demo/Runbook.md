# Demo Guide

## Prerequisites
Before running BudgetBite, make sure you have:
- Python 3.8 or higher installed
- uv (Python package manager)
- Git (for cloning the repository)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/KevinAdkins/BudgetBite.git
cd BudgetBite
```
### Backend Setup

### Make venv and install dependencies
Navigate to backend make venv and install dependencies
```bash
cd backend
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

#### Initialize the Database
The database will be automatically created when you first run the app. To manually seed the database with sample data, run:
```bash
python (or py) seed.py
```
Seed data is stored in [backend/data/meals_seed.csv](backend/data/meals_seed.csv) so teammates can update rows without hand-writing SQL inserts.
The CSV includes pricing fields (`estimated_price`, `currency`, `price_source`, `price_last_updated`) so you can share stable seeded prices without calling external APIs.
To export the latest DB meals back into CSV for teammates, run:
```bash
python (or py) seed.py --export-csv
```
#### Add Gemini API Key to env file in main directory
You can find your gemini api key at this link https://aistudio.google.com/api-keys?project=gen-lang-client-0861647321
```bash
GEMINI_API_KEY=YOUR GEMINI API KEY HERE
```
### Kroger API Setup

Go to this link to create an account
[kroger.api/login](https://login.kroger.com/eciamp.onmicrosoft.com/B2C_1A__developer_signup_signin/api/CombinedSigninAndSignup/unified?local=signup&csrf_token=Tm0xY1lYN0cxZXd2Y0RET1U4eEVXK1FQaG92clduQ1ptWnN1ZWpTRWtrUmJWbTlqc0V5K01YcjFSWklIcFByN1Z6ZzhBZ2sxZ2xLTlZvNU1RbVpIT3c9PTsyMDI2LTA1LTAxVDE1OjMwOjIyLjUwMTA4MjhaO3V4WEpKbWdFWUJnWHAwbEJFcnpNV0E9PTt7Ik9yY2hlc3RyYXRpb25TdGVwIjo0fQ==&tx=StateProperties=eyJUSUQiOiIyMmRmYmYxYi0xOGEzLTRiMTktOTYzNC04YmY1OGI0YmVhNDcifQ&p=B2C_1A__developer_signup_signin)

Copy and paset the client_id and client_secret

In the same .env file from the Genimi Setup
Request keys from Mr.Abundis
```bash
KROGER_CLIENT_ID=app-name
KROGER_CLIENT_SECRET=your-api-key
KROGER_BASE_URL=https://api-ce.kroger.com
KROGER_SCOPE=product.compact
KROGER_ZIP_CODE=zip-code
```

#### Start the Backend Server
```bash
python (or py) app.py
```

The backend API will start running at `http://localhost:5001`

You should see a message indicating the Flask server is running.

### Frontend Setup

In a new terminal

````bash
cd frontend
```bash

### Find your IP address and add to .env inside of frontend folder

Find your local IP address:
```bash
ipconfig on Windows
hostname -I for Linux
Look for IPv4 Address for your IP
````

In `.env`,  add your IP with the port in the .env.example:

### Download expo imports
```bash
npm install
```
#### Start the Frontend

```bash
npx expo start --web
```

If your phone can't connect run:

```bash
npx expo start --web --host tunnel
```

#### Expo Go 
Download Expo Go from your phone's app store and scan the QR code in the terminal output after running npx expo start

Taking pictures is the easiest with the phone camera

#### Good Test Cases
- Take a picture of just one ingredient such as a water bottle -> Alert not enough ingredients
- Take a picture of the inside of your fridge or groceries -> A recipe

- Regeneration Flow
  - Provide this text input: filet mignon steak, lobster tails, sea scallops, king crab legs, black truffle oil, fresh parmesan cheese, heavy cream, unsalted butter, yukon gold potatoes, asparagus, extra virgin olive oil, garlic, shallots, fresh thyme, fresh rosemary, lemon, sea salt, black pepper
  - Select the the cheap budget tier
 
How to read Budget Results
<img width="1356" height="184" alt="image" src="https://github.com/user-attachments/assets/5a677598-bb5f-4bbd-9b1e-8ead03e1cb6a" />
- Using Budget: the selected budget tier
- Estimated total: The total of only the ingredient used in the recipe 
- Budget Limit: Max budget in the selected tier
- Generation attempts: The amount of times the recipe has been generated.

### Test the API
You can test if the backend is working by visiting these endpoints in your browser:
- `http://localhost:5001/` - API information
- `http://localhost:5001/api/meals` - View all meals (pls let me know if it works)

