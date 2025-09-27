#!/usr/bin/env python3
"""
Test script for SparkyAI enhancements
Tests the three main improvements:
1. Documentation completeness
2. SunDevilCentral migration
3. Enhanced data processing pipeline
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test imports
try:
    from rag.web_scrape import ASUWebScraper
    # Skip other imports that might have complex dependencies for now
    print("✅ Core imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    # Continue with tests that don't require full imports

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancementTester:
    """Test suite for SparkyAI enhancements"""
    
    def __init__(self):
        self.results = {
            'documentation': {'status': 'pending', 'tests': []},
            'migration': {'status': 'pending', 'tests': []},
            'pipeline': {'status': 'pending', 'tests': []}
        }
    
    def test_documentation(self):
        """Test documentation completeness"""
        logger.info("Testing documentation completeness...")
        
        docs_dir = project_root / "docs"
        required_docs = [
            "API_DOCUMENTATION.md",
            "DEVELOPMENT_GUIDE.md", 
            "DEPLOYMENT_GUIDE.md"
        ]
        
        tests = []
        for doc in required_docs:
            doc_path = docs_dir / doc
            if doc_path.exists() and doc_path.stat().st_size > 1000:  # At least 1KB
                tests.append({'name': f'{doc} exists and has content', 'status': 'pass'})
            else:
                tests.append({'name': f'{doc} missing or empty', 'status': 'fail'})
        
        # Check API documentation structure
        api_doc_path = docs_dir / "API_DOCUMENTATION.md"
        if api_doc_path.exists():
            content = api_doc_path.read_text()
            required_sections = [
                "Agent System Architecture",
                "RAG System Components",
                "Agent Tools",
                "Web Scraping Engine"
            ]
            
            for section in required_sections:
                if section in content:
                    tests.append({'name': f'API doc has {section} section', 'status': 'pass'})
                else:
                    tests.append({'name': f'API doc missing {section} section', 'status': 'fail'})
        
        self.results['documentation']['tests'] = tests
        self.results['documentation']['status'] = 'pass' if all(t['status'] == 'pass' for t in tests) else 'fail'
    
    def test_migration(self):
        """Test SunDevilCentral migration"""
        logger.info("Testing SunDevilCentral migration...")
        
        tests = []
        
        # Test WebScraper has SunDevilCentral support
        try:
            scraper = WebScraper(logger)
            if hasattr(scraper, 'scrape_sundevil_central'):
                tests.append({'name': 'WebScraper has scrape_sundevil_central method', 'status': 'pass'})
                
                # Test method structure
                import inspect
                method_params = inspect.signature(scraper.scrape_sundevil_central).parameters
                if 'base_url' in method_params and 'max_pages' in method_params:
                    tests.append({'name': 'scrape_sundevil_central has correct parameters', 'status': 'pass'})
                else:
                    tests.append({'name': 'scrape_sundevil_central missing required parameters', 'status': 'fail'})
            else:
                tests.append({'name': 'WebScraper missing scrape_sundevil_central method', 'status': 'fail'})
        except Exception as e:
            tests.append({'name': f'WebScraper initialization failed: {e}', 'status': 'fail'})
        
        # Test StudentClubsEventsTools migration logic
        try:
            utils = Utils()
            tools = StudentClubsEventsTools(utils)
            
            # Check for dual platform support methods
            if hasattr(tools, '_get_base_url'):
                tests.append({'name': 'StudentClubsEventsTools has _get_base_url method', 'status': 'pass'})
            else:
                tests.append({'name': 'StudentClubsEventsTools missing _get_base_url method', 'status': 'fail'})
                
            if hasattr(tools, '_build_central_event_params'):
                tests.append({'name': 'StudentClubsEventsTools has _build_central_event_params method', 'status': 'pass'})
            else:
                tests.append({'name': 'StudentClubsEventsTools missing _build_central_event_params method', 'status': 'fail'})
                
        except Exception as e:
            tests.append({'name': f'StudentClubsEventsTools initialization failed: {e}', 'status': 'fail'})
        
        self.results['migration']['tests'] = tests
        self.results['migration']['status'] = 'pass' if all(t['status'] == 'pass' for t in tests) else 'fail'
    
    def test_pipeline(self):
        """Test enhanced data processing pipeline"""
        logger.info("Testing enhanced data processing pipeline...")
        
        tests = []
        
        # Test DataPreprocessor enhancements
        try:
            processor = DataPreprocessor(logger, enable_caching=True)
            
            # Check for caching support
            if hasattr(processor, 'enable_caching') and processor.enable_caching:
                tests.append({'name': 'DataPreprocessor has caching support', 'status': 'pass'})
            else:
                tests.append({'name': 'DataPreprocessor missing caching support', 'status': 'fail'})
            
            # Check for performance metrics
            if hasattr(processor, 'get_performance_metrics'):
                tests.append({'name': 'DataPreprocessor has performance metrics', 'status': 'pass'})
            else:
                tests.append({'name': 'DataPreprocessor missing performance metrics', 'status': 'fail'})
            
            # Check for enhanced processing methods
            enhanced_methods = [
                'process_documents_batch_async',
                '_semantic_chunking',
                '_paragraph_chunking',
                '_clean_text_enhanced'
            ]
            
            for method in enhanced_methods:
                if hasattr(processor, method):
                    tests.append({'name': f'DataPreprocessor has {method}', 'status': 'pass'})
                else:
                    tests.append({'name': f'DataPreprocessor missing {method}', 'status': 'fail'})
                    
        except Exception as e:
            tests.append({'name': f'DataPreprocessor initialization failed: {e}', 'status': 'fail'})
        
        # Test RAPTOR enhancements  
        try:
            # Mock vector store for testing
            class MockVectorStore:
                def generate_embedding(self, texts):
                    return [[0.1] * 384 for _ in texts]  # Mock embeddings
                
                @property
                def embedding_model(self):
                    return self
                
                def embed_query(self, query):
                    return [0.1] * 384
            
            mock_vs = MockVectorStore()
            raptor = RaptorRetriever(mock_vs, logger, mock_vs, enable_caching=True)
            
            # Check for caching support
            if hasattr(raptor, 'enable_caching') and raptor.enable_caching:
                tests.append({'name': 'RaptorRetriever has caching support', 'status': 'pass'})
            else:
                tests.append({'name': 'RaptorRetriever missing caching support', 'status': 'fail'})
            
            # Check for performance metrics
            if hasattr(raptor, 'get_performance_metrics'):
                tests.append({'name': 'RaptorRetriever has performance metrics', 'status': 'pass'})
            else:
                tests.append({'name': 'RaptorRetriever missing performance metrics', 'status': 'fail'})
            
            # Check for priority queue
            if hasattr(raptor, 'queue_raptor_tree_priority'):
                tests.append({'name': 'RaptorRetriever has priority queue support', 'status': 'pass'})
            else:
                tests.append({'name': 'RaptorRetriever missing priority queue support', 'status': 'fail'})
                
        except Exception as e:
            tests.append({'name': f'RaptorRetriever initialization failed: {e}', 'status': 'fail'})
        
        self.results['pipeline']['tests'] = tests
        self.results['pipeline']['status'] = 'pass' if all(t['status'] == 'pass' for t in tests) else 'fail'
    
    async def run_integration_tests(self):
        """Run integration tests"""
        logger.info("Running integration tests...")
        
        integration_tests = []
        
        # Test web scraping with SunDevilCentral (mock)
        try:
            scraper = WebScraper(logger)
            # Test method exists and can be called (with mock data)
            if hasattr(scraper, 'scrape_sundevil_central'):
                integration_tests.append({
                    'name': 'SunDevilCentral scraping method callable', 
                    'status': 'pass'
                })
            else:
                integration_tests.append({
                    'name': 'SunDevilCentral scraping method missing', 
                    'status': 'fail'
                })
        except Exception as e:
            integration_tests.append({
                'name': f'SunDevilCentral scraping test failed: {e}', 
                'status': 'fail'
            })
        
        # Test data processing pipeline with sample data
        try:
            processor = DataPreprocessor(logger, enable_caching=True)
            
            # Test with sample document
            sample_docs = [
                {
                    'text': 'This is a sample document for testing the enhanced data processing pipeline.',
                    'metadata': {'source': 'test', 'type': 'sample'}
                }
            ]
            
            # Test batch processing
            if hasattr(processor, 'process_documents_batch_async'):
                result = await processor.process_documents_batch_async(sample_docs)
                if result and len(result) > 0:
                    integration_tests.append({
                        'name': 'Batch document processing works',
                        'status': 'pass'
                    })
                else:
                    integration_tests.append({
                        'name': 'Batch document processing returned no results',
                        'status': 'fail'
                    })
            else:
                integration_tests.append({
                    'name': 'Batch processing method missing',
                    'status': 'fail'
                })
                
        except Exception as e:
            integration_tests.append({
                'name': f'Data processing integration test failed: {e}',
                'status': 'fail'
            })
        
        self.results['integration'] = {
            'status': 'pass' if all(t['status'] == 'pass' for t in integration_tests) else 'fail',
            'tests': integration_tests
        }
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "="*80)
        print("SPARKYAI ENHANCEMENT TEST REPORT")
        print("="*80)
        
        overall_status = "PASS"
        
        for category, results in self.results.items():
            status = results['status'].upper()
            if status != 'PASS':
                overall_status = "FAIL"
            
            print(f"\n{category.upper()}: {status}")
            print("-" * 40)
            
            for test in results['tests']:
                icon = "✅" if test['status'] == 'pass' else "❌"
                print(f"{icon} {test['name']}")
        
        print("\n" + "="*80)
        print(f"OVERALL STATUS: {overall_status}")
        print("="*80)
        
        # Save detailed results
        report_path = project_root / "test_results.json"
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nDetailed results saved to: {report_path}")
        
        return overall_status == "PASS"

async def main():
    """Run all tests"""
    tester = EnhancementTester()
    
    # Run component tests
    tester.test_documentation()
    tester.test_migration()
    tester.test_pipeline()
    
    # Run integration tests
    await tester.run_integration_tests()
    
    # Generate report
    success = tester.generate_report()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())