# Car Marketplace Backend

FastAPI backend for the Car Marketplace project. It provides authentication, car listings, rentals, purchase inquiries and messaging, sale completion, image uploads, and admin management.

## Requirements

- Python 3.14 or newer
- PostgreSQL
- Docker and Docker Compose (for the full-stack Docker setup)

## Environment variables

Copy the example file and set a private JWT secret:

```bash
cp .env.example .env
```

Generate a secret with:

```bash
openssl rand -hex 32
```

Set the generated value as `JWT_SECRET_KEY` in `.env`. Do not commit `.env` or share its secret.

`DATABASE_URL` is required when running the API directly. For Docker Compose, the API's database URL is configured to use the Compose PostgreSQL service; the host `DATABASE_URL` value is not used by that container.

## Run with Docker Compose

From the backend directory:

```bash
cp .env.example .env
# Edit .env and set JWT_SECRET_KEY.
docker compose up --build -d
docker compose exec api alembic upgrade head
```

The Compose file also builds the frontend from `../frontend`. The API is available at <http://localhost:8000>, interactive API documentation at <http://localhost:8000/docs>, and the frontend at <http://localhost:5173>.

PostgreSQL data and uploaded images are stored in Docker volumes.

To stop the services without deleting their data:

```bash
docker compose down
```

## Run the API directly

Create and activate a virtual environment, install dependencies, and make sure PostgreSQL is running with the database URL configured in `.env`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

On Windows PowerShell, activate the virtual environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## Authentication

Register with `POST /users/`. Log in at `POST /auth/login` using form fields `username` and `password`. The response contains a bearer access token. Send it on protected endpoints as:

```text
Authorization: Bearer <access_token>
```

Newly registered accounts have the `user` role. To provision the initial administrator, register that account, then promote it directly in PostgreSQL:

```sql
UPDATE users SET role = 'admin' WHERE username = 'your-admin-username';
```

After an administrator exists, admins can manage user roles through the admin API.

## Main API routes

Use `/docs` for request and response schemas for all routes.

### Cars

- `GET /cars/` — browse and filter cars
- `GET /cars/for-sale` — browse unsold sale listings
- `GET /cars/for-rent` — browse unsold rental listings
- `GET /cars/my-listings` — view your unsold listings
- `POST /cars/` — create a listing
- `GET /cars/{car_id}` — view a car
- `PUT /cars/{car_id}` — update your listing
- `DELETE /cars/{car_id}` — delete your listing

### Rentals

- `POST /rentals/` — create a rental
- `GET /rentals/` — view your rentals
- `PATCH /rentals/{rental_id}/cancel` — cancel your rental

### Purchase inquiries and sale

- `POST /purchase-inquiries/` — start an inquiry; an optional initial message is accepted
- `GET /purchase-inquiries/mine` — view your inquiries as a buyer
- `GET /purchase-inquiries/for-my-cars` — view inquiries for your listings
- `GET /purchase-inquiries/{inquiry_id}/messages` — view conversation messages
- `POST /purchase-inquiries/{inquiry_id}/messages` — send a message
- `PATCH /purchase-inquiries/{inquiry_id}/status` — seller accepts or rejects an inquiry
- `POST /purchase-inquiries/{inquiry_id}/complete` — seller records completion of an accepted sale

Sale completion does not process payment. It marks the car sold, transfers its owner to the buyer, and closes other active inquiries.

### Administration

These routes require an administrator bearer token:

- `GET /admin/users` — list users
- `DELETE /admin/users/{user_id}` — delete a user and associated records
- `PUT /admin/users/{user_id}/password` — set a user's password
- `PATCH /admin/users/{user_id}/role` — change a user's role
- `GET /admin/cars` — list all cars, including sold cars
- `DELETE /admin/cars/{car_id}` — delete any car listing

### Images

- `POST /cars/cars/{car_id}/images` — upload a car image
- `GET /cars/cars/{car_id}/images` — list images for a car

## Database migrations

Apply migrations with Alembic:

```bash
alembic upgrade head
```

With Docker Compose:

```bash
docker compose exec api alembic upgrade head
```
