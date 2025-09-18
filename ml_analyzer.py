import numpy as np
from typing import Dict, List, Tuple
import re

class FinancialAnalyzer:
    def __init__(self):
        self.threshold = 10.0  # 10% threshold for pros/cons classification
        
        self.pros_templates = [
            "Company is almost debt-free",
            "Company has reduced debt",
            "Company has a good return on equity (ROE) track record: 3 Years ROE {value}%",
            "Company has been maintaining a healthy dividend payout of {value}%",
            "Company has delivered good profit growth of {value}%",
            "Company's median sales growth is {value}% of last 10 years",
            "Company has strong operating margins of {value}%",
            "Company maintains healthy current ratio of {value}",
            "Company has excellent asset turnover of {value}%"
        ]
        
        self.cons_templates = [
            "The company has delivered a poor sales growth of {value}% over past five years",
            "Company is not paying out dividend",
            "Company has a low return on equity of {value}% over last 3 years",
            "Company has high debt-to-equity ratio of {value}%",
            "Company's profit margins have declined to {value}%",
            "Company has poor working capital management",
            "Company's asset quality has deteriorated",
            "Company has inconsistent earnings growth of {value}%"
        ]
    
    def extract_financial_metrics(self, financial_data: Dict) -> Dict:
        """Extract key financial metrics from the data"""
        metrics = {}
        
        # Extract from different sections
        ratios = financial_data.get('ratios', {})
        growth = financial_data.get('growth_metrics', {})
        balance_sheet = financial_data.get('balance_sheet', {})
        profit_loss = financial_data.get('profit_loss', {})
        
        # ROE calculation
        if 'roe' in ratios:
            metrics['roe'] = self._safe_float(ratios['roe'])
        
        # Sales/Revenue growth
        if 'sales_growth' in growth:
            metrics['sales_growth'] = self._safe_float(growth['sales_growth'])
        
        # Profit growth
        if 'profit_growth' in growth:
            metrics['profit_growth'] = self._safe_float(growth['profit_growth'])
        
        # Dividend payout
        if 'dividend_payout' in ratios:
            metrics['dividend_payout'] = self._safe_float(ratios['dividend_payout'])
        
        # Debt ratios
        if 'debt_to_equity' in ratios:
            metrics['debt_to_equity'] = self._safe_float(ratios['debt_to_equity'])
        
        # Operating margins
        if 'operating_margin' in ratios:
            metrics['operating_margin'] = self._safe_float(ratios['operating_margin'])
        
        return metrics
    
    def _safe_float(self, value) -> float:
        """Safely convert value to float"""
        try:
            if isinstance(value, str):
                # Remove % sign and convert
                value = value.replace('%', '').strip()
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def analyze_financial_health(self, financial_data: Dict) -> Dict:
        """Generate pros and cons based on financial metrics"""
        metrics = self.extract_financial_metrics(financial_data)
        
        pros = []
        cons = []
        
        # Analyze each metric
        for metric_name, value in metrics.items():
            if metric_name == 'roe' and value > self.threshold:
                pros.append(f"Company has a good return on equity (ROE) track record: 3 Years ROE {value:.1f}%")
            elif metric_name == 'roe' and value < self.threshold:
                cons.append(f"Company has a low return on equity of {value:.1f}% over last 3 years")
            
            elif metric_name == 'sales_growth' and value > self.threshold:
                pros.append(f"Company's median sales growth is {value:.1f}% of last 10 years")
            elif metric_name == 'sales_growth' and value < self.threshold:
                cons.append(f"The company has delivered a poor sales growth of {value:.1f}% over past five years")
            
            elif metric_name == 'profit_growth' and value > self.threshold:
                pros.append(f"Company has delivered good profit growth of {value:.1f}%")
            
            elif metric_name == 'dividend_payout' and value > self.threshold:
                pros.append(f"Company has been maintaining a healthy dividend payout of {value:.1f}%")
            elif metric_name == 'dividend_payout' and value == 0:
                cons.append("Company is not paying out dividend")
            
            elif metric_name == 'debt_to_equity' and value < 0.3:
                pros.append("Company is almost debt-free")
            elif metric_name == 'debt_to_equity' and value > 1.0:
                cons.append(f"Company has high debt-to-equity ratio of {value:.1f}%")
        
        # Select top 3 pros and cons
        selected_pros = pros[:3] if len(pros) >= 3 else pros
        selected_cons = cons[:3] if len(cons) >= 3 else cons
        
        return {
            'pros': selected_pros,
            'cons': selected_cons,
            'metrics': metrics
        }
    
    def generate_insights(self, company_data: Dict) -> str:
        """Generate overall financial insights"""
        company_name = company_data.get('company_name', 'Company')
        analysis = self.analyze_financial_health(company_data)
        
        pros_count = len(analysis['pros'])
        cons_count = len(analysis['cons'])
        
        if pros_count > cons_count:
            return f"{company_name} shows strong financial performance with {pros_count} positive indicators"
        elif cons_count > pros_count:
            return f"{company_name} faces financial challenges with {cons_count} areas of concern"
        else:
            return f"{company_name} shows mixed financial performance requiring careful monitoring"