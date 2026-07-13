# Booking Attractions

A Django-based data importer that processes Booking.com Attractions datasets and stores them in a SQLite database. The importer supports attractions, localized content, photos, reviews, and review score breakdowns with efficient batch processing, streaming JSON parsing, and bulk database operations.

## Features

* Import attraction details
* Import localized names and descriptions
* Import attraction photos
* Import attraction reviews
* Import review score breakdowns
* Batch processing for large datasets
* Streaming JSON parsing using `ijson`
* Bulk create and upsert operations
* Thread-safe database writes
* Dedicated database service layer
* Centralized configuration using TOML

## Tech Stack

* Python 3.12+
* Django ORM
* SQLite
* ijson

## Project Structure

```text
```text
booking_attraction/
├── apps/
│   ├── attractions/
│      ├── management/
│      │   └── commands/
│      │       └── import_attractions.py
│      ├── migrations/
│      ├── models.py
│      ├── services.py
│      ├── db_services.py
│      ├── apps.py
│      └── __init__.py
│
│
├── core/
│   ├── utils/
│   │   ├── attraction_row_builder.py
│   │   ├── batch_buffer.py
│   │   ├── import_config.py
│   │   ├── locked_write.py
│   │   └── skip_counter.py
│   │
│   ├── app_config.toml.example
│   ├── configuration.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
│   └── __init__.py
│
├── data/
│   ├── attraction_details/
│   ├── reviews/
│   └── reviews_scores/
│
├── db.sqlite3
├── manage.py
├── requirements.txt
├── README.md
└── .gitignore
```

```

## Setup

Clone the repository:

```bash
git clone https://github.com/sabbirhosen44/Booking-Attractions.git
cd Booking-Attractions
```

Create and activate a virtual environment:

```bash
python3 -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
python3 manage.py migrate
```

## Data Directory

Place the Booking.com JSON files inside:

```text
data/
├── attraction_details/
├── reviews/
└── reviews_scores/
```

## Configuration

Application configuration :

```text
Change config/app_config.toml.example to  config/app_config.toml
```

## Run Import

```bash
python3 manage.py import_attractions
```

The importer will automatically process:

* Attraction details
* Localized content
* Photos
* Reviews
* Review score breakdowns



This includes environment, database, and import-related settings.

## Author

Author: Md Sabbir Hosen
