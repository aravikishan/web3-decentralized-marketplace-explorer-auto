from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
from datetime import datetime
import sqlite3
import os

app = FastAPI()

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Database setup
DATABASE = 'marketplace.db'

# Ensure database and tables are created
if not os.path.exists(DATABASE):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE listings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        price REAL NOT NULL,
        seller_wallet TEXT NOT NULL
    )''')
    cursor.execute('''CREATE TABLE users (
        wallet_address TEXT PRIMARY KEY,
        profile_info TEXT NOT NULL
    )''')
    cursor.execute('''CREATE TABLE transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_wallet TEXT NOT NULL,
        listing_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    # Seed data
    cursor.execute("INSERT INTO listings (title, description, price, seller_wallet) VALUES (?, ?, ?, ?)",
                   ("Sample Listing", "This is a sample listing.", 10.0, "0xSellerWallet"))
    cursor.execute("INSERT INTO users (wallet_address, profile_info) VALUES (?, ?)",
                   ("0xUserWallet", "Sample user profile info."))
    cursor.execute("INSERT INTO transactions (user_wallet, listing_id, amount) VALUES (?, ?, ?)",
                   ("0xUserWallet", 1, 10.0))
    conn.commit()
    conn.close()

# Data models
class Listing(BaseModel):
    id: int
    title: str
    description: str
    price: float
    seller_wallet: str

class User(BaseModel):
    wallet_address: str
    profile_info: str
    transaction_history: List[int]

class Transaction(BaseModel):
    id: int
    user_wallet: str
    listing_id: int
    amount: float
    timestamp: datetime

# Endpoints
@app.get("/api/listings", response_model=List[Listing])
async def get_listings():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM listings")
    listings = cursor.fetchall()
    conn.close()
    return [Listing(id=row[0], title=row[1], description=row[2], price=row[3], seller_wallet=row[4]) for row in listings]

@app.get("/api/listings/{id}", response_model=Listing)
async def get_listing(id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM listings WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return Listing(id=row[0], title=row[1], description=row[2], price=row[3], seller_wallet=row[4])
    raise HTTPException(status_code=404, detail="Listing not found")

@app.post("/api/users", response_model=User)
async def create_user(user: User):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (wallet_address, profile_info) VALUES (?, ?)",
                       (user.wallet_address, user.profile_info))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="User already exists")
    finally:
        conn.close()
    return user

@app.get("/api/users/{wallet_address}", response_model=User)
async def get_user(wallet_address: str):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE wallet_address = ?", (wallet_address,))
    user_row = cursor.fetchone()
    if not user_row:
        raise HTTPException(status_code=404, detail="User not found")
    cursor.execute("SELECT * FROM transactions WHERE user_wallet = ?", (wallet_address,))
    transactions = cursor.fetchall()
    conn.close()
    transaction_history = [Transaction(id=row[0], user_wallet=row[1], listing_id=row[2], amount=row[3], timestamp=row[4]) for row in transactions]
    return User(wallet_address=user_row[0], profile_info=user_row[1], transaction_history=transaction_history)

@app.get("/api/transactions", response_model=List[Transaction])
async def get_transactions(user_wallet: str):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE user_wallet = ?", (user_wallet,))
    transactions = cursor.fetchall()
    conn.close()
    return [Transaction(id=row[0], user_wallet=row[1], listing_id=row[2], amount=row[3], timestamp=row[4]) for row in transactions]

# HTML Routes
@app.get("/", response_class=HTMLResponse)
async def read_home(request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/listings", response_class=HTMLResponse)
async def read_listings(request):
    return templates.TemplateResponse("listings.html", {"request": request})

@app.get("/profile", response_class=HTMLResponse)
async def read_profile(request):
    return templates.TemplateResponse("profile.html", {"request": request})

@app.get("/listing/{id}", response_class=HTMLResponse)
async def read_listing_detail(request, id: int):
    return templates.TemplateResponse("listing_detail.html", {"request": request, "id": id})

@app.get("/about", response_class=HTMLResponse)
async def read_about(request):
    return templates.TemplateResponse("about.html", {"request": request})
