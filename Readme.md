# Booking Attractions

A data importer that processes Booking.com Attractions datasets and loads them into a database, using streaming/batch/parallel processing. The project contains **two parallel, independent pipelines** that do the same job into two different storage backends, built so the team can compare them:

1. **Postgres pipeline** — Django ORM + `psqlextra`, writes into a partitioned PostgreSQL/PostGIS schema.
2. **Iceberg pipeline** — PySpark, writes into local filesystem-backed Apache Iceberg tables via a Hadoop catalog.

Both pipelines read the exact same source files under `data/` and populate the same logical entities (attractions, localized content, photos, reviews, review scores, price history, skipped/unmatched records) — just into different targets.

## Features

* Import attraction details
* Import localized names and descriptions
* Import attraction photos
* Import attraction reviews
* Import review score breakdowns
* Import price/date snapshots
* Batch processing for large datasets
* Streaming JSON parsing using `ijson`
* Bulk create and upsert operations (Postgres)
* Iceberg `MERGE INTO` upserts (Iceberg pipeline)
* Thread-safe database writes
* Dedicated database service layer
* Centralized configuration using TOML
* PostgreSQL database support
* PostGIS support for spatial data
* Apache Iceberg support via PySpark + Hadoop catalog
* Dockerized development environment
* Conflict-safe bulk upserts for PostgreSQL
* Jupyter notebook support for inspecting Iceberg data


## Tech Stack

* Python 3.12+
* Django ORM
* PostgreSQL 16
* PostGIS 3.4
* Docker & Docker Compose
* ijson
* Psycopg
* PySpark 3.5.4
* Apache Iceberg (Spark runtime jar 1.6.1, Scala 2.12)
* Jupyter Notebook


## Project Structure

```text
booking_attraction/
├── apps/
│   └── attractions/
│       ├── management/
│       │   └── commands/
│       │       ├── import_attractions.py
│       │       └── import_attractions_iceberg.py
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
│   │   ├── review_row_builder.py
│   │   ├── price_row_builder.py
│   │   ├── location_resolver.py
│   │   ├── partition_manager.py
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
├── pyspark_etl/
│   ├── config.py
│   ├── session.py
│   ├── pipeline.py
│   ├── services.py
│   ├── catalog/
│   │   ├── schema_defs.py
│   │   ├── tables.py
│   │   └── align.py
│   ├── schemas/
│   │   └── source.py
│   ├── readers/
│   │   ├── json_reader.py
│   │   └── location_mapping_reader.py
│   ├── transforms/
│   │   ├── slug.py
│   │   ├── rental_property.py
│   │   ├── property_reviews.py
│   │   └── price_history.py
│   └── writers/
│       └── iceberg_writer.py
│
├── data/
│   ├── attraction_details/
│   ├── reviews/
│   ├── reviews_scores/
│   ├── search/
│   └── static/
│       └── location_mapping/
│
├── spark_pipeline/
│   └── warehouse/          # local Iceberg warehouse (generated at runtime)
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

> Note: if the `attractions` app has changes to partitioned models, use `python manage.py pgmakemigrations` instead of `makemigrations` — plain `makemigrations` generates a non-partitioned table for `PostgresPartitionedModel` subclasses.


## Data Directory

Place the Booking.com JSON files inside:

```text
data/
├── attraction_details/<date>/changed/*.json
├── reviews/<date>/changed/*.json
├── reviews_scores/<date>/changed/*.json
├── search/<date>/changed/*.json
└── static/
    └── location_mapping/
        └── <country_code>/
            ├── city.json
            ├── district.json
            ├── landmark.json
            └── region.json
```


## Configuration

Create a local configuration file:

```bash
cp core/app_config.toml.example core/app_config.toml
```

For the Iceberg pipeline, `core/app_config.toml` also needs an `[iceberg]` section:

```toml
[iceberg]
warehouse_dir = "spark_pipeline/warehouse"
catalog_name = "booking"
database = "attractions"
```


## Run Import — Postgres Pipeline

```bash
docker compose exec web python manage.py import_attractions
```

The importer will automatically process, in order:

* Attraction details
* Localized content
* Photos
* Reviews
* Review score breakdowns
* Price/date snapshots

Reviews and search records that reference an attraction not yet imported are logged to `SkipProperties` rather than failing the run.


## Run Import — Iceberg / PySpark Pipeline

```bash
docker compose exec web python manage.py import_attractions_iceberg
```

This runs the same import logic against Apache Iceberg tables (local filesystem storage, Hadoop catalog) instead of PostgreSQL. It can be run independently of, and without interfering with, the Postgres pipeline — both read from the same `data/` folder but write to entirely separate storage.

Each Iceberg table mirrors the full column set of its corresponding Django model (not just the fields this importer populates), so schema stays comparable across both pipelines.

> If `pyspark_etl/catalog/schema_defs.py` changes (columns added/removed), existing Iceberg tables do **not** auto-migrate. Delete `spark_pipeline/warehouse/` and re-run the importer from scratch after any schema change.


## Inspecting Iceberg Data with Jupyter Notebook

Since Iceberg data is stored as partitioned Parquet files, the most reliable way to inspect it is to query it back through Spark (rather than opening `.parquet` files directly, which won't render as text).

**1. Make sure `jupyter`, `pandas`, and `pyarrow` are in `requirements.txt`, then rebuild:**

```bash
docker compose build web
docker compose up -d
```

**2. Launch the notebook server inside the running container:**

```bash
docker compose exec web jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root
```

Copy the printed URL (including the `?token=...` part) into your browser, e.g.:

```
http://127.0.0.1:8888/tree?token=<token>
```

> Requires port `8888` to be mapped in `docker-compose.yml` under the `web` service's `ports:` section.

**3. In a new notebook cell, query a table through Spark:**

```python
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

from pyspark_etl.session import get_spark_session
spark = get_spark_session()

result = spark.sql("SELECT * FROM booking.attractions.rental_property LIMIT 20")
pdf = result.toPandas()
pdf
```

Swap `rental_property` for any other table: `rental_property_localize`, `property_image_meta`, `property_reviews`, `price_history`, `skip_properties`.

To filter by a specific country, or find which country codes exist:

```python
# Filter by country_code
spark.sql("SELECT * FROM booking.attractions.rental_property WHERE country_code = 'de' LIMIT 20").toPandas()

# List all country codes and row counts
spark.sql("SELECT country_code, COUNT(*) as count FROM booking.attractions.rental_property GROUP BY country_code ORDER BY count DESC").toPandas()
```

> Note: on child tables (`property_reviews`, `price_history`, `rental_property_localize`, `property_image_meta`, `skip_properties`), the `id` column will always show as `NaN`/`NULL`. This is expected — it exists only for column parity with the Postgres schema; Iceberg has no autoincrement to populate it. Use the table's actual foreign-key/reference columns (e.g. `property_id`) to identify rows instead.


## Author

Author: Md Sabbir Hosen