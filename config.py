API_CONFIG = {
    'base_url': 'https://bluemutualfund.in/server/api/company.php',
    'api_key': 'ghfkffu6378382826hhdjgk',
    'timeout': 30,
    'max_retries': 3
}

# Database Configuration
DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'finance',
    'user': 'root',
    'password': 'hoodn',  
    'charset': 'utf8mb4'
}

# ML Analysis Configuration
ML_CONFIG = {
    'threshold': 10.0,  # 10% threshold for pros/cons
    'max_pros': 3,
    'max_cons': 3
}

# Web App Configuration
WEB_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': True
}

# File Paths
FILE_PATHS = {
    'company_list': 'Nifty100Companies.xlsx',
    'templates': 'templates/',
    'static': 'static/'
}

## 7. Installation and Setup Instructions

### Prerequisites
# Python 3.8+
# MySQL Server
# Git (optional)

### Installation Steps

# 1. **Clone/Download Project**
#    ```bash
#    # Create project directory
#    mkdir ml_financial_analysis
#    cd ml_financial_analysis
#    ```

# 2. **Install Dependencies**
#    ```bash
#    pip install -r requirements.txt
#    ```

# 3. **Database Setup**
#    ```sql
#    -- Create database
#    CREATE DATABASE ml;
   
#    -- Update config.py with your MySQL credentials
#    ```

# 4. **Download Company List**
#    - Download the Nifty100Companies Excel file
#    - Place it in the project root directory

# 5. **Run the System**
#    ```bash
#    # Batch analysis
#    python main.py batch
   
#    # Interactive mode
#    python main.py interactive
   
#    # Single company
#    python main.py company=TCS
   
#    # Web application
#    python main.py
#    # Then select option 3
#    ```

# ### Project Structure
# ```
# ml_financial_analysis/
# ├── main.py                 # Main orchestration script
# ├── data_fetcher.py        # API integration
# ├── ml_analyzer.py         # ML analysis engine
# ├── database_manager.py    # MySQL operations
# ├── web_app.py            # Flask web application
# ├── config.py             # Configuration settings
# ├── requirements.txt      # Dependencies
# ├── Nifty100Companies.xlsx # Company list
# ├── templates/            # HTML templates
# │   ├── index.html
# │   ├── company.html
# │   └── view_all.html
# └── static/              # CSS, JS, images
#     ├── css/
#     ├── js/
#     └── images/
# ```

# ### Usage Examples

# 1. **Analyze specific company**:
#    ```bash
#    python main.py company=TCS
#    ```

# 2. **Batch process all companies**:
#    ```bash
#    python main.py batch
#    ```

# 3. **Start web interface**:
#    ```bash
#    python web_app.py
#    # Visit: http://localhost:5000
#    ```

# ### Key Features
# -  Real-time API data fetching
# -  ML-based financial analysis
# - MySQL database integration
# -  Web interface for visualization
# -  Terminal-based monitoring
# -  Batch and interactive modes
# -  Error handling and logging
# -  Company comparison features
