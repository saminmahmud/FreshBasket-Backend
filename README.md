# DRF Starter Template

A modern DRF starter template with user authentication, custom user model, and image upload functionality.

## Features

✨ **Key Features:**
- **Django** - Latest Django framework
- **Custom User Model** - Extended Django AbstractUser with image field
- **User Authentication** - Django-allauth + dj_rest_auth integration for authentication
- **Image Upload** - Pillow integration for image handling with automatic cleanup
- **Environment Variables** - python-decouple for secure configuration
- **Static Files & Media** - Properly configured static and media directories
- **Admin Interface** - Pre-configured Django admin with custom fieldsets

### Authentication
- django-allauth + dj_rest_auth handles signup, login, and social authentication
- Configured templates in `templates/` directory
- Email verification available

### Admin Configuration (users/admin.py)
CustomUserAdmin uses fieldsets to organize admin form:
```python
fieldsets = UserAdmin.fieldsets + (
    (None, {'fields': ('image',)}),
)
```

## Static Files & Media

- **Static files** - CSS, JavaScript, images at `/static/`
- **Media files** - User uploads (avatars) at `/media/`
- **django-cleanup** - Automatically removes old files when updated

## Installation

### Prerequisites
- Python >= 3.14
- pip or uv (Python package manager)

### Clone the repository
   ```bash
    git clone https://github.com/saminmahmud/DRF-Starter-Template.git . && rm -rf .git
   ```

### Setup with UV (Recommended)

1. **Install UV** (if not already installed)
   ```bash
   pip install uv
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Activate virtual environment**
   ```bash
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. **Create .env file** (for environment variables)
   ```bash
   cp .env.example .env
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

### Setup with Pip

1. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install --upgrade pip
   ```

3. **Run migrations**
   ```bash
   python manage.py migrate
   ```

4. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run development server**
   ```bash
   python manage.py runserver
   ```

   Access the application at `http://127.0.0.1:8000/api/` or `http://localhost:8000/api/`.


## Support
For issues or questions, please create an issue in the repository.

---
Happy coding! 🚀