# Clario — Odoo OCR Invoice Processing Addon

Clario OCR is an Odoo 17 addon designed to automate supplier invoice and receipt processing using **AI-powered Optical Character Recognition (OCR)**.

The module integrates **Microsoft Azure Document Intelligence** with Odoo Accounting to extract structured financial data from invoices and receipts. Extracted data is automatically used to generate **draft vendor bills**, significantly reducing manual data entry and improving accounting efficiency.

This project was originally developed as a **Senior Project (SP2)** at **Assumption University**, and has since evolved into a deployable Odoo module.

---

## Features

### Current Features

* OCR invoice processing using **Azure Document Intelligence**
* Automatic extraction of:

  * Vendor name
  * Invoice reference
  * Date
  * Subtotal
  * VAT
  * Total amount
* Vendor matching with existing partners
* Automatic creation of **draft vendor bills**
* VAT and subtotal validation logic
* Multi-currency support
* Secure Azure API configuration via Odoo settings
* Fully Dockerized development environment

---

### Planned Enhancements

* Advanced line-item extraction
* AI confidence scoring
* Thai OCR improvements
* Vendor detection based on historical invoices
* Invoice analytics dashboard
* Fraud / risky invoice detection
* LINE OA integration for mobile invoice uploads

---

## Tech Stack

| Component     | Technology                            |
| ------------- | ------------------------------------- |
| ERP Engine    | Odoo 17                               |
| OCR Engine    | Microsoft Azure Document Intelligence |
| Backend       | Python (Odoo ORM)                     |
| Database      | PostgreSQL 15                         |
| Environment   | Docker & Docker Compose               |
| UI            | Odoo XML Views                        |
| Collaboration | GitHub                                |

---

## Project Structure

```
odoo-17-clario-ocr/
│
├── addons/
│   └── clario_ocr/
│       ├── models/
│       ├── views/
│       ├── security/
│       ├── static/
│       ├── __manifest__.py
│       └── __init__.py
│
├── odoo-conf/
│   └── odoo.conf
│
├── docker-compose.yml
└── README.md
```

---

## Environment Requirements

Clario OCR requires an Odoo environment that supports **third-party modules**.

### Supported environments:

* Odoo.sh (official cloud hosting)
* On-premise Odoo installations

### Not supported:

* Odoo Online (SaaS)

The SaaS version does not allow custom modules and therefore cannot run Clario OCR.

---

## Installation & Setup

The recommended method for development and testing is using **Docker**.

Only **Docker Desktop** is required — no manual Odoo installation is needed.

---

### 1️. Clone the Repository

```bash
git clone https://github.com/harry-lynnoo/odoo-17-clario-ocr.git
cd odoo-17-clario-ocr
```

---

### 2️. Start the Odoo Environment

```bash
docker compose up -d
```

This will start:

* Odoo 17
* PostgreSQL 15
* Clario OCR addon

---

### 3. Open Odoo

Open your browser:

```
http://localhost:8069
```

Create a database (example):

* Database name: `clario_dev`
* Email: any
* Password: any

---

### 4. Install Clario OCR Module

Inside Odoo:

1. Open **Apps**
2. Remove all filters
3. Click **Update Apps List**
4. Search:

```
Clario OCR
```

5. Click **Install**

---

## Azure OCR Configuration

Clario OCR requires **Microsoft Azure Document Intelligence**.

After installing the module:

1. Go to **Settings**
2. Open **Clario OCR Settings**
3. Enter:

   * API Endpoint
   * API Key
4. Click **Save**

---

### Azure Free Tier

Microsoft Azure provides a **free tier**:

* Up to **500 pages per month**

Additional usage will follow Azure pricing.

---

## OCR Workflow

1. Upload an invoice or receipt
2. Document is processed via Azure OCR
3. Data is extracted and validated
4. Draft vendor bill is generated
5. User reviews and confirms

---

## Developer Workflow

Restart Odoo after code changes:

```bash
docker compose restart odoo
```

View logs:

```bash
docker compose logs -f odoo
```

Stop services:

```bash
docker compose down
```

Rebuild if needed:

```bash
docker compose down
docker compose up -d --build
```

---

## Team Contribution Workflow

Pull latest changes:

```bash
git pull origin main
```

Create a feature branch:

```bash
git checkout -b feature/your-feature
```

Push your branch:

```bash
git push -u origin feature/your-feature
```

Commit changes:

```bash
git add .
git commit -m "Your commit message"
git push
```

Then open a **Pull Request → Review → Merge**

---

## .gitignore Rules

```
db-data/
__pycache__/
*.log
*.pyc
*.pyo
.env
```

Prevents:

* Large database files
* Cache
* Logs
* Secrets

---

## Odoo Marketplace

Clario OCR is designed to be distributed via the **Odoo Apps Marketplace**.

The module is available as a **one-time purchase** and can be used in:

* Odoo.sh
* On-premise Odoo

---

## Authors

Clario Team — Assumption University:

* Thu Ya Myint Myat Thein
* S Harry Lynn Oo
* Hein Htet Moe Tun

---

## Support

For inquiries:

```
ootunthein6969@gmail.com
```