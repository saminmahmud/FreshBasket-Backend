# FreshBasket Backend
A scalable, production-ready grocery delivery backend built with **Django**, **Django REST Framework**, **Django Channels**, and **Celery**. FreshBasket provides REST APIs together with real-time order tracking, asynchronous background task processing, Redis-powered caching, and containerized local development with Docker.

## Features

*   **User Management**: JWT-based authentication, user registration with email verification, and distinct user roles (Customer, Delivery Partner, Admin).
*   **Product Catalog**: Complete CRUD operations for products and categories. Data is cached using Redis to reduce database queries and improve API response times.
*   **Advanced Filtering & Search**: Filter products by category and price range, with full-text search on product names.
*   **Order Processing**: 
    *   Create and manage orders with support for Cash on Delivery and online payments via SSLCommerz.
    * Order confirmation emails are sent in the background using Celery.
*   **Stock Management**: 
    *   Automatic stock reduction upon order confirmation and restoration upon cancellation.
    * Low-stock notification emails are automatically sent to administrators.
*   **Delivery Workflow**:
    *   Admins can confirm and assign orders to delivery partners or cancel them.
    *   Delivery partners can update order statuses (Packed, Out for Delivery, Delivered).
    *   OTP-based verification for confirming deliveries.
*   **Order Tracking**: Customers can track order status and the delivery partner's live location using a unique tracking code.
*   **Reviews & Ratings**: Authenticated users who have purchased a product can leave reviews and ratings.
*   **Payment Integration**: Seamless payment processing with SSLCommerz.
*   **Cloud Media Storage**: Uses Cloudinary for efficient storage and delivery of product images and user avatars.
*   **API Documentation**: Auto-generated, interactive API documentation available with Swagger UI and Redoc.
* **Real-time Order Tracking**:
    * Live delivery partner location updates using Django Channels, WebSockets, and Redis.
    * Public order tracking using a unique tracking code.
    * Delivery partners can start and stop live location sharing.
    * Customers receive real-time rider location updates without refreshing the page.
* **Containerized Development**: Docker and Docker Compose support for consistent local development.
*   **Deployment Ready**: Configured for easy deployment on Render.

## Technology Stack

* **Backend**: Django, Django REST Framework, Django Channels, Celery
* **Database**: PostgreSQL
* **Caching & Message Broker**: Redis
* **Authentication**: JWT, Django AllAuth
* **Real-time**: WebSockets, Uvicorn
* **Payment**: SSLCommerz
* **Media Storage**: Cloudinary
* **Containerization**: Docker
* **Deployment**: Render, WhiteNoise
* **API Documentation**: Swagger UI, Redoc

## Project Structure

The project is organized into modular Django apps for clear separation of concerns:

```
├── apps/
│   ├── home/
│   ├── users/
│   ├── products/
│   └── orders/
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── celery.py
├── docker-compose.yml
├── Dockerfile
├── static/
└── templates/
```

## API Overview
   *   **Base URL**: `https://freshbasket-backend-vn3f.onrender.com/api/`
   * **Base WebSocket URL**: `wss://freshbasket-backend-vn3f.onrender.com/ws/`

#### Documentation:
   *   **Swagger UI**: `https://freshbasket-backend-vn3f.onrender.com/api/schema/swagger-ui/`
   *   **Redoc**: `https://freshbasket-backend-vn3f.onrender.com/api/schema/redoc/`


## Setup and Installation

Follow these steps to set up the project locally for development.

## Clone the repository:
```bash
git clone https://github.com/saminmahmud/FreshBasket-Backend.git
cd FreshBasket-Backend
```
## Setup with Docker
```bash
docker compose up --build
```

The following services will start automatically:

- Django Backend
- Redis
- Celery Worker
---

## Setup with UV 

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
   # Redis must be running before starting the Django server.
   uvicorn config.asgi:application --reload
   ```
---

### Setup with Pip (Alternative)

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

3. **Create .env file**
   ```bash
   cp .env.example .env
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   # Ensure Redis is running before starting the Django server.
   uvicorn config.asgi:application --reload
   ```
Access the application at `http://localhost:8000/`.

---
## Environment Variables

The following environment variables are required for the application to run. They should be defined in a `.env` file in the project root.

| Variable                  | Description                                                               |
| ------------------------- | ------------------------------------------------------------------------- |
| `DEBUG`                   | Set to `True` for development, `False` for production.                    |
| `ALLOWED_HOSTS`           | Comma-separated list of allowed hostnames.                                |
| `CSRF_TRUSTED_ORIGINS`    | Comma-separated list of trusted frontend origins.                         |
| `CORS_ALLOWED_ORIGINS`    | Comma-separated list of allowed frontend origins for CORS.                |
| `SECRET_KEY`              | Your Django secret key.                                                   |
| `EMAIL`                   | Email address for sending verification and notification emails.           |
| `EMAIL_PASSWORD`          | App-specific password for the email account (e.g., for Gmail).            |
| `FRONTEND_URL`            | The base URL of your frontend application.                                |
| `BACKEND_URL`             | The base URL of this backend application.                                 |
| `STORE_ID`                | Your SSLCommerz store ID.                                                 |
| `STORE_PASSWORD`          | Your SSLCommerz store password.                                           |
| `CLOUD_NAME`              | Your Cloudinary cloud name.                                               |
| `CLOUDINARY_API_KEY`      | Your Cloudinary API key.                                                  |
| `CLOUDINARY_API_SECRET`   | Your Cloudinary API secret.                                               |
| `DATABASE_URL`            | The connection URL for your PostgreSQL database.  
| `REDIS_URL`               | The connection URL for your Redis instance.                               |

## 🔐 Authentication & Roles
The system uses JWT authentication.

Roles:
* Customer
    * Browse products
    * Place orders
    * Leave reviews for purchased products
    * Track order status
    * View delivery partner live location
* Delivery Partner
    * Share live location
    * Update delivery status
* Admin 
    * full system control                    

## 🔄 Key Workflows
🛒 Order Flow
- User places order
- Send order confirmation email
- Stock is reduced automatically & low-stock email sent if needed
- Admin assigns delivery partner
- Delivery partner updates status
- OTP confirms delivery
- Delivery partner starts live location sharing
- Customer tracks rider in real time

💳 Payment Flow
- Choose Cash on Delivery or SSLCommerz
- Payment confirmed → order marked paid
- Failed payment → stock restored if needed

⭐ Review Flow
- Only verified buyers can review products
- Ratings update product average score

## 🤝 Contributing
Contributions are welcome! Please fork the repository and create a pull request with your changes.

Happy coding! 🚀
