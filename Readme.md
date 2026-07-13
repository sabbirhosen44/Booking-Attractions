# Booking Attractions

A Django-based data importer that processes Booking.com Attractions datasets and stores them in PostgreSQL with PostGIS support. The importer supports attractions, localized content, photos, reviews, and review score breakdowns using streaming JSON parsing, batch processing, parallel execution, and bulk upsert operations.

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
* PostgreSQL database support
* PostGIS support for future GeoDjango spatial features
* Dockerized development environment
* Conflict-safe bulk upserts for PostgreSQL


## Tech Stack

* Python 3.12+
* Django ORM
* PostgreSQL 16
* PostGIS 3.4
* Docker & Docker Compose
* ijson
* Psycopg


## Project Structure

```text
booking_attraction/
├── apps/
│   └── attractions/
│       ├── management/
│       │   └── commands/
│       │       └── import_attractions.py
│       ├── migrations/
│       ├── models.py
│       ├── services.py
│       ├── db_services.py
│       ├── apps.py
│       └── __init__.py
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
├── docker/
│   └── django/
│       └── Dockerfile
│
├── docker-compose.yml
├── manage.py
├── requirements.txt
├── README.md
└── .gitignore
```


## Setup
```

Clone the repository:

```bash
git clone https://github.com/sabbirhosen44/Booking-Attractions.git
cd Booking-Attractions
```

Copy the configuration file:

```bash
cp core/app_config.toml.example core/app_config.toml
```

Build Docker containers:

```bash
docker compose build
```

Start services:

```bash
docker compose up -d
```

Run migrations:

```bash
docker compose exec web python manage.py migrate
```

## Data Directory

Place the Booking.com JSON files inside:

```text
data/
├── attraction_details/
├── reviews/
└── reviews_scores/
```



`
## Configuration

Create a local configuration file:

```bash
cp core/app_config.toml.example core/app_config.toml
```

## Run Import

```bash
docker compose exec web python manage.py import_attractions
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
