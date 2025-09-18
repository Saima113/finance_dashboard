"""
Setup script for ML Financial Analysis Project
"""

import os
import sys
import subprocess
import mysql.connector
from mysql.connector import Error

def install_requirements():
    """Install required Python packages"""
    print(" Installing required packages...")
    
    requirements = [
        'pandas>=1.5.0',
        'requests>=2.28.0',
        'sqlalchemy>=1.4.0',
        'scikit-learn>=1.1.0',
        'mysql-connector-python>=8.0.0',
        'flask>=2.2.0',
        'openpyxl>=3.0.0',
        'numpy>=1.21.0'
    ]
    
    for package in requirements:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f" Installed: {package}")
        except subprocess.CalledProcessError as e:
            print(f" Failed to install {package}: {e}")
            return False
    
    return True

def setup_database():
    """Setup MySQL database and tables"""
    print("\n  Setting up database...")
    
    # Get database credentials
    host = input("MySQL Host (default: localhost): ").strip() or 'localhost'
    user = input("MySQL User (default: root): ").strip() or 'root'
    password = input("MySQL Password: ").strip()
    
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        
        cursor = connection.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS finance")
        cursor.execute("USE finance")
        
        # Create tables
        tables = {
            'companies': """
                CREATE TABLE IF NOT EXISTS companies (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    symbol VARCHAR(20) UNIQUE NOT NULL,
                    company_name VARCHAR(255),
                    sector VARCHAR(100),
                    market_cap BIGINT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """,
            'analysis': """
                CREATE TABLE IF NOT EXISTS analysis (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    company_symbol VARCHAR(20),
                    insights TEXT,
                    overall_score DECIMAL(5,2),
                    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_symbol) REFERENCES companies(symbol) ON DELETE CASCADE
                )
            """,
            'pros': """
                CREATE TABLE IF NOT EXISTS pros (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    company_symbol VARCHAR(20),
                    pro_text TEXT,
                    metric_name VARCHAR(100),
                    metric_value DECIMAL(10,2),
                    weight DECIMAL(3,2) DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_symbol) REFERENCES companies(symbol) ON DELETE CASCADE
                )
            """,
            'cons': """
                CREATE TABLE IF NOT EXISTS cons (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    company_symbol VARCHAR(20),
                    con_text TEXT,
                    metric_name VARCHAR(100),
                    metric_value DECIMAL(10,2),
                    weight DECIMAL(3,2) DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_symbol) REFERENCES companies(symbol) ON DELETE CASCADE
                )
            """
        }
        
        for table_name, create_query in tables.items():
            cursor.execute(create_query)
            print(f" Created table: {table_name}")
        
        connection.commit()
        print(f" Database 'finance' setup complete")
        
        # Update config file
        update_config_file(host, user, password)
        
        return True
        
    except Error as e:
        print(f" Database setup failed: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def update_config_file(host, user, password):
    """Update configuration files with database credentials"""
    config_updates = [
        ('database_manager.py', f"'password': '{password}'"),
        ('enhanced_web_app.py', f"'password': '{password}'"),
        ('run_analysis.py', f"'password': '{password}'")
    ]
    
    for filename, password_line in config_updates:
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    content = f.read()
                
                # Update password line
                content = content.replace("'password': 'your_password'", password_line)
                content = content.replace('"password": "your_password"', f'"password": "{password}"')
                
                with open(filename, 'w') as f:
                    f.write(content)
                
                print(f" Updated config in {filename}")
            except Exception as e:
                print(f"  Warning: Could not update {filename}: {e}")

def create_project_structure():
    """Create necessary project directories"""
    print("\n Creating project structure...")
    
    directories = [
        'templates',
        'static/css',
        'static/js',
        'static/images',
        'data',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f" Created: {directory}/")

def create_sample_data():
    """Create sample Nifty100 companies Excel file"""
    print("\n Creating sample company list...")
    
    sample_companies = [
        'TCS', 'HDFCBANK', 'DMART', 'INFOSYS', 'WIPRO', 'RELIANCE',
        'SBIN', 'ICICIBANK', 'BHARTIARTL', 'HINDUNILVR', 'KOTAKBANK',
        'LT', 'ASIANPAINT', 'MARUTI', 'BAJFINANCE', 'NESTLEIND',
        'TECHM', 'TITAN', 'AXISBANK', 'HCLTECH', 'ULTRACEMCO',
        'SUNPHARMA', 'ONGC', 'NTPC', 'POWERGRID', 'COALINDIA',
        'INDUSINDBK', 'BRITANNIA', 'DRREDDY', 'EICHERMOT',
        'BAJAJFINSV', 'CIPLA', 'GRASIM', 'SHREECEM', 'HINDALCO'
    ]
    
    try:
        import pandas as pd
        df = pd.DataFrame({'Symbol': sample_companies})
        df.to_excel('Nifty100Companies.xlsx', index=False)
        print(f" Created Nifty100Companies.xlsx with {len(sample_companies)} companies")
    except ImportError:
        print("  pandas not installed, skipping Excel file creation")

def main():
    """Main setup function"""
    print(" ML Financial Analysis Project Setup")
    
    
    # Step 1: Install requirements
    if not install_requirements():
        print(" Failed to install requirements. Please install manually.")
        return
    
    # Step 2: Create project structure
    create_project_structure()
    
    # Step 3: Setup database
    if not setup_database():
        print(" Database setup failed. Please configure manually.")
        return
    
    # Step 4: Create sample data
    create_sample_data()
    
    print(f"\n Setup Complete!")
    print(f"{'='*50}")
    print(f" Project structure created")
    print(f"  Database configured")
    print(f" Dependencies installed")
    print(f" Sample data created")
    print(f"{'='*50}")
    print(f"\n Next Steps:")
    print(f"1. Run analysis: python run_analysis.py batch")
    print(f"2. Start web app: python enhanced_web_app.py")
    print(f"3. Visit: http://localhost:5000")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
