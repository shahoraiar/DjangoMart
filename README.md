# DjangoMart

DjangoMart is a simple online shopping website built with Django.  
Anyone can browse products, add them to a cart, register, pay online, and track orders.

This document explains how the project works in easy English.

---

## What is this project?

DjangoMart is an e-commerce demo with:

- Product store and categories
- Guest cart and logged-in cart
- Email OTP registration
- Forgot password with OTP
- Checkout with SSLCommerz payment (sandbox)
- Order history, transactions, and settings
- Modern admin panel (Django Unfold)

---

## How to run the project

```bash
cd DjangoMart
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open:

- Website: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

Create an admin user if needed:

```bash
python manage.py createsuperuser
```

---

## Project apps (simple map)

| App | What it does |
|-----|----------------|
| `category` | Categories and products |
| `store` | Store pages, product detail, search |
| `cart` | Add / remove cart items |
| `accounts` | Register, login, OTP, profile, settings |
| `orders` | Place order and SSLCommerz payment |
| `Django_Mart` | Main project settings and home page |

---

## Unique features (what makes this project special)

### 1) Guest cart uses session (saved in database)

When a visitor is **not logged in**, the cart still works.

1. Django creates a **session key** for the browser.
2. A `Cart` row is saved in the database with that session key as `cart_id`.
3. Each product goes into `CartItem` linked to that cart.

So guest cart data is **not only in browser memory**. It is stored in the database.

### 2) Registration moves guest cart to the new user

This is an important unique flow:

1. Guest adds products to cart.
2. Guest registers (email + password).
3. System sends an OTP email.
4. After OTP is verified, the account becomes active.
5. Guest cart items are moved to the new authenticated user.

Meaning: products added before signup are not lost after registration.

### 3) Login does not steal guest cart

If someone already has an account:

- Login shows **that user’s own cart**
- Guest cart is **not merged** into the account
- Guest cart is kept for later (session key is reattached after login/logout)

So:

- **Register** = transfer guest cart to new user  
- **Login** = keep user cart as it is

### 4) Email OTP for registration and password reset

Registration is not finished until OTP is verified.

- OTP is sent by Gmail SMTP
- OTP is valid for **5 minutes**
- User can resend OTP
- Verify page has a live countdown timer
- Email is sent in a nice HTML format

Forgot password also uses OTP:

1. Enter email  
2. Get OTP  
3. Verify OTP  
4. Set new password  

### 5) Payment with SSLCommerz

After checkout form:

1. Order is saved
2. User goes to SSLCommerz payment page
3. On success, payment + order products are saved
4. Cart is cleared
5. Stock is reduced
6. User is redirected to **My order history**

### 6) User dashboard

After login, Profile area includes:

- **My order history** – completed orders from database
- **Transactions** – payment list
- **Settings** – update username/name (email cannot be changed)
- **Received orders** – paid order list

### 7) Modern Unfold admin

Admin panel uses **django-unfold** for a cleaner UI.  
Open `/admin/` with a staff/superuser account.

---

## Full shopping flow (step by step)

1. Open home or store page  
2. Add products to cart (as guest or logged-in user)  
3. Go to cart and review items  
4. If guest: Register → verify OTP  
5. Place order (billing form)  
6. Pay with SSLCommerz sandbox  
7. See order in Profile → My order history  

---

## Cart system in one picture

```text
Guest user
  browser session key
       |
       v
  Cart table (cart_id = session key)
       |
       v
  CartItem (product + quantity)

After Registration + OTP success
  CartItem.user = new user
  guest Cart is cleaned

After Login
  show CartItem where user = logged-in user
  guest cart stays separate
```

---

## Auth pages

| URL | Purpose |
|-----|---------|
| `/account/register/` | Sign up + send OTP |
| `/account/verify-otp/` | Verify OTP |
| `/account/signin/` | Login |
| `/account/forgot-password/` | Request reset OTP |
| `/account/reset-password/` | Set new password |
| `/account/profile/` | Order history |
| `/account/transactions/` | Payments |
| `/account/settings/` | Profile settings |
| `/account/logout/` | Logout |

---

## Order and payment notes

- Tax is calculated as **2%** of cart total
- Payment gateway settings are stored in `PaymentGateWaySettings` (store id / password)
- Sandbox mode is used for testing
- Successful payments redirect to order history, not only cart

---

## Important technical notes

1. **Session change on login/logout**  
   Django changes session key after login and logout.  
   This project re-links guest cart to the new session key so guest items do not disappear.

2. **Email cannot be edited in Settings**  
   Email is shown as read-only for safety.

3. **Footer stays at bottom**  
   Even if a page has little content, footer stays down.

4. **Pagination warning fixed**  
   Product lists use `order_by('id')` so page results stay stable.

---

## Main technologies

- Python + Django
- SQLite database
- Pillow (product images)
- SSLCommerz (payment)
- Django Unfold (admin UI)
- Gmail SMTP (OTP emails)

---

## Folder overview

```text
DjangoMart/
├── accounts/      # auth, OTP, profile dashboard
├── cart/          # cart logic
├── category/      # category + product models
├── store/         # store pages
├── orders/        # checkout + payment
├── templates/     # shared templates (base, home)
├── static/        # css, js, images
├── media/         # uploaded product photos
├── manage.py
├── requirements.txt
└── README.md
```

---

## What to test manually

1. Add products as guest → register → verify OTP → cart should still have products  
2. Add products as guest → login existing user → see only that user’s cart  
3. Logout → guest cart should come back (same browser session flow)  
4. Place order → pay in sandbox → check Profile and Transactions  
5. Open `/admin/` and manage products/orders  

---

## Summary

DjangoMart is a full mini e-commerce flow.  
The most unique parts are:

- session-based guest cart saved in DB  
- cart transfer only on registration  
- OTP email verification  
- SSLCommerz checkout  
- clean order dashboard and Unfold admin  

If you are new to Django, start from Home → Store → Cart → Register → Order → Profile. That path shows almost every important feature.
