import time
import sys
from data_fetcher import FinancialDataFetcher
from ml_analyzer import FinancialAnalyzer
from database_manager import DatabaseManager
from typing import List

class FinancialAnalysisSystem:
    def __init__(self):
        # API Configuration
        self.api_key = "ghfkffu6378382826hhdjgk"
        self.base_url = "https://bluemutualfund.in/server/api/company.php"
        
        # Database Configuration
        self.db_config = {
            'host': 'localhost',
            'database': 'finance',
            'user': 'root',
            'password': 'your_password'  # Update with your MySQL password
        }
        
        # Initialize components
        self.fetcher = FinancialDataFetcher(self.api_key, self.base_url)
        self.analyzer = FinancialAnalyzer()
        self.db_manager = DatabaseManager(**self.db_config)
        
        # Connect to database
        self.db_manager.connect()
    
    def load_companies(self, excel_path: str = "Nifty100Companies.xlsx") -> List[str]:
        """Load company list from Excel file"""
        companies = self.fetcher.load_company_list(excel_path)
        if not companies:
            # Fallback to hardcoded list if Excel not available
            companies = [
                'TCS', 'HDFCBANK', 'DMART', 'INFOSYS', 'WIPRO', 'RELIANCE',
                'SBIN', 'ICICIBANK', 'BHARTIARTL', 'HINDUNILVR', 'KOTAKBANK',
                'LT', 'ASIANPAINT', 'MARUTI', 'BAJFINANCE'
            ]
        print(f"Loaded {len(companies)} companies for analysis")
        return companies
    
    def analyze_single_company(self, company_id: str) -> bool:
        """Analyze a single company and store results"""
        print(f"\n{'='*50}")
        print(f"Analyzing: {company_id}")
        print(f"{'='*50}")
        
        # Fetch data
        raw_data = self.fetcher.fetch_company_data(company_id)
        if not raw_data:
            print(f"❌ Failed to fetch data for {company_id}")
            return False
        
        # Process data
        processed_data = self.fetcher.process_financial_statements(raw_data)
        if not processed_data:
            print(f" Failed to process data for {company_id}")
            return False
        
        # Store company info
        company_name = processed_data.get('company_name', company_id)
        self.db_manager.store_company(company_id, company_name)
        
        # Perform ML analysis
        analysis_result = self.analyzer.analyze_financial_health(processed_data)
        insights = self.analyzer.generate_insights(processed_data)
        
        # Display results in terminal
        print(f"\n Analysis Results for {company_name} ({company_id})")
        print(f" Insights: {insights}")
        
        print(f"\n Pros ({len(analysis_result['pros'])}):")
        for i, pro in enumerate(analysis_result['pros'], 1):
            print(f"   {i}. {pro}")
        
        print(f"\n Cons ({len(analysis_result['cons'])}):")
        for i, con in enumerate(analysis_result['cons'], 1):
            print(f"   {i}. {con}")
        
        # Store in database
        self.db_manager.store_analysis_results(
            company_id,
            analysis_result['pros'],
            analysis_result['cons'],
            insights,
            analysis_result['metrics']
        )
        
        print(f" Analysis completed and stored for {company_id}")
        return True
    
    def run_batch_analysis(self, companies: List[str], delay: float = 2.0):
        """Run analysis for multiple companies"""
        total_companies = len(companies)
        successful_analyses = 0
        failed_analyses = 0
        
        print(f"\n Starting batch analysis for {total_companies} companies")
        print(f"  Delay between requests: {delay} seconds")
        
        for i, company_id in enumerate(companies, 1):
            print(f"\n Progress: {i}/{total_companies} ({(i/total_companies)*100:.1f}%)")
            
            try:
                if self.analyze_single_company(company_id):
                    successful_analyses += 1
                else:
                    failed_analyses += 1
                
                # Add delay between requests to avoid rate limiting
                if i < total_companies:
                    time.sleep(delay)
                    
            except KeyboardInterrupt:
                print(f"\n Analysis interrupted by user")
                break
            except Exception as e:
                print(f" Unexpected error analyzing {company_id}: {e}")
                failed_analyses += 1
        
        # Final summary
        print(f"\n{'='*60}")
        print(f" BATCH ANALYSIS COMPLETE")
        print(f"{'='*60}")
        print(f" Successful: {successful_analyses}")
        print(f" Failed: {failed_analyses}")
        print(f" Success Rate: {(successful_analyses/total_companies)*100:.1f}%")
        print(f"{'='*60}")
    
    def interactive_mode(self):
        """Interactive mode for single company analysis"""
        print("\n Interactive Analysis Mode")
        print("Enter company symbols (or 'quit' to exit)")
        
        while True:
            company_id = input("\nEnter company ID: ").strip().upper()
            
            if company_id.lower() in ['quit', 'exit', 'q']:
                break
            
            if not company_id:
                continue
            
            self.analyze_single_company(company_id)
    
    def shutdown(self):
        """Clean shutdown"""
        self.db_manager.close_connection()
        print("\n👋 System shutdown complete")

def main():
    """Main execution function"""
    system = FinancialAnalysisSystem()
    
    try:
        print(" ML Financial Analysis System")
        print("=" * 40)
        
        if len(sys.argv) > 1:
            mode = sys.argv[1].lower()
            
            if mode == 'batch':
                # Batch analysis mode
                companies = system.load_companies()
                system.run_batch_analysis(companies)
            
            elif mode == 'interactive':
                # Interactive mode
                system.interactive_mode()
            
            elif mode.startswith('company='):
                # Single company mode
                company_id = mode.split('=')[1].upper()
                system.analyze_single_company(company_id)
            
            else:
                print("Usage: python main.py [batch|interactive|company=SYMBOL]")
        
        else:
            # Default: show options
            print("Select mode:")
            print("1. Batch analysis (all companies)")
            print("2. Interactive mode")
            print("3. Web app mode")
            
            choice = input("\nEnter choice (1/2/3): ").strip()
            
            if choice == '1':
                companies = system.load_companies()
                system.run_batch_analysis(companies)
            elif choice == '2':
                system.interactive_mode()
            elif choice == '3':
                print("Starting web application...")
                print("Visit: http://localhost:5000")
                # Import and run web app
                from web_app import app
                app.run(debug=True)
            else:
                print("Invalid choice")
    
    except KeyboardInterrupt:
        print("\n  Operation cancelled by user")
    except Exception as e:
        print(f" System error: {e}")
    finally:
        system.shutdown()

if __name__ == "__main__":
    main()