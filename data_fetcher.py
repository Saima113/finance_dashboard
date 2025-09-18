import requests
import pandas as pd
import json
import time
from typing import Dict, List, Optional

class FinancialDataFetcher:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
    
    def fetch_company_data(self, company_id: str) -> Optional[Dict]:
        """Fetch financial data for a specific company"""
        try:
            url = f"{self.base_url}?id={company_id}&api_key={self.api_key}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            if response.text.strip():
                return response.json()
            else:
                print(f"Empty response for {company_id}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {company_id}: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON decode error for {company_id}: {e}")
            return None
    
    def process_financial_statements(self, raw_data: Dict) -> Dict:
        """Clean and structure financial data"""
        if not raw_data:
            return {}
        
        processed = {
            'company_id': raw_data.get('symbol', ''),
            'company_name': raw_data.get('companyName', ''),
            'balance_sheet': raw_data.get('balanceSheet', {}),
            'profit_loss': raw_data.get('profitLoss', {}),
            'cash_flow': raw_data.get('cashFlow', {}),
            'ratios': raw_data.get('ratios', {}),
            'growth_metrics': raw_data.get('growth', {})
        }
        
        return processed
    
    def load_company_list(self, excel_file_path: str) -> List[str]:
        """Load company IDs from Excel file"""
        try:
            df = pd.read_excel(excel_file_path)
            # Assuming the Excel has a column with company symbols
            company_ids = df['Symbol'].tolist() if 'Symbol' in df.columns else df.iloc[:, 0].tolist()
            return [str(company_id).strip() for company_id in company_ids if pd.notna(company_id)]
        except Exception as e:
            print(f"Error loading company list: {e}")
            return []