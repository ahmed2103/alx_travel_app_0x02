# alx_travel_app_0x00

## Setup Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Make migrations and migrate:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. Seed the database:
   ```bash
   python manage.py seed
   ```

## Models

- **Listing**: Travel property with title, description, price, location, owner.
- **Booking**: Booking for a listing with check-in and check-out dates.
- **Review**: Rating and comment for a listing by a user.

