
# Hotel Bix API

This project is a hotel reservation management system, where you can make room reservations, view made reservations, view available rooms, and view occupied rooms.

## Technologies Used

- Python
- Django
- Django REST Framework
- Celery
- Redis
- PostgreSQL

## Environment Setup

### Prerequisites

- Python 3.10
- Docker

### Entity Relationship Diagram (ERD)

The project's database structure is outlined in the [Entity Relationship Diagram (ERD)](erd.png). It visually represents the schema, relationships, and constraints.


### Architecture
This project is organized in apps, and each app has its own responsibility.

The apps are:
- **authentication**: Where the JWT token is generated and refreshed.
- **bookings**: Where the bookings are made, confirmed, and canceled.
- **checkins**: Where check-ins and check-outs are managed.
- **rooms**: Where rooms are created and availability is checked.
- **users**: Where users are created.

We also have:
- **hotel_api**: The main project settings.
- **fixtures**: A directory containing initial data to populate the database. You can run:

    ```bash
    python manage.py loaddata fixtures/users_fixtures.json
    python manage.py loaddata fixtures/rooms_fixtures.json
    python manage.py loaddata fixtures/bookings_fixtures.json
    python manage.py loaddata fixtures/checkins_fixtures.json
    ```

    Remember to run these commands in this order, as the data has dependencies.

Inside each app, you will find core `.py` files:
- **models.py**: Defines database models.
- **serializers.py**: Converts models to JSON and validates information.
- **repositories.py**: Executes database queries.
- **services.py**: Contains business logic and calls the repositories.
- **views.py**: Defines API views and calls the services.
- **urls.py**: Defines API routes.

Some apps also have a `tasks.py` file for defining Celery tasks.

Additionally, there's a **utils.py** module containing:
- Custom exceptions
- Custom permissions
- Email services
- A custom handler for exceptions

The **unit_tests** directory contains tests for the project. Run `pytest` to execute them.

The `docker-compose` file includes:
- A PostgreSQL container
- A Redis container
- A Celery container
- A Celery Beat container
- The Web container

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/itsmevicot/hotel_bix_api.git
    ```

2. Create and activate a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Configure environment variables:

    Create a `.env` file in the project root and fill it as per `.env_example`. To generate a secure SECRET_KEY, run:

    ```bash
    python manage.py shell
    from django.core.management.utils import get_random_secret_key
    get_random_secret_key()
    ```

    Copy the output as your SECRET_KEY. Configure SMTP server settings to send emails; [see this blog post](https://dev.to/abderrahmanemustapha/how-to-send-email-with-django-and-gmail-in-production-the-right-way-24ab) for Gmail SMTP.

5. Run Docker:

    ```bash
    docker-compose up -d --build
    ```

6. Access the Web container bash:

    ```bash
    docker exec -it bix_hotel_api-web-1 bash
    ```

7. Run migrations:

    ```bash
    python manage.py migrate
    ```

You're ready to go! Access `localhost:8000/docs` or `localhost:8000/redoc` to view API documentation.

### User Registration and Authentication

1. Register at `/users/register/`. Valid CPF, email, and age above 18 are required.
2. Obtain a JWT token at `/token/` and use it in the Authorization header with the Bearer prefix for other routes.

### Main Endpoints

- **/bookings/** (POST): Make a booking.
- **/bookings/** (GET): View bookings.
- **/rooms/availability/filter/** (GET): Check room availability.
- **/bookings/{booking_id}/confirm/** (POST): Confirm booking.
- **/bookings/{booking_id}/cancel/** (POST): Cancel booking.
- **/bookings/{booking_id}/checkin/** (POST): Check-in.
- **/bookings/{booking_id}/checkout/** (POST): Check-out.

The JWT token expires in 60 minutes. Refresh it at `/token/refresh/` as needed.

### API Collection

To facilitate testing, an [API collection](api_collection.json) is available. If you choose to import on Postman, there's already a test environment
with the necessary variables to test it, so you just have to import the collection, generate the token, and start testing!

