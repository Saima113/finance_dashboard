from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import sys
import threading
import time
from datetime import datetime
from database_manager import DatabaseManager
from data_fetcher import FinancialDataFetcher
from ml_analyzer import FinancialAnalyzer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Configuration
API_KEY = "ghfkffu6378382826hhdjgk"
BASE_URL = "https://bluemutualfund.in/server/api/company.php"

DB_CONFIG = {
    'host': 'localhost',
    'database': 'finance',
    'user': 'root',
    'password': 'hoodn'  
}

# Initialize components
db_manager = DatabaseManager(**DB_CONFIG)
fetcher = FinancialDataFetcher(API_KEY, BASE_URL)
analyzer = FinancialAnalyzer()

# Global analysis status
analysis_status = {
    'running': False,
    'current_company': '',
    'progress': 0,
    'total': 0
}

@app.route('/')
def home():
    """Home page - main search interface"""
    return render_template('index.html')

@app.route('/pages/company.php')
def company_analysis():
    """Individual company analysis page"""
    company_id = request.args.get('id', '').upper()
    if not company_id:
        return redirect(url_for('home'))
    
    # Get analysis data
    analysis_data = db_manager.get_company_analysis(company_id)
    
    # If no analysis exists, trigger background analysis
    if not analysis_data or not analysis_data.get('pros') and not analysis_data.get('cons'):
        trigger_single_analysis(company_id)
    
    return render_template('company.html', 
                         company_id=company_id,
                         analysis=analysis_data)

@app.route('/view_all.html')
def view_all():
    """View all companies page"""
    companies = db_manager.get_all_companies()
    return render_template('view_all.html', companies=companies)

@app.route('/api/company/<company_id>')
def api_company_data(company_id):
    """API endpoint for company analysis data"""
    analysis_data = db_manager.get_company_analysis(company_id.upper())
    return jsonify(analysis_data)

@app.route('/api/refresh/<company_id>', methods=['POST'])
def refresh_company_analysis(company_id):
    """Refresh analysis for a specific company"""
    try:
        company_id = company_id.upper()
        
        # Run analysis in background thread
        thread = threading.Thread(target=analyze_company_background, args=(company_id,))
        thread.daemon = True
        thread.start()
        
        return jsonify({'status': 'success', 'message': f'Analysis refresh started for {company_id}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/status')
def get_analysis_status():
    """Get current analysis status"""
    return jsonify(analysis_status)

@app.route('/api/companies')
def api_all_companies():
    """API endpoint for all companies data"""
    companies = db_manager.get_all_companies()
    return jsonify(companies)

@app.route('/api/batch_analysis', methods=['POST'])
def start_batch_analysis():
    """Start batch analysis for all companies"""
    if analysis_status['running']:
        return jsonify({'status': 'error', 'message': 'Analysis already running'}), 400
    
    try:
        # Load company list
        companies = load_company_list()
        
        # Start batch analysis in background
        thread = threading.Thread(target=run_batch_analysis_background, args=(companies,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'status': 'success', 
            'message': f'Batch analysis started for {len(companies)} companies'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/docs')
def api_documentation():
    """API documentation page"""
    return render_template('api_docs.html')

@app.errorhandler(404)
def not_found(error):
    """Custom 404 error page"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Custom 500 error page"""
    return render_template('500.html'), 500

# Background Analysis Functions
def trigger_single_analysis(company_id):
    """Trigger analysis for a single company in background"""
    if not analysis_status['running']:
        thread = threading.Thread(target=analyze_company_background, args=(company_id,))
        thread.daemon = True
        thread.start()

def analyze_company_background(company_id):
    """Analyze a single company in background thread"""
    try:
        print(f"Starting background analysis for {company_id}")
        
        # Fetch data
        raw_data = fetcher.fetch_company_data(company_id)
        if not raw_data:
            print(f"Failed to fetch data for {company_id}")
            return
        
        # Process data
        processed_data = fetcher.process_financial_statements(raw_data)
        if not processed_data:
            print(f"Failed to process data for {company_id}")
            return
        
        # Store company
        company_name = processed_data.get('company_name', company_id)
        db_manager.store_company(company_id, company_name)
        
        # Perform analysis
        analysis_result = analyzer.analyze_financial_health(processed_data)
        insights = analyzer.generate_insights(processed_data)
        
        # Store results
        db_manager.store_analysis_results(
            company_id,
            analysis_result['pros'],
            analysis_result['cons'],
            insights,
            analysis_result['metrics']
        )
        
        print(f"Analysis completed for {company_id}")
        
    except Exception as e:
        print(f"Error in background analysis for {company_id}: {e}")

def run_batch_analysis_background(companies):
    """Run batch analysis in background"""
    global analysis_status
    
    analysis_status['running'] = True
    analysis_status['total'] = len(companies)
    analysis_status['progress'] = 0
    
    try:
        for i, company_id in enumerate(companies):
            if not analysis_status['running']:  # Check if stopped
                break
                
            analysis_status['current_company'] = company_id
            analysis_status['progress'] = i + 1
            
            analyze_company_background(company_id)
            time.sleep(2)  # Rate limiting
            
    except Exception as e:
        print(f"Error in batch analysis: {e}")
    finally:
        analysis_status['running'] = False
        analysis_status['current_company'] = ''
        print("Batch analysis completed")

def load_company_list():
    """Load company list from Excel or fallback to hardcoded list"""
    try:
        companies = fetcher.load_company_list("Nifty100Companies.xlsx")
        if companies:
            return companies
    except Exception as e:
        print(f"Error loading Excel file: {e}")
    
    # Fallback company list
    return [
        'TCS', 'HDFCBANK', 'DMART', 'INFOSYS', 'WIPRO', 'RELIANCE',
        'SBIN', 'ICICIBANK', 'BHARTIARTL', 'HINDUNILVR', 'KOTAKBANK',
        'LT', 'ASIANPAINT', 'MARUTI', 'BAJFINANCE', 'NESTLEIND',
        'TECHM', 'TITAN', 'AXISBANK', 'HCLTECH', 'ULTRACEMCO',
        'SUNPHARMA', 'ONGC', 'NTPC', 'POWERGRID', 'COALINDIA'
    ]

# Template filters
@app.template_filter('datetime')
def datetime_filter(value, format='%Y-%m-%d %H:%M'):
    if value is None:
        return ''
    return value.strftime(format)

@app.template_filter('currency')
def currency_filter(value):
    if value is None:
        return '₹0'
    return f"₹{value:,.0f}"

@app.template_filter('percentage')
def percentage_filter(value):
    if value is None:
        return '0%'
    return f"{value:.1f}%"

if __name__ == '__main__':
    # Initialize database connection
    db_manager.connect()
    
    print(" ML Financial Analysis Web Application")
    print("=" * 50)
    print(" Starting web server...")
    print(" Database connected")
    print(" API configured")
    print(" Ready to serve requests")
    print("=" * 50)
    print(" Access the application at: http://localhost:5000")
    print(" API documentation at: http://localhost:5000/api/docs")
    print("=" * 50)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
    finally:
        db_manager.close_connection()
        print("👋 Server stopped")
