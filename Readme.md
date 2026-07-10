# Booking Attractions

A Python-based data importer that processes Booking.com Attractions API datasets and stores them in a SQLite database using SQLAlchemy. The importer supports attractions, localized content, photos, reviews, and review score breakdowns with efficient batch processing and upsert operations.

## Features

- Import attraction details
- Import localized names and descriptions
- Import attraction photos
- Import attraction reviews
- Import review score breakdowns
- Batch processing for large JSON files
- Streaming JSON parsing using `ijson`
- Upsert support to avoid duplicate records

## Tech Stack

- Python 3.12+
- Django (settings & management command)
- SQLAlchemy
- SQLite
- ijson

## Project Structure

```
booking_attraction/
├── attractions/
├── data/
│   ├── attraction_details/
│   ├── reviews/
│   └── reviews_scores/
├── database.py
├── manage.py
├── requirements.txt
└── db.sqlite3
```

## Setup

Clone the repository:

```bash
git clone https://github.com/sabbirhosen44/Booking-Attractions.git
cd Booking-Attractions
```

Create and activate a virtual environment:

```bash
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

Place the Booking.com JSON data inside the `data/` directory:

```
data/
├── attraction_details/
├── reviews/
└── reviews_scores/
```

Then run:

```bash
python3 manage.py import_attractions
```

The importer will automatically:

- Create database tables (if needed)
- Import attraction details
- Import reviews
- Import review score breakdowns

## Author

Author: Md Sabbir Hosen