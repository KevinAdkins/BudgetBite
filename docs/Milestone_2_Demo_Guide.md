### Demo Guide
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
In the same .env file from the Genimi Setup
Request keys from Mr.Abundis
```bash
KROGER_CLIENT_ID=app-name
KROGER_CLIENT_SECRET=your-api-key
KROGER_BASE_URL=https://api-ce.kroger.com
KROGER_SCOPE=product-scope
KROGER_ZIP_CODE=zip-code
```

#### Start the Backend Server
```bash
python (or py) app.py
```

The backend API will start running at `http://localhost:5001`

You should see a message indicating the Flask server is running.

### Frontend Setup

````bash
cd frontend
```bash

### Find your IP address and add to .env

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

### Test the API
You can test if the backend is working by visiting these endpoints in your browser:
- `http://localhost:5001/` - API information
- `http://localhost:5001/api/meals` - View all meals (pls let me know if it works)

