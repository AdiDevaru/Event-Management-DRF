# Event-Management-DRF
This is a Django-based REST API for an event management system that allows users to create and manage events, RSVP to events, and handle user profiles with the ability to upload profile pictures. It also includes JWT-based authentication and supports private and public events with invitations for private ones.

## Features
- JWT Authentication
- Event creation and management (public and private events)
- Invitations for private events
- RSVP system for events
- Review system for events
- User profile with image upload
- Search filtering for events
- Pagination for events and reviews
- CRUD operations for UserProfile and Event models

## Setup Instructions

### 1. Prerequisites

- Python 3.8+ installed
- Django 4.x installed
- PostgreSQL or any other database (or use SQLite for simplicity)
- `pip` for package management

### 2. Clone the Repository

```bash
git clone https://github.com/AdiDevaru/Event-Management-DRF.git
cd Event-Management-DRF
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a Superuser
```bash
python manage.py createsuperuser
```

### 6. Run the Development Server
```bash
python manage.py runserver
```
