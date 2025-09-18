"""
ML Financial Analysis - Batch Runner
Execute this script to run comprehensive analysis on all Nifty 100 companies
"""

import sys
import time
import argparse
from datetime import datetime
from data_fetcher import FinancialDataFetcher
import database_manager
from ml_analyzer import FinancialAnalyzer
from database_manager import DatabaseManager

class AnalysisRunner:
    def __init__(self):
        # Configuration
        self.api_key = "ghfkffu6378382826hhdjgk"
        self.base_url = "https://bluemutualfund.in/server/api/company.php"
        
        self.db_config = {
            'host': 'localhost',
            'database': 'finance',
            'user': 'root',
            'password': 'hoodn'  # Update this
        }
        
        # Initialize components
        self.fetcher = FinancialDataFetcher(self.api_key, self.base_url)
        self.analyzer = FinancialAnalyzer()
        self.db_manager = DatabaseManager(**self.db_config)
        
        # Statistics
        self.stats = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'start_time': None,
            'end_time': None
        }
    
    def setup(self):
        """Initialize database connection and setup"""
        print(" Setting up analysis environment...")
        self.db_manager.connect()
        print(" Database connected")
        print(" API configured")
        print(" ML analyzer ready")
    
    def load_companies(self):
        """Load company list"""
        print(" Loading company list...")
        
        # Try to load from Excel first
        companies = self.fetcher.load_company_list("company_id.xlsx")
        
        if not companies:
            print("⚠️  Excel file not found, using default company list")
            companies = [
                'TCS', 'HDFCBANK', 'DMART', 'INFOSYS', 'WIPRO', 'RELIANCE',
                'SBIN', 'ICICIBANK', 'BHARTIARTL', 'HINDUNILVR', 'KOTAKBANK',
                'LT', 'ASIANPAINT', 'MARUTI', 'BAJFINANCE', 'NESTLEIND',
                'TECHM', 'TITAN', 'AXISBANK', 'HCLTECH', 'ULTRACEMCO',
                'SUNPHARMA', 'ONGC', 'NTPC', 'POWERGRID', 'COALINDIA',
                'INDUSINDBK', 'BRITANNIA', 'DRREDDY', 'EICHERMOT',
                'BAJAJFINSV', 'CIPLA', 'GRASIM', 'SHREECEM', 'HINDALCO'
            ]
        
        print(f" Loaded {len(companies)} companies for analysis")
        return companies
    
    def analyze_company(self, company_id: str) -> bool:
        """Analyze a single company"""
        try:
            print(f"\n{'='*60}")
            print(f" Analyzing: {company_id}")
            print(f"{'='*60}")
            
            # Fetch data
            print(f" Fetching data from API...")
            raw_data = self.fetcher.fetch_company_data(company_id)
            if not raw_data:
                print(f" Failed to fetch data for {company_id}")
                return False
            
            print(f" Data fetched successfully")
            
            # Process data
            print(f" Processing financial statements...")
            processed_data = self.fetcher.process_financial_statements(raw_data)
            if not processed_data:
                print(f" Failed to process data for {company_id}")
                return False
            
            # Store company info
            company_name = processed_data.get('company_name', company_id)
            self.db_manager.store_company(company_id, company_name)
            print(f" Company info stored: {company_name}")
            
            # Perform ML analysis
            print(f" Running ML analysis...")
            analysis_result = self.analyzer.analyze_financial_health(processed_data)
            insights = self.analyzer.generate_insights(processed_data)
            
            # Display results
            print(f"\n Analysis Results for {company_name} ({company_id})")
            print(f" Insights: {insights}")
            
            print(f"\n Pros ({len(analysis_result['pros'])}):")
            for i, pro in enumerate(analysis_result['pros'], 1):
                print(f"   {i}. {pro}")
            
            print(f"\n Cons ({len(analysis_result['cons'])}):")
            for i, con in enumerate(analysis_result['cons'], 1):
                print(f"   {i}. {con}")
            
            # Store in database
            print(f" Storing analysis results...")
            self.db_manager.store_analysis_results(
                company_id,
                analysis_result['pros'],
                analysis_result['cons'],
                insights,
                analysis_result['metrics']
            )
            
            print(f" Analysis completed and stored for {company_id}")
            print(f" View online: http://localhost:5000/pages/company.php?id={company_id}")
            
            return True
            
        except Exception as e:
            print(f" Error analyzing {company_id}: {e}")
            return False
    
    def run_batch_analysis(self, companies: list[str], delay: float = 2.0):
        """Run batch analysis for all companies"""
        self.stats['total'] = len(companies)
        self.stats['start_time'] = datetime.now()
        
        print(f"\n Starting Batch Analysis")
        print(f"{'='*70}")
        print(f" Total Companies: {len(companies)}")
        print(f"  Delay per request: {delay} seconds")
        print(f" Started at: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")
        
        for i, company_id in enumerate(companies, 1):
            print(f"\n Progress: {i}/{len(companies)} ({(i/len(companies))*100:.1f}%)")
            print(f" ETA: {self._calculate_eta(i, len(companies), self.stats['start_time'], delay)}")
            
            try:
                if self.analyze_company(company_id):
                    self.stats['successful'] += 1
                else:
                    self.stats['failed'] += 1
                
                # Rate limiting
                if i < len(companies):
                    print(f"  Waiting {delay} seconds...")
                    time.sleep(delay)
                    
            except KeyboardInterrupt:
                print(f"\n  Analysis interrupted by user at company {i}/{len(companies)}")
                break
            except Exception as e:
                print(f" Unexpected error with {company_id}: {e}")
                self.stats['failed'] += 1
        
        self.stats['end_time'] = datetime.now()
        self._print_final_summary()
    
    def _calculate_eta(self, current, total, start_time, delay):
        """Calculate estimated time of arrival"""
        elapsed = (datetime.now() - start_time).total_seconds()
        if current == 0:
            return "Calculating..."
        
        avg_time_per_company = elapsed / current
        remaining_companies = total - current
        eta_seconds = remaining_companies * (avg_time_per_company + delay)
        
        hours = int(eta_seconds // 3600)
        minutes = int((eta_seconds % 3600) // 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def _print_final_summary(self):
        """Print final analysis summary"""
        duration = self.stats['end_time'] - self.stats['start_time']
        
        print(f"\n{'='*70}")
        print(f" BATCH ANALYSIS COMPLETE")
        print(f"{'='*70}")
        print(f" Successful: {self.stats['successful']}")
        print(f" Failed: {self.stats['failed']}")
        print(f" Success Rate: {(self.stats['successful']/self.stats['total'])*100:.1f}%")
        print(f" Total Duration: {duration}")
        print(f" Completed at: {self.stats['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f" View results: http://localhost:5000/view_all.html")
        print(f"{'='*70}")
    
    def interactive_mode(self):
        """Interactive analysis mode"""
        print(f"\n Interactive Analysis Mode")
        print(f"{'='*40}")
        print("Commands:")
        print("  - Enter company symbol to analyze")
        print("  - 'batch' to run batch analysis")
        print("  - 'list' to show all companies")
        print("  - 'status' to show current status")
        print("  - 'quit' to exit")
        print(f"{'='*40}")
        
        while True:
            try:
                command = input("\n Enter command: ").strip().upper()
                
                if command.lower() in ['quit', 'exit', 'q']:
                    break
                elif command.lower() == 'batch':
                    companies = self.load_companies()
                    self.run_batch_analysis(companies)
                elif command.lower() == 'list':
                    self._show_company_list()
                elif command.lower() == 'status':
                    self._show_status()
                elif command:
                    self.analyze_company(command)
                else:
                    print(" Invalid command. Try again.")
                    
            except KeyboardInterrupt:
                print(f"\n Interactive mode interrupted")
                break
            except Exception as e:
                print(f" Error: {e}")
    
    def _show_company_list(self):
        """Show list of available companies"""
        companies = database_manager.get_all_companies()
        print(f"\n Available Companies ({len(companies)}):")
        for company in companies[:20]:  # Show first 20
            status ="done" if company.get('analysis_date') else "not done"
            print(f"  {status} {company['symbol']} - {company.get('company_name', 'Unknown')}")
        
        if len(companies) > 20:
            print(f"  ... and {len(companies) - 20} more companies")
    
    def _show_status(self):
        """Show current system status"""
        companies = database_manager.get_all_companies()
        analyzed = len([c for c in companies if c.get('analysis_date')])
        
        print(f"\n System Status:")
        print(f"   Total Companies: {len(companies)}")
        print(f"   Analyzed: {analyzed}")
        print(f"   Pending: {len(companies) - analyzed}")
        print(f"   Analysis Running: {'Yes' if AnalysisRunner['running'] else 'No'}")
        
        if AnalysisRunner['running']:
            print(f"   Current: {AnalysisRunner['current_company']}")
            print(f"   Progress: {AnalysisRunner['progress']}/{AnalysisRunner['total']}")
    
    def cleanup(self):
        """Clean shutdown"""
        self.db_manager.close_connection()
        print("\n👋 Analysis runner shutdown complete")

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='ML Financial Analysis Runner')
    parser.add_argument('mode', nargs='?', choices=['batch', 'interactive', 'web'], 
                       default='interactive', help='Analysis mode')
    parser.add_argument('--company', help='Analyze specific company')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between API calls')
    
    args = parser.parse_args()
    
    runner = AnalysisRunner()
    
    try:
        runner.setup()
        
        if args.company:
            # Single company analysis
            runner.analyze_company(args.company.upper())
        
        elif args.mode == 'batch':
            # Batch analysis
            companies = runner.load_companies()
            runner.run_batch_analysis(companies, args.delay)
        
        elif args.mode == 'interactive':
            # Interactive mode
            runner.interactive_mode()
        
        elif args.mode == 'web':
            # Start web application
            print(" Starting web application...")
            print(" Visit: http://localhost:5000")
            from web_app import app
            app.run(debug=True, threaded=True)
        
    except KeyboardInterrupt:
        print(f"\n⏹  Operation cancelled by user")
    except Exception as e:
        print(f"❌ System error: {e}")
    finally:
        runner.cleanup()

if __name__ == "__main__":
    main()
