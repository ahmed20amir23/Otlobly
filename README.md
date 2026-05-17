# 🍔 Otlobly – Food Ordering Web Application

![Flask](https://img.shields.io/badge/Flask-Python-black)
![Database](https://img.shields.io/badge/Database-MySQL-blue)
![Status](https://img.shields.io/badge/Status-Completed-success)
![License](https://img.shields.io/badge/License-Educational-lightgrey)

---

## 🚀 Overview

**Otlobly** is a modern web application built using Flask that allows users to order food, manage their orders, and handle payments, with a powerful admin dashboard for full system control.

---

## ✨ Features

### 👤 User

* Register & Login system
* Create, update, and delete orders
* Payment system
* View order and payment history

---

### Admin

* View all users
* Delete users (Cascade Delete enabled)
* View all orders
* Delete payments
* Add Products
* Full system control

---


## 📸 Screenshots

### 👤 User Dashboard
![User Dashboard](Otlobly/docs/dashboard.png)

### 👑 Admin Dashboard
![Admin Dashboard](Otlobly/docs/admin.png)

---

## 🧠 System Design

### 📊 Database Tables

* **User**
* **Product**
* **Order**
* **Payment**

---

### 🔗 Relationships

* User → Order (**1:N**)
* Product → Order (**1:N**)
* Order → Payment (**1:1**)

---

### 🔥 Advanced Concept

* **Cascade Delete**

  * Deleting a user removes all related orders and payments automatically.

---

## 🌐 Endpoints

### Authentication

* `/register`
* `/login`
* `/logout`

### User

* `/dashboard`

### Orders

* `/order`
* `/order/<id>/update`
* `/order/<id>/delete`

### Payments

* `/payment/add`
* `/payment/<id>/delete`

### Admin

* `/admin`
* `/admin/product/add`
* `/admin/user/<id>/delete`
* `/admin/payment/<id>/delete`

---

## 🛠️ Tech Stack

| Layer    | Technology           |
| -------- | -------------------- |
| Backend  | Flask (Python)       |
| Database | MySQL                |
| ORM      | SQLAlchemy           |
| Frontend | HTML, CSS, Bootstrap |

---

## ⚙️ Setup Instructions

### 1️⃣ Clone Repo

```bash
git clone https://github.com/your-username/otlobly.git
cd otlobly
```

---

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3️⃣ Environment Variables

Create `secret.env`:

```env
SQLALCHEMY_DATABASE_URI=mysql+pymysql://username:password@localhost/db_name
SECRET_KEY=your_secret_key
```

---

### 4️⃣ Run Project

```bash
python app.py
```

---

## 👑 Admin Account

| Email                                     | Password |
| ----------------------------------------- | -------- |
| [admin@gmail.com](mailto:admin@gmail.com) | 123      |

---

## 📁 Project Structure

```
Otlobly/
│
├── app.py
├── requirements.txt
├── secret.env
├── Readme.md
│
├── templates/
├── static/
│
└── docs/
    ├── ERD.png
    ├── DFD.png
    ├── Otlobly_Food_Ordering_System_Documentation.pdf
```

---

## 🧪 Future Enhancements

* 🔍 Search & filtering
* 📊 Analytics dashboard
* 🔐 JWT Authentication
* 🌐 REST API

---

## 👨‍💻 Author

Developed by **Ahmed's** 

---

## 📄 License

This project is for educational purposes only.
