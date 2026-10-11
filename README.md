# 📊 GaussifyAPI

A modular, production-ready Flask REST API that answers a fundamental statistical question: **given a mean ($\mu$), a standard deviation ($\sigma$), and a target value ($x$), what is the probability of landing at or below that value on a Gaussian (Normal) distribution?**

$$P(X \le x) = \frac{1}{\sigma \sqrt{2\pi}} \int_{-\infty}^{x} e^{-\frac{(t - \mu)^2}{2\sigma^2}} \, dt$$

GaussifyAPI computes the cumulative probability using **SciPy**, renders the bell curve with the shaded probability area using **Matplotlib**, and stores full calculation history in **SQLite** via **SQLAlchemy**.

---

## 💡 Why a Normal Distribution API?

The Gaussian (Normal) distribution is a cornerstone of statistics, data science, and machine learning:
- **Feature Scaling & Standardization**: $Z$-score transformations rely directly on $\mu$ and $\sigma$.
- **Probabilistic Modeling**: Algorithms like Gaussian Naive Bayes and Gaussian Mixture Models model continuous variables using bell curves.
- **Statistical Inference & Hypothesis Testing**: $p$-values, confidence intervals, and A/B test evaluations depend on cumulative distribution functions ($CDF$).

While formulas are easy to read in textbooks, visualizing the area under the curve makes probability intuitive: input three parameters, receive the exact mathematical probability, and get an immediate visual representation of where that value sits on the distribution.

---

## 📸 Visualization Example

Every calculation generates a high-resolution, area-shaded bell curve chart encoded as a base64 string:

![Normal Distribution with cumulative probability area highlighted](assets/example-chart.png)

*The blue curve represents the probability density function (PDF), the red dashed line marks the target value $x$, and the shaded indigo region represents the cumulative probability $P(X \le x)$.*

---

## 🏗️ Architecture & Project Structure

The project is structured following Flask's **Application Factory** pattern with a strict separation of concerns between core scientific computation and web infrastructure:

```
GaussifyAPI/
├── api/                       # Web & persistence layer
│   ├── __init__.py            # Application factory (create_app) & error handlers
│   ├── extensions.py          # SQLAlchemy database instance
│   ├── models.py              # Calculation ORM model & DB constraints
│   └── routes.py              # RESTful API endpoints (/api/calculations)
│
├── core/                      # Domain logic (zero Flask / HTTP dependencies)
│   ├── __init__.py            # Clean interface export
│   └── services.py            # SciPy CDF calculations & Matplotlib rendering
│
├── tests/                     # Automated test suite (54 tests, >95% coverage)
│   ├── conftest.py            # Pytest fixtures & test client setup
│   ├── test_models.py         # Database model & constraint tests
│   ├── test_routes.py         # HTTP routes, status codes & validation tests
│   ├── test_services.py       # Math accuracy & chart generation tests
│   └── test_database_integrity.py  # SQLite constraint enforcement tests
│
├── assets/                    # Static assets & documentation images
│   └── example-chart.png
│
├── config.py                  # Environment-specific configuration classes
├── run.py                     # Application entry point for development
├── verify_db.py               # Database integrity verification script
├── Makefile                   # Convenient CLI task shortcuts
├── requirements.txt           # Project dependencies
└── .env.example               # Environment variables template
```

### Key Design Principles

1. **Decoupled Math Engine (`core/`)**: The calculation and plotting routines are completely independent of Flask or any database. They take raw numeric inputs and return pure data and image buffers, making them individually testable and portable.
2. **Headless Chart Generation**: Matplotlib is configured to use the headless `Agg` backend, safely rendering figures in non-GUI / server environments without memory leaks (buffers are explicitly closed).
3. **Database Constraints & Integrity**: SQLite enforces positive standard deviations (`std_dev > 0`) and valid probability bounds (`0 <= probability <= 1`) at the database level via Check Constraints, alongside indexed timestamps for fast chronological sorting.
4. **Centralized Error Handling**: Standardized JSON responses for `400 Bad Request`, `404 Not Found`, and `500 Internal Server Error`.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ (tested up to Python 3.14)
- `pip` and virtual environment support (`venv`)

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/joaopinheiroc/GaussifyAPI.git
cd GaussifyAPI

python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
# or using Makefile:
make install
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Open `.env` and set `SECRET_KEY`:
```env
SECRET_KEY=your-generated-secret-key-here
```

### 4. Run the Server

```bash
python run.py
# or using Makefile:
make run
```

The server will start at `http://127.0.0.1:5000`. The SQLite database (`instance/gaussify.db`) is initialized automatically on first startup.

---

## 📡 API Reference

Base URL: `http://127.0.0.1:5000/api/calculations`

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/calculations` | Compute a new probability, save record, and return result + chart |
| `GET` | `/api/calculations` | List all past calculations (chronological, newest first) |
| `GET` | `/api/calculations/<id>` | Get calculation details by ID (includes dynamically rendered chart) |
| `DELETE` | `/api/calculations/<id>` | Delete a calculation from history |

---

### 1. Calculate & Store Probability

Computes $P(X \le \text{target x})$, persists the calculation, and renders the bell curve chart.

- **URL**: `POST /api/calculations`
- **Headers**: `Content-Type: application/json`
- **Request Body**:

```json
{
  "mean": 100.0,
  "std_dev": 15.0,
  "target_x": 130.0
}
```

- **Validation Rules**:
  - `mean`: Required float/int.
  - `std_dev`: Required float/int, must be **strictly greater than 0**.
  - `target_x`: Required float/int.

#### Example Request:
```bash
curl -X POST http://127.0.0.1:5000/api/calculations \
  -H "Content-Type: application/json" \
  -d '{"mean": 100, "std_dev": 15, "target_x": 130}'
