# Judicial Auctions Analytics Platform

## Overview
Web platform that collects and analyzes data from Córdoba's Judicial Auctions website to provide advanced statistics and future price predictions. The system offers improved visualization tools and analytics compared to the original platform.

## Features

### Current
- Automated data collection from official auctions website
- Advanced statistics dashboard
- Historical price tracking

### Planned
- Machine learning model for auction final price prediction
- Price trend analysis
- Bidding pattern recognition
- Automated alerts system

## Tech Stack
- Backend: Django
- Frontend: Bootstrap 5
- Database: sqlite3

## Installation

```bash
# Clone repository
git clone [repository-url]

# Create virtual environment
python -m venv env
source env/bin/activate  # Linux/Mac
env\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

## Usage

1. Create an admin account:
```bash
python manage.py createsuperuser
```

2. Access the platform at `http://localhost:8000`
3. Use the sync options to start collecting auction data
4. Navigate to the statistics dashboard to view analytics

## Data Collection
The system collects:
- Auction details
- Starting prices
- Final prices
- Bidding history
