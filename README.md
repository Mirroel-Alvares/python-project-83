### Hexlet tests and linter status:
[![Actions Status](https://github.com/Mirroel-Alvares/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/Mirroel-Alvares/python-project-83/actions)

[![test-check](https://github.com/Mirroel-Alvares/python-project-83/actions/workflows/test-check.yml/badge.svg)](https://github.com/Mirroel-Alvares/python-project-83/actions/workflows/test-check.yml)

Maintainability and Test Coverage status:
[![Maintainability](https://api.codeclimate.com/v1/badges/9218f6e5cbffb32c8abf/maintainability)](https://codeclimate.com/github/Mirroel-Alvares/python-project-83/maintainability)

### Access to the deployed application
[You can see the web-service in action at Render] (https://python-project-83-03lm.onrender.com)

---

# Page Analyzer

**Page Analyzer** is a web application for analyzing web pages.  
It allows checking website availability and analyzing **SEO data**.

---

###  Local Run
1. **Clone the repository**:
   ```sh
   git clone https://github.com/Mirroel-Alvares/python-project-83.git
   cd python-project-83
   ```
2. **Install dependencies**:
   ```sh
   make install
   ```
3. **Set up environment variables (`.env`)**:
   ```sh
   DATABASE_URL=postgresql://user:password@localhost:5432/database
   SECRET_KEY=your_secret_key
   ```
4. **Create database tables**:
   ```sh
   make build
   ```
5. **Run the application**:
   - In **development**:  
     ```sh
     make dev
     ```
   - In **production**:  
     ```sh
     make start
     ```

6. **Open in browser**:
   - **Locally**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
   - **Deployed application**: [https://python-project-83-03lm.onrender.com](https://python-project-83-03lm.onrender.com)

---

## Requirements
- Python 3.13+
- PostgreSQL
- Flask, Requests, BeautifulSoup
- UV (dependency management)

---

## License
This project is available under the MIT license.