```

#### Success Response (`201 Created`):
```json
{
  "id": 1,
  "mean": 100.0,
  "std_dev": 15.0,
  "target_x": 130.0,
  "probability": 0.9772498680518208,
  "created_at": "2026-10-11T12:00:00+00:00",
  "chart_base64": "iVBORw0KGgoAAAANSUhEUgAABQAAA..."
}
```

#### Error Response (`400 Bad Request`):
```json
{
  "error": "Standard deviation must be greater than zero."
}
```

---

### 2. List Calculations History

Returns all calculations ordered by creation date (newest first). To keep payloads lightweight and fast, the list view omits the heavy base64 chart strings.

- **URL**: `GET /api/calculations`

#### Example Request:
```bash
curl -X GET http://127.0.0.1:5000/api/calculations
```

#### Success Response (`200 OK`):
```json
[
  {
    "id": 2,
    "mean": 0.0,
    "std_dev": 1.0,
    "target_x": 1.96,
    "probability": 0.9750021048517795,
    "created_at": "2026-10-11T12:05:00+00:00"
  },
  {
    "id": 1,
    "mean": 100.0,
    "std_dev": 15.0,
    "target_x": 130.0,
    "probability": 0.9772498680518208,
    "created_at": "2026-10-11T12:00:00+00:00"
  }
]
```

---

### 3. Get Calculation Details

Fetches a specific calculation by its ID and dynamically generates its base64 chart.

- **URL**: `GET /api/calculations/<id>`

#### Example Request:
```bash
curl -X GET http://127.0.0.1:5000/api/calculations/1
```

#### Success Response (`200 OK`):
```json
{
  "id": 1,
  "mean": 100.0,
  "std_dev": 15.0,
  "target_x": 130.0,
  "probability": 0.9772498680518208,
  "created_at": "2026-10-11T12:00:00+00:00",
  "chart_base64": "iVBORw0KGgoAAAANSUhEUgAABQAAA..."
}
```

#### Error Response (`404 Not Found`):
```json
{
  "error": "Calculation not found."
}
```

---

### 4. Delete Calculation

Deletes a calculation record from the database.

- **URL**: `DELETE /api/calculations/<id>`

#### Example Request:
```bash
curl -X DELETE http://127.0.0.1:5000/api/calculations/1
```

#### Success Response (`200 OK`):
```json
{
  "message": "Calculation 1 deleted sucessfully"
}
```

---

## 🖼️ Displaying the Chart in Frontend

The returned `chart_base64` string is a standard PNG image encoded in base64.

### In HTML / React:
```html
<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAABQAAA..." alt="Normal Distribution Chart" />
```

### In Python (Save as Image File):
```python
import base64

chart_data = response.json()["chart_base64"]
with open("chart.png", "wb") as f:
    f.write(base64.b64decode(chart_data))
```

---

## 🛡️ Database & Data Integrity

The API enforces data integrity at both the application and database layers:

- **Check Constraints (`api/models.py`)**:
  - `check_std_dev_positive`: Guarantees `std_dev > 0`.
  - `check_probability_range`: Guarantees `probability >= 0 AND probability <= 1`.
- **Indexed Timestamps**: The `created_at` field is indexed to ensure fast chronological queries.

### Integrity Verification CLI

A dedicated verification script checks database health and validates all records:

```bash
python verify_db.py
# or using Makefile:
make verify-db
```

Output:
```text
============================================================
DATABASE INTEGRITY REPORT
============================================================
Total calculations: 12
Issues found: 0

✓ No integrity issues found!
✓ All constraints are being enforced properly
✓ Database is healthy
```

---

## 🧪 Testing & Quality Assurance

The project includes an automated test suite with **54 tests** covering routes, services, database constraints, error handlers, and edge cases.

### Running Tests

```bash
# Run all tests
pytest tests/ -v
# or
make test

# Run tests with code coverage report
pytest tests/ -v --cov=api --cov=core --cov-report=term-missing
# or
make test-cov

# Run specific test modules
pytest tests/test_routes.py -v
pytest tests/test_models.py -v
pytest tests/test_services.py -v
pytest tests/test_database_integrity.py -v
```

---

## 🛠️ Makefile Commands

A `Makefile` is provided to streamline development:

| Command | Description |
|---|---|
| `make help` | Show all available commands |
| `make install` | Install dependencies from `requirements.txt` |
| `make run` | Start the development server |
| `make test` | Run test suite with pytest |
| `make test-cov` | Run tests and generate HTML and terminal coverage reports |
| `make verify-db` | Run database integrity checks |
| `make lint` | Check code style with flake8 (if installed) |
| `make clean` | Clean up `__pycache__`, coverage files, and temporary artifacts |

---

## 📦 Tech Stack

| Technology | Purpose |
|---|---|
| **Python** | Core programming language |
| **Flask** | Lightweight WSGI web framework & routing |
| **Flask-SQLAlchemy** | ORM for database modeling and query execution |
| **SQLite** | Zero-configuration relational database |
| **SciPy (`scipy.stats.norm`)** | Cumulative Distribution Function ($CDF$) computation |
| **NumPy** | Array generation for curve coordinates |
| **Matplotlib** | Data visualization & figure rendering (`Agg` backend) |
| **pytest & pytest-cov** | Automated unit/integration testing & coverage tracking |
| **python-dotenv** | Environment variable management |

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
