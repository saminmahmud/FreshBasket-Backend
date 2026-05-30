# FreshBasket Backend
A scalable and production-ready grocery delivery e-commerce backend built with **Django** and **Django REST Framework (DRF)**. FreshBasket provides a complete API for managing role-based access control, products, orders, payments, delivery workflow, and reviews.

## Features

*   **User Management**: JWT-based authentication, user registration with email verification, and distinct user roles (Customer, Delivery Partner, Admin).
*   **Product Catalog**: Complete CRUD operations for products and categories.
*   **Advanced Filtering & Search**: Filter products by category and price range, with full-text search on product names.
*   **Order Processing**: Create and manage orders with support for Cash on Delivery and online payments via SSLCommerz.
*   **Stock Management**: Automatic stock reduction upon order confirmation and restoration upon cancellation.
*   **Delivery Workflow**:
    *   Admins can confirm and assign orders to delivery partners or cancel them.
    *   Delivery partners can update order statuses (Packed, Out for Delivery, Delivered).
    *   OTP-based verification for confirming deliveries.
*   **Order Tracking**: Customers can track their order status using a unique tracking code.
*   **Reviews & Ratings**: Authenticated users who have purchased a product can leave reviews and ratings.
*   **Payment Integration**: Seamless payment processing with SSLCommerz.
*   **Cloud Media Storage**: Uses Cloudinary for efficient storage and delivery of product images and user avatars.
*   **API Documentation**: Auto-generated, interactive API documentation available with Swagger UI and Redoc.
*   **Deployment Ready**: Configured for easy deployment on Vercel.

## Technology Stack

*   **Backend**: Django, Django REST Framework
*   **Database**: PostgreSQL
*   **Authentication**: Django AllAuth, JWT, Dj-Rest-Auth
*   **API Documentation**: Swagger UI, Redoc
*   **Payment Gateway**: SSLCommerz
*   **File Storage**: Cloudinary
*   **Deployment**: Gunicorn, Whitenoise, Vercel

## Project Structure

The project is organized into modular Django apps for clear separation of concerns:

```
├── apps/
│   ├── home/        # Welcome endpoint
│   ├── users/       # User models, authentication, permissions, and roles
│   ├── products/    # Product, Category, and Review management
│   └── orders/      # Order processing, payment, and tracking
├── config/          # Django project settings and main URL configuration
├── static/          # Static assets
└── templates/       # HTML templates
```

## API Overview
   *   **Base URL**: `https://freshbasket-backend-five.vercel.app/api/`

#### Documentation:
   *   **Swagger UI**: `https://freshbasket-backend-five.vercel.app/api/schema/swagger-ui/`
   *   **Redoc**: `https://freshbasket-backend-five.vercel.app/api/schema/redoc/`


## Setup and Installation

Follow these steps to set up the project locally for development.

## Clone the repository:
```bash
git clone https://github.com/saminmahmud/FreshBasket-Backend.git
cd FreshBasket-Backend
```

## Setup with UV (Recommended)

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
   Access the application at `http://localhost:8000/`.

---

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

## 🔐 Authentication & Roles
The system uses JWT authentication.

Roles:
* Customer → browse, order, review
* Delivery Partner → update delivery status
* Admin → full system control                    

## 🔄 Key Workflows
🛒 Order Flow
- User places order
- Stock is reduced automatically
- Admin assigns delivery partner
- Delivery partner updates status
- OTP confirms delivery

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
