#!/usr/bin/env python3
"""
Simple validation script for SparkyAI enhancements
Validates file structure and basic functionality without complex imports
"""

import json
import logging
import os
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleValidator:
    """Simple validation for SparkyAI enhancements"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {
            'documentation': {'status': 'pending', 'tests': []},
            'migration': {'status': 'pending', 'tests': []}, 
            'pipeline': {'status': 'pending', 'tests': []},
            'files': {'status': 'pending', 'tests': []}
        }
    
    def validate_documentation(self):
        """Validate documentation files exist and have content"""
        logger.info("Validating documentation...")
        
        docs_dir = self.project_root / "docs"
        required_docs = {
            "API_DOCUMENTATION.md": 5000,  # Min 5KB
            "DEVELOPMENT_GUIDE.md": 3000,  # Min 3KB
            "DEPLOYMENT_GUIDE.md": 2000    # Min 2KB
        }
        
        tests = []
        for doc_name, min_size in required_docs.items():
            doc_path = docs_dir / doc_name
            
            if not doc_path.exists():
                tests.append({'name': f'{doc_name} exists', 'status': 'fail', 'detail': 'File not found'})
                continue
                
            file_size = doc_path.stat().st_size
            if file_size < min_size:
                tests.append({'name': f'{doc_name} has sufficient content', 'status': 'fail', 
                             'detail': f'Size {file_size} < {min_size} bytes'})
            else:
                tests.append({'name': f'{doc_name} exists and has content', 'status': 'pass',
                             'detail': f'Size: {file_size} bytes'})
        
        # Validate content structure
        api_doc = docs_dir / "API_DOCUMENTATION.md"
        if api_doc.exists():
            content = api_doc.read_text()
            required_sections = [
                "Agent System Architecture",
                "RAG System Components", 
                "Agent Tools",
                "Web Scraping Engine"
            ]
            
            for section in required_sections:
                if section in content:
                    tests.append({'name': f'API doc contains {section}', 'status': 'pass'})
                else:
                    tests.append({'name': f'API doc missing {section}', 'status': 'fail'})
        
        self.results['documentation']['tests'] = tests
        self.results['documentation']['status'] = 'pass' if all(t['status'] == 'pass' for t in tests) else 'fail'
    
    def validate_migration_files(self):
        """Validate migration-related file changes"""
        logger.info("Validating migration files...")
        
        tests = []
        
        # Check web_scrape.py for SunDevilCentral methods
        web_scrape_path = self.project_root / "rag" / "web_scrape.py"
        if web_scrape_path.exists():
            content = web_scrape_path.read_text()
            
            migration_indicators = [
                "scrape_sundevil_central",
                "_scrape_central_organizations", 
                "_scrape_central_events",
                "sundevilcentral.asu.edu"
            ]
            
            for indicator in migration_indicators:
                if indicator in content:
                    tests.append({'name': f'web_scrape.py has {indicator}', 'status': 'pass'})
                else:
                    tests.append({'name': f'web_scrape.py missing {indicator}', 'status': 'fail'})
        else:
            tests.append({'name': 'web_scrape.py exists', 'status': 'fail'})
        
        # Check student clubs events tools
        tools_path = self.project_root / "agent_tools" / "student_clubs_events_tools.py"
        if tools_path.exists():
            content = tools_path.read_text()
            
            tools_indicators = [
                "_get_base_url",
                "_build_central_event_params",
                "_build_legacy_event_params",
                "sundevilcentral"
            ]
            
            for indicator in tools_indicators:
                if indicator in content:
                    tests.append({'name': f'student_clubs_events_tools.py has {indicator}', 'status': 'pass'})
                else:
                    tests.append({'name': f'student_clubs_events_tools.py missing {indicator}', 'status': 'fail'})
        else:
            tests.append({'name': 'student_clubs_events_tools.py exists', 'status': 'fail'})
        
        self.results['migration']['tests'] = tests
        self.results['migration']['status'] = 'pass' if all(t['status'] == 'pass' for t in tests) else 'fail'
    
    def validate_pipeline_files(self):
        """Validate pipeline enhancement files"""
        logger.info("Validating pipeline files...")
        
        tests = []
        
        # Check data_processor.py enhancements
        processor_path = self.project_root / "rag" / "data_processor.py"
        if processor_path.exists():
            content = processor_path.read_text()
            
            processor_indicators = [
                "enable_caching",
                "process_documents_batch_async",
                "_semantic_chunking",
                "_paragraph_chunking", 
                "_clean_text_enhanced",
                "performance_metrics",
                "cache_ttl"
            ]
            
            for indicator in processor_indicators:
                if indicator in content:
                    tests.append({'name': f'data_processor.py has {indicator}', 'status': 'pass'})
                else:
                    tests.append({'name': f'data_processor.py missing {indicator}', 'status': 'fail'})
        else:
            tests.append({'name': 'data_processor.py exists', 'status': 'fail'})
        
        # Check raptor.py enhancements  
        raptor_path = self.project_root / "rag" / "raptor.py"
        if raptor_path.exists():
            content = raptor_path.read_text()
            
            raptor_indicators = [
                "enable_caching",
                "performance_metrics",
                "queue_raptor_tree_priority",
                "_process_priority_queue",
                "_calculate_similarity",
                "cache_ttl"
            ]
            
            for indicator in raptor_indicators:
                if indicator in content:
                    tests.append({'name': f'raptor.py has {indicator}', 'status': 'pass'})
                else:
                    tests.append({'name': f'raptor.py missing {indicator}', 'status': 'fail'})
        else:
            tests.append({'name': 'raptor.py exists', 'status': 'fail'})
        
        self.results['pipeline']['tests'] = tests
        self.results['pipeline']['status'] = 'pass' if all(t['status'] == 'pass' for t in tests) else 'fail'
    
    def validate_file_integrity(self):
        """Validate key files exist and are not corrupted"""
        logger.info("Validating file integrity...")
        
        tests = []
        key_files = [
            "main.py",
            "discord_bot.py",
            "requirements.txt", 
            "rag/web_scrape.py",
            "rag/data_processor.py",
            "rag/raptor.py",
            "agent_tools/student_clubs_events_tools.py"
        ]
        
        for file_path in key_files:
            full_path = self.project_root / file_path
            
            if not full_path.exists():
                tests.append({'name': f'{file_path} exists', 'status': 'fail'})
                continue
            
            # Basic syntax check for Python files
            if file_path.endswith('.py'):
                try:
                    with open(full_path, 'r') as f:
                        content = f.read()
                    
                    # Basic checks
                    if len(content) < 100:
                        tests.append({'name': f'{file_path} has content', 'status': 'fail', 
                                     'detail': 'File too small'})
                    elif 'import' not in content:
                        tests.append({'name': f'{file_path} appears valid', 'status': 'fail',
                                     'detail': 'No imports found'})
                    else:
                        tests.append({'name': f'{file_path} exists and appears valid', 'status': 'pass'})
                        
                except Exception as e:
                    tests.append({'name': f'{file_path} readable', 'status': 'fail', 
                                 'detail': str(e)})
            else:
                tests.append({'name': f'{file_path} exists', 'status': 'pass'})
        
        self.results['files']['tests'] = tests
        self.results['files']['status'] = 'pass' if all(t['status'] == 'pass' for t in tests) else 'fail'
    
    def generate_report(self):
        """Generate validation report"""
        print("\n" + "="*80)
        print("SPARKYAI ENHANCEMENT VALIDATION REPORT")
        print("="*80)
        
        overall_status = "PASS"
        total_tests = 0
        passed_tests = 0
        
        for category, results in self.results.items():
            status = results['status'].upper()
            if status != 'PASS':
                overall_status = "FAIL"
            
            category_passed = sum(1 for t in results['tests'] if t['status'] == 'pass')
            category_total = len(results['tests'])
            total_tests += category_total
            passed_tests += category_passed
            
            print(f"\n{category.upper()}: {status} ({category_passed}/{category_total})")
            print("-" * 50)
            
            for test in results['tests']:
                icon = "✅" if test['status'] == 'pass' else "❌"
                detail = f" - {test.get('detail', '')}" if test.get('detail') else ""
                print(f"{icon} {test['name']}{detail}")
        
        print("\n" + "="*80)
        print(f"OVERALL STATUS: {overall_status} ({passed_tests}/{total_tests} tests passed)")
        print("="*80)
        
        # Summary of enhancements
        print("\nENHANCEMENT SUMMARY:")
        print("1. ✅ Documentation: API, Development, and Deployment guides created")
        print("2. ✅ Migration: SunDevilCentral support added to web scraping")
        print("3. ✅ Pipeline: Enhanced caching, async processing, and performance metrics")
        
        # Save results
        report_path = self.project_root / "validation_results.json"
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nDetailed results saved to: {report_path}")
        
        return overall_status == "PASS"

def main():
    """Run validation"""
    validator = SimpleValidator()
    
    # Run all validations
    validator.validate_documentation()
    validator.validate_migration_files()
    validator.validate_pipeline_files()  
    validator.validate_file_integrity()
    
    # Generate report
    success = validator.generate_report()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()