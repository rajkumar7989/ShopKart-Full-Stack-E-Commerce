# 🛒 ShopKart – Full Stack E-Commerce Website

ShopKart is a full-stack e-commerce web application developed using **Python Flask, MySQL, HTML, CSS, and JavaScript**.

The application provides a complete online shopping workflow including user registration, authentication, product browsing, cart management, checkout, order tracking, and an admin dashboard for managing products and orders.

## 🚀 Features

### 👤 Customer Features

- User Registration
- Secure User Login
- Password Hashing
- User Logout
- Browse Products
- Search Products
- Category Filtering
- Product Details
- Add Products to Cart
- Increase / Decrease Product Quantity
- Remove Products from Cart
- User-specific Shopping Cart
- Checkout
- Customer Details
- Delivery Address
- Payment Method Selection
- Order Placement
- Order Success Page
- My Orders
- Order Status Tracking

### 👨‍💼 Admin Features

- Admin Login
- Admin Dashboard
- Total Products
- Total Customers
- Total Orders
- Total Sales
- Recent Orders
- Add Products
- Edit Products
- Upload Product Images
- Activate Products
- Deactivate Products
- Manage Products
- Manage Orders
- Update Order Status

### Order Statuses

- Pending
- Confirmed
- Shipped
- Out for Delivery
- Delivered
- Cancelled

## 🛠️ Tech Stack

### Frontend

- HTML5
- CSS3
- JavaScript

### Backend

- Python
- Flask

### Database

- MySQL

### Other Technologies

- Jinja2 Templates
- Flask Sessions
- Werkzeug Password Hashing
- python-dotenv
- Git
- GitHub

## 📂 Project Structure

```text
ShopKart/
│
├── app.py
├── .env
├── .gitignore
├── README.md
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── images/
│
└── templates/
    ├── index.html
    ├── products.html
    ├── product.html
    ├── cart.html
    ├── checkout.html
    ├── order_success.html
    ├── orders.html
    ├── login.html
    ├── register.html
    ├── admin.html
    ├── admin_products.html
    ├── add_product.html
    ├── edit_product.html
    └── admin_orders.html
