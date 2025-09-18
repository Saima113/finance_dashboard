# database_manager.py - FIXED VERSION
import mysql.connector
from mysql.connector import Error
import json
from typing import Dict, List, Optional

class DatabaseManager:
    def __init__(self, host: str, database: str, user: str, password: str):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if self.connection.is_connected():
                print("Successfully connected to MySQL database")
                self.create_tables()
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
    
    def create_tables(self):
        """Create necessary tables if they don't exist - FIXED VERSION"""
        cursor = self.connection.cursor()
        
        try:
            # First, drop existing tables if they exist (to fix foreign key issues)
            drop_tables = [
                "DROP TABLE IF EXISTS pros",
                "DROP TABLE IF EXISTS cons", 
                "DROP TABLE IF EXISTS analysis",
                "DROP TABLE IF EXISTS companies"
            ]
            
            for drop_query in drop_tables:
                cursor.execute(drop_query)
            
            # Companies table - FIXED with 'symbol' column
            companies_table = """
            CREATE TABLE companies (
                id INT AUTO_INCREMENT PRIMARY KEY,
                symbol VARCHAR(20) UNIQUE NOT NULL,
                company_name VARCHAR(255),
                sector VARCHAR(100),
                market_cap BIGINT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_symbol (symbol)
            )
            """
            
            # Analysis table - FIXED foreign key reference
            analysis_table = """
            CREATE TABLE analysis (
                id INT AUTO_INCREMENT PRIMARY KEY,
                company_symbol VARCHAR(20),
                insights TEXT,
                overall_score DECIMAL(5,2),
                analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_symbol) REFERENCES companies(symbol) ON DELETE CASCADE,
                INDEX idx_company_symbol (company_symbol)
            )
            """
            
            # Pros table - FIXED foreign key reference
            pros_table = """
            CREATE TABLE pros (
                id INT AUTO_INCREMENT PRIMARY KEY,
                company_symbol VARCHAR(20),
                pro_text TEXT,
                metric_name VARCHAR(100),
                metric_value DECIMAL(10,2),
                weight DECIMAL(3,2) DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_symbol) REFERENCES companies(symbol) ON DELETE CASCADE,
                INDEX idx_company_symbol (company_symbol)
            )
            """
            
            # Cons table - FIXED foreign key reference
            cons_table = """
            CREATE TABLE cons (
                id INT AUTO_INCREMENT PRIMARY KEY,
                company_symbol VARCHAR(20),
                con_text TEXT,
                metric_name VARCHAR(100),
                metric_value DECIMAL(10,2),
                weight DECIMAL(3,2) DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_symbol) REFERENCES companies(symbol) ON DELETE CASCADE,
                INDEX idx_company_symbol (company_symbol)
            )
            """
            
            # Execute table creation in correct order
            cursor.execute(companies_table)
            cursor.execute(analysis_table)
            cursor.execute(pros_table)
            cursor.execute(cons_table)
            
            self.connection.commit()
            print(" Tables created successfully")
            
        except Error as e:
            print(f"Error creating tables: {e}")
        finally:
            cursor.close()
    
    def store_company(self, symbol: str, company_name: str):
        """Store company information"""
        cursor = self.connection.cursor()
        query = """
        INSERT INTO companies (symbol, company_name) 
        VALUES (%s, %s) 
        ON DUPLICATE KEY UPDATE 
        company_name = VALUES(company_name),
        updated_at = CURRENT_TIMESTAMP
        """
        try:
            cursor.execute(query, (symbol, company_name))
            self.connection.commit()
            print(f"✅ Company stored: {symbol} - {company_name}")
        except Error as e:
            print(f"Error storing company {symbol}: {e}")
        finally:
            cursor.close()
    
    def store_analysis_results(self, company_symbol: str, pros: List[str], 
                             cons: List[str], insights: str, metrics: Dict):
        """Store complete analysis results"""
        cursor = self.connection.cursor()
        
        try:
            # Clear existing analysis for this company
            self.clear_company_analysis(company_symbol)
            
            # Calculate overall score
            overall_score = len(pros) * 10 - len(cons) * 5
            
            # Store insights
            insights_query = """
            INSERT INTO analysis (company_symbol, insights, overall_score) 
            VALUES (%s, %s, %s)
            """
            cursor.execute(insights_query, (company_symbol, insights, overall_score))
            
            # Store pros
            for i, pro in enumerate(pros):
                metric_value = self._extract_value_from_text(pro)
                metric_name = self._extract_metric_name(pro)
                pros_query = """
                INSERT INTO pros (company_symbol, pro_text, metric_name, metric_value) 
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(pros_query, (company_symbol, pro, metric_name, metric_value))
            
            # Store cons
            for i, con in enumerate(cons):
                metric_value = self._extract_value_from_text(con)
                metric_name = self._extract_metric_name(con)
                cons_query = """
                INSERT INTO cons (company_symbol, con_text, metric_name, metric_value) 
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(cons_query, (company_symbol, con, metric_name, metric_value))
            
            self.connection.commit()
            print(f"✅ Analysis stored for {company_symbol}")
            
        except Error as e:
            print(f"Error storing analysis for {company_symbol}: {e}")
            self.connection.rollback()
        finally:
            cursor.close()
    
    def _extract_value_from_text(self, text: str) -> Optional[float]:
        """Extract numeric value from analysis text"""
        import re
        pattern = r'(\d+\.?\d*)%?'
        match = re.search(pattern, text)
        return float(match.group(1)) if match else None
    
    def _extract_metric_name(self, text: str) -> str:
        """Extract metric name from analysis text"""
        text_lower = text.lower()
        if 'roe' in text_lower:
            return 'ROE'
        elif 'sales growth' in text_lower:
            return 'Sales Growth'
        elif 'profit growth' in text_lower:
            return 'Profit Growth'
        elif 'dividend' in text_lower:
            return 'Dividend'
        elif 'debt' in text_lower:
            return 'Debt Ratio'
        else:
            return 'General'
    
    def clear_company_analysis(self, company_symbol: str):
        """Clear existing analysis for a company"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("DELETE FROM pros WHERE company_symbol = %s", (company_symbol,))
            cursor.execute("DELETE FROM cons WHERE company_symbol = %s", (company_symbol,))
            cursor.execute("DELETE FROM analysis WHERE company_symbol = %s", (company_symbol,))
            print(f"🗑️  Cleared existing analysis for {company_symbol}")
        except Error as e:
            print(f"Error clearing analysis for {company_symbol}: {e}")
        finally:
            cursor.close()
    
    def get_company_analysis(self, company_symbol: str) -> Dict:
        """Retrieve complete analysis for a company"""
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            # Get company info
            cursor.execute("SELECT * FROM companies WHERE symbol = %s", (company_symbol,))
            company = cursor.fetchone()
            
            # Get insights
            cursor.execute("""
                SELECT insights, overall_score, analysis_date 
                FROM analysis 
                WHERE company_symbol = %s 
                ORDER BY analysis_date DESC 
                LIMIT 1
            """, (company_symbol,))
            insights_result = cursor.fetchone()
            
            # Get pros
            cursor.execute("""
                SELECT pro_text, metric_name, metric_value 
                FROM pros 
                WHERE company_symbol = %s 
                ORDER BY created_at DESC
            """, (company_symbol,))
            pros = cursor.fetchall()
            
            # Get cons
            cursor.execute("""
                SELECT con_text, metric_name, metric_value 
                FROM cons 
                WHERE company_symbol = %s 
                ORDER BY created_at DESC
            """, (company_symbol,))
            cons = cursor.fetchall()
            
            return {
                'company': company,
                'insights': insights_result['insights'] if insights_result else "",
                'overall_score': insights_result['overall_score'] if insights_result else 0,
                'analysis_date': insights_result['analysis_date'] if insights_result else None,
                'pros': [p['pro_text'] for p in pros],
                'cons': [c['con_text'] for c in cons],
                'pros_details': pros,
                'cons_details': cons
            }
            
        except Error as e:
            print(f"Error retrieving analysis for {company_symbol}: {e}")
            return {}
        finally:
            cursor.close()
    
    def get_all_companies(self) -> List[Dict]:
        """Get all companies with their analysis status"""
        cursor = self.connection.cursor(dictionary=True)
        try:
            query = """
            SELECT 
                c.symbol, 
                c.company_name, 
                c.sector,
                a.analysis_date,
                a.overall_score,
                COUNT(p.id) as pros_count,
                COUNT(con.id) as cons_count
            FROM companies c
            LEFT JOIN analysis a ON c.symbol = a.company_symbol 
                AND a.analysis_date = (
                    SELECT MAX(analysis_date) 
                    FROM analysis a2 
                    WHERE a2.company_symbol = c.symbol
                )
            LEFT JOIN pros p ON c.symbol = p.company_symbol
            LEFT JOIN cons con ON c.symbol = con.company_symbol
            GROUP BY c.symbol, c.company_name, c.sector, a.analysis_date, a.overall_score
            ORDER BY a.analysis_date DESC, c.symbol
            """
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error retrieving companies: {e}")
            return []
        finally:
            cursor.close()
    
    def get_analysis_summary(self) -> Dict:
        """Get overall analysis summary statistics"""
        cursor = self.connection.cursor(dictionary=True)
        try:
            # Total companies
            cursor.execute("SELECT COUNT(*) as total FROM companies")
            total = cursor.fetchone()['total']
            
            # Analyzed companies
            cursor.execute("SELECT COUNT(DISTINCT company_symbol) as analyzed FROM analysis")
            analyzed = cursor.fetchone()['analyzed']
            
            # Average scores
            cursor.execute("SELECT AVG(overall_score) as avg_score FROM analysis")
            avg_score_result = cursor.fetchone()
            avg_score = avg_score_result['avg_score'] if avg_score_result['avg_score'] else 0
            
            return {
                'total_companies': total,
                'analyzed_companies': analyzed,
                'pending_companies': total - analyzed,
                'average_score': float(avg_score),
                'completion_rate': (analyzed / total * 100) if total > 0 else 0
            }
        except Error as e:
            print(f"Error getting summary: {e}")
            return {}
        finally:
            cursor.close()
    
    def close_connection(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")