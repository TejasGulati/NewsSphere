# NewsSphere

This is a web application built using Django REST Framework for the backend, Celery for task queue management, Redis as a message broker for Celery, MySQL for the database, and Angular for the frontend.

## Table of Contents

- [Project Setup](#project-setup)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
  - [Starting the Backend](#starting-the-backend)
  - [Starting the Frontend](#starting-the-frontend)
- [Using Celery](#using-celery)
  - [Starting Celery Worker](#starting-celery-worker)
  - [Starting Celery Beat](#starting-celery-beat)
- [API Documentation](#api-documentation)
- [Frontend Build](#frontend-build)
- [License](#license)
- [CONTACT](#contact)


## Project Setup

### Backend Setup

1. **Clone the repository:**

    ```bash
    git clone https://github.com/TejasGulati/NewsSphere.git
    cd NewsSphere
    ```

2. **Create a virtual environment and activate it:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install the backend dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Setup the MySQL database:**

    Create a MySQL database and update the `DATABASES` configuration in your `settings.py` file.

    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'yourdbname',
            'USER': 'yourdbuser',
            'PASSWORD': 'yourdbpassword',
            'HOST': 'localhost',
            'PORT': '3306',
        }
    }
    ```

5. **Run database migrations:**

    ```bash
    python manage.py migrate
    ```

6. **Create a superuser for the admin panel:**

    ```bash
    python manage.py createsuperuser
    ```

### Frontend Setup

1. **Navigate to the `frontend` directory:**

    ```bash
    cd frontend
    ```

2. **Install the Angular dependencies:**

    ```bash
    npm install
    ```

## CONTACT

email:tejasgulati11227@gmail.com

## Environment Variables

Create a `.env` file in the root directory of your project and add the following environment variables:

```bash
SECRET_KEY=your_secret_key
DEBUG=True

# MySQL configuration
DB_NAME=yourdbname
DB_USER=yourdbuser
DB_PASSWORD=yourdbpassword
DB_HOST=localhost
DB_PORT=3306

# Redis configuration
REDIS_URL=redis://localhost:6379/0

#CONTACT
email:tejasgulati11227@gmail.com
