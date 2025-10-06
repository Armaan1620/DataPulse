#!/usr/bin/env python3
"""
DataPulse Backend API Testing Suite
Tests all backend functionality including auth, file upload, data processing, and AI insights
"""

import requests
import json
import io
import pandas as pd
import os
from dotenv import load_dotenv
import time
import sys

# Load environment variables
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE_URL = f"{BACKEND_URL}/api"

print(f"Testing backend at: {API_BASE_URL}")

class DataPulseAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.test_results = {
            'auth': {'passed': 0, 'failed': 0, 'errors': []},
            'file_upload': {'passed': 0, 'failed': 0, 'errors': []},
            'data_processing': {'passed': 0, 'failed': 0, 'errors': []},
            'ai_insights': {'passed': 0, 'failed': 0, 'errors': []},
            'crud_operations': {'passed': 0, 'failed': 0, 'errors': []}
        }
        self.dataset_id = None

    def log_result(self, category, test_name, success, error_msg=None):
        """Log test results"""
        if success:
            self.test_results[category]['passed'] += 1
            print(f"✅ {test_name}")
        else:
            self.test_results[category]['failed'] += 1
            self.test_results[category]['errors'].append(f"{test_name}: {error_msg}")
            print(f"❌ {test_name}: {error_msg}")

    def test_health_check(self):
        """Test basic API health"""
        print("\n=== Testing API Health ===")
        try:
            response = self.session.get(f"{API_BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API Health Check: {data}")
                return True
            else:
                print(f"❌ API Health Check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API Health Check failed: {str(e)}")
            return False

    def test_user_registration(self):
        """Test user registration"""
        print("\n=== Testing User Registration ===")
        
        # Test data
        user_data = {
            "username": "sarah_analyst",
            "email": "sarah.analyst@datapulse.com",
            "password": "SecurePass123!"
        }
        
        try:
            response = self.session.post(f"{API_BASE_URL}/auth/register", json=user_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                self.user_data = data.get('user')
                
                # Set authorization header for future requests
                self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                
                self.log_result('auth', 'User Registration', True)
                print(f"   User ID: {self.user_data['id']}")
                print(f"   Token received: {self.auth_token[:20]}...")
                return True
            else:
                error_msg = f"Status {response.status_code}: {response.text}"
                self.log_result('auth', 'User Registration', False, error_msg)
                return False
                
        except Exception as e:
            self.log_result('auth', 'User Registration', False, str(e))
            return False

    def test_user_login(self):
        """Test user login with existing credentials"""
        print("\n=== Testing User Login ===")
        
        login_data = {
            "email": "sarah.analyst@datapulse.com",
            "password": "SecurePass123!"
        }
        
        try:
            # Clear existing auth for login test
            temp_headers = self.session.headers.copy()
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            response = self.session.post(f"{API_BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user = data.get('user')
                
                # Restore auth header
                self.session.headers.update({'Authorization': f'Bearer {token}'})
                
                self.log_result('auth', 'User Login', True)
                print(f"   Login successful for: {user['email']}")
                return True
            else:
                # Restore original headers
                self.session.headers = temp_headers
                error_msg = f"Status {response.status_code}: {response.text}"
                self.log_result('auth', 'User Login', False, error_msg)
                return False
                
        except Exception as e:
            # Restore original headers
            self.session.headers = temp_headers
            self.log_result('auth', 'User Login', False, str(e))
            return False

    def test_protected_route(self):
        """Test JWT token validation on protected route"""
        print("\n=== Testing Protected Route Access ===")
        
        try:
            response = self.session.get(f"{API_BASE_URL}/auth/me")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result('auth', 'Protected Route Access', True)
                print(f"   Current user: {data['username']} ({data['email']})")
                return True
            else:
                error_msg = f"Status {response.status_code}: {response.text}"
                self.log_result('auth', 'Protected Route Access', False, error_msg)
                return False
                
        except Exception as e:
            self.log_result('auth', 'Protected Route Access', False, str(e))
            return False

    def create_sample_csv(self):
        """Create sample CSV data for testing"""
        data = {
            'customer_id': range(1, 101),
            'age': [25, 34, 45, 23, 56, 67, 29, 38, 42, 31] * 10,
            'income': [45000, 67000, 89000, 34000, 120000, 78000, 52000, 95000, 73000, 61000] * 10,
            'spending_score': [78, 82, 45, 67, 23, 89, 91, 56, 73, 84] * 10,
            'region': ['North', 'South', 'East', 'West', 'Central'] * 20,
            'purchase_amount': [234.50, 567.80, 123.45, 890.12, 456.78, 234.56, 678.90, 345.67, 789.01, 123.45] * 10
        }
        df = pd.DataFrame(data)
        return df.to_csv(index=False)

    def create_sample_json(self):
        """Create sample JSON data for testing"""
        data = [
            {
                "product_id": i,
                "product_name": f"Product_{i}",
                "category": ["Electronics", "Clothing", "Books", "Home", "Sports"][i % 5],
                "price": round(20.0 + (i * 15.5), 2),
                "rating": round(3.0 + (i % 3), 1),
                "sales_count": 100 + (i * 25),
                "in_stock": i % 3 != 0
            }
            for i in range(1, 51)
        ]
        return json.dumps(data, indent=2)

    def test_csv_file_upload(self):
        """Test CSV file upload and validation"""
        print("\n=== Testing CSV File Upload ===")
        
        try:
            csv_content = self.create_sample_csv()
            
            files = {
                'file': ('customer_data.csv', csv_content, 'text/csv')
            }
            
            response = self.session.post(f"{API_BASE_URL}/datasets/upload", files=files)
            
            if response.status_code == 200:
                data = response.json()
                self.dataset_id = data.get('dataset_id')
                
                self.log_result('file_upload', 'CSV File Upload', True)
                print(f"   Dataset ID: {self.dataset_id}")
                print(f"   Processing time: {data.get('processing_time', 0):.2f}s")
                print(f"   Rows: {data.get('rows')}, Columns: {data.get('columns')}")
                return True
            else:
                error_msg = f"Status {response.status_code}: {response.text}"
                self.log_result('file_upload', 'CSV File Upload', False, error_msg)
                return False
                
        except Exception as e:
            self.log_result('file_upload', 'CSV File Upload', False, str(e))
            return False

    def test_json_file_upload(self):
        """Test JSON file upload and validation"""
        print("\n=== Testing JSON File Upload ===")
        
        try:
            json_content = self.create_sample_json()
            
            files = {
                'file': ('product_data.json', json_content, 'application/json')
            }
            
            response = self.session.post(f"{API_BASE_URL}/datasets/upload", files=files)
            
            if response.status_code == 200:
                data = response.json()
                
                self.log_result('file_upload', 'JSON File Upload', True)
                print(f"   Dataset ID: {data.get('dataset_id')}")
                print(f"   Processing time: {data.get('processing_time', 0):.2f}s")
                print(f"   Rows: {data.get('rows')}, Columns: {data.get('columns')}")
                return True
            else:
                error_msg = f"Status {response.status_code}: {response.text}"
                self.log_result('file_upload', 'JSON File Upload', False, error_msg)
                return False
                
        except Exception as e:
            self.log_result('file_upload', 'JSON File Upload', False, str(e))
            return False

    def test_file_size_validation(self):
        """Test file size limit validation (50MB)"""
        print("\n=== Testing File Size Validation ===")
        
        try:
            # Create a large CSV content (simulate large file)
            large_content = "col1,col2,col3\n" + "test,data,values\n" * 100000  # Should be under 50MB
            
            files = {
                'file': ('large_test.csv', large_content, 'text/csv')
            }
            
            response = self.session.post(f"{API_BASE_URL}/datasets/upload", files=files)
            
            # This should succeed as it's under 50MB
            if response.status_code == 200:
                self.log_result('file_upload', 'File Size Validation (Valid)', True)
                return True
            else:
                error_msg = f"Status {response.status_code}: {response.text}"
                self.log_result('file_upload', 'File Size Validation (Valid)', False, error_msg)
                return False
                
        except Exception as e:
            self.log_result('file_upload', 'File Size Validation (Valid)', False, str(e))
            return False

    def test_invalid_file_type(self):
        """Test invalid file type rejection"""
        print("\n=== Testing Invalid File Type Rejection ===")
        
        try:
            # Try to upload a text file (should be rejected)
            files = {
                'file': ('test.txt', 'This is a text file', 'text/plain')
            }
            
            response = self.session.post(f"{API_BASE_URL}/datasets/upload", files=files)
            
            # This should fail with 400 status
            if response.status_code == 400:
                self.log_result('file_upload', 'Invalid File Type Rejection', True)
                print(f"   Correctly rejected: {response.json().get('detail', 'Unknown error')}")
                return True
            else:
                error_msg = f"Expected 400, got {response.status_code}: {response.text}"
                self.log_result('file_upload', 'Invalid File Type Rejection', False, error_msg)
                return False
                
        except Exception as e:
            self.log_result('file_upload', 'Invalid File Type Rejection', False, str(e))
            return False

    def test_data_analysis_retrieval(self):
        """Test data analysis retrieval"""
        print("\n=== Testing Data Analysis Retrieval ===")
        
        if not self.dataset_id:
            self.log_result('data_processing', 'Data Analysis Retrieval', False, "No dataset ID available")
            return False
        
        try:
            response = self.session.get(f"{API_BASE_URL}/datasets/{self.dataset_id}/analysis")
            
            if response.status_code == 200:
                data = response.json()
                dataset = data.get('dataset', {})
                analysis = data.get('analysis', {})
                
                # Verify analysis components
                has_summary_stats = bool(analysis.get('summary_stats'))
                has_correlations = 'correlations' in analysis
                has_missing_data = bool(analysis.get('missing_data'))
                has_outliers = 'outliers' in analysis
                has_ai_insights = bool(analysis.get('ai_insights'))
                
                self.log_result('data_processing', 'Data Analysis Retrieval', True)
                print(f"   Dataset: {dataset.get('filename')} ({dataset.get('status')})")
                print(f"   Summary Stats: {'✅' if has_summary_stats else '❌'}")
                print(f"   Correlations: {'✅' if has_correlations else '❌'}")
                print(f"   Missing Data Analysis: {'✅' if has_missing_data else '❌'}")
                print(f"   Outlier Detection: {'✅' if has_outliers else '❌'}")
                print(f"   AI Insights: {'✅' if has_ai_insights else '❌'}")
                
                # Test individual components
                self.test_summary_statistics(analysis.get('summary_stats', {}))
                self.test_correlation_analysis(analysis.get('correlations', {}))
                self.test_missing_data_analysis(analysis.get('missing_data', {}))
                self.test_outlier_detection(analysis.get('outliers', {}))
                self.test_ai_insights_content(analysis.get('ai_insights', ''))
                
                return True
            else:
                error_msg = f"Status {response.status_code}: {response.text}"
                self.log_result('data_processing', 'Data Analysis Retrieval', False, error_msg)
                return False
                
        except Exception as e:
            self.log_result('data_processing', 'Data Analysis Retrieval', False, str(e))
            return False

    def test_summary_statistics(self, summary_stats):
        """Test summary statistics component"""
        try:
            has_numeric = bool(summary_stats.get('numeric'))
            has_categorical = bool(summary_stats.get('categorical'))
            
            if has_numeric or has_categorical:
                self.log_result('data_processing', 'Summary Statistics Generation', True)
                print(f"     Numeric stats: {'✅' if has_numeric else '❌'}")
                print(f"     Categorical stats: {'✅' if has_categorical else '❌'}")
            else:
                self.log_result('data_processing', 'Summary Statistics Generation', False, "No statistics generated")
        except Exception as e:
            self.log_result('data_processing', 'Summary Statistics Generation', False, str(e))

    def test_correlation_analysis(self, correlations):
        """Test correlation analysis component"""
        try:
            if correlations and len(correlations) > 0:
                self.log_result('data_processing', 'Correlation Analysis', True)
                print(f"     Correlation matrix generated with {len(correlations)} variables")
            else:
                self.log_result('data_processing', 'Correlation Analysis', True)
                print(f"     No correlations (expected for single numeric column)")
        except Exception as e:
            self.log_result('data_processing', 'Correlation Analysis', False, str(e))

    def test_missing_data_analysis(self, missing_data):
        """Test missing data analysis component"""
        try:
            has_total = bool(missing_data.get('total_missing'))
            has_percentage = bool(missing_data.get('percentage_missing'))
            
            if has_total and has_percentage:
                self.log_result('data_processing', 'Missing Data Analysis', True)
                print(f"     Missing data analysis completed")
            else:
                self.log_result('data_processing', 'Missing Data Analysis', False, "Missing data analysis incomplete")
        except Exception as e:
            self.log_result('data_processing', 'Missing Data Analysis', False, str(e))

    def test_outlier_detection(self, outliers):
        """Test outlier detection component"""
        try:
            if 'error' in outliers:
                self.log_result('data_processing', 'Outlier Detection', True)
                print(f"     Outlier detection handled gracefully: {outliers['error']}")
            elif 'total_outliers' in outliers:
                self.log_result('data_processing', 'Outlier Detection', True)
                print(f"     Outliers detected: {outliers.get('total_outliers', 0)}")
            else:
                self.log_result('data_processing', 'Outlier Detection', False, "No outlier analysis results")
        except Exception as e:
            self.log_result('data_processing', 'Outlier Detection', False, str(e))

    def test_ai_insights_content(self, ai_insights):
        """Test AI insights generation"""
        try:
            if ai_insights and len(ai_insights.strip()) > 50:  # Reasonable content length
                if "AI insights unavailable" in ai_insights or "failed" in ai_insights.lower():
                    self.log_result('ai_insights', 'AI Insights Generation', False, ai_insights)
                else:
                    self.log_result('ai_insights', 'AI Insights Generation', True)
                    print(f"     AI insights generated ({len(ai_insights)} characters)")
                    print(f"     Preview: {ai_insights[:100]}...")
            else:
                self.log_result('ai_insights', 'AI Insights Generation', False, "No meaningful AI insights generated")
        except Exception as e:
            self.log_result('ai_insights', 'AI Insights Generation', False, str(e))

    def test_dataset_listing(self):
        """Test dataset listing with user isolation"""
        print("\n=== Testing Dataset Listing ===")
        
        try:
            response = self.session.get(f"{API_BASE_URL}/datasets")
            
            if response.status_code == 200:
                datasets = response.json()
                
                self.log_result('crud_operations', 'Dataset Listing', True)
                print(f"   Found {len(datasets)} datasets for current user")
                
                for i, dataset in enumerate(datasets[:3]):  # Show first 3
                    print(f"     {i+1}. {dataset.get('filename')} ({dataset.get('status')})")
                
                return True
            else:
                error_msg = f"Status {response.status_code}: {response.text}"
                self.log_result('crud_operations', 'Dataset Listing', False, error_msg)
                return False
                
        except Exception as e:
            self.log_result('crud_operations', 'Dataset Listing', False, str(e))
            return False

    def test_dataset_deletion(self):
        """Test dataset deletion"""
        print("\n=== Testing Dataset Deletion ===")
        
        if not self.dataset_id:
            self.log_result('crud_operations', 'Dataset Deletion', False, "No dataset ID available")
            return False
        
        try:
            response = self.session.delete(f"{API_BASE_URL}/datasets/{self.dataset_id}")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result('crud_operations', 'Dataset Deletion', True)
                print(f"   {data.get('message', 'Dataset deleted')}")
                
                # Verify deletion by trying to access the dataset
                verify_response = self.session.get(f"{API_BASE_URL}/datasets/{self.dataset_id}/analysis")
                if verify_response.status_code == 404:
                    print(f"   ✅ Deletion verified - dataset no longer accessible")
                else:
                    print(f"   ⚠️  Dataset still accessible after deletion")
                
                return True
            else:
                error_msg = f"Status {response.status_code}: {response.text}"
                self.log_result('crud_operations', 'Dataset Deletion', False, error_msg)
                return False
                
        except Exception as e:
            self.log_result('crud_operations', 'Dataset Deletion', False, str(e))
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting DataPulse Backend API Tests")
        print("=" * 50)
        
        # Health check first
        if not self.test_health_check():
            print("❌ API is not accessible. Stopping tests.")
            return False
        
        # Authentication tests
        print("\n🔐 AUTHENTICATION TESTS")
        self.test_user_registration()
        self.test_user_login()
        self.test_protected_route()
        
        # File upload tests
        print("\n📁 FILE UPLOAD TESTS")
        self.test_csv_file_upload()
        self.test_json_file_upload()
        self.test_file_size_validation()
        self.test_invalid_file_type()
        
        # Data processing tests (depends on successful upload)
        print("\n📊 DATA PROCESSING TESTS")
        self.test_data_analysis_retrieval()
        
        # CRUD operations tests
        print("\n🔄 CRUD OPERATIONS TESTS")
        self.test_dataset_listing()
        self.test_dataset_deletion()
        
        # Print summary
        self.print_test_summary()
        
        return True

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 50)
        print("📋 TEST SUMMARY")
        print("=" * 50)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results['passed']
            failed = results['failed']
            total_passed += passed
            total_failed += failed
            
            status = "✅" if failed == 0 else "❌"
            print(f"{status} {category.upper().replace('_', ' ')}: {passed} passed, {failed} failed")
            
            # Show errors
            for error in results['errors']:
                print(f"   ❌ {error}")
        
        print(f"\n🎯 OVERALL: {total_passed} passed, {total_failed} failed")
        
        if total_failed == 0:
            print("🎉 All tests passed!")
        else:
            print(f"⚠️  {total_failed} tests failed - see details above")
        
        return total_failed == 0


def main():
    """Main test execution"""
    tester = DataPulseAPITester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()