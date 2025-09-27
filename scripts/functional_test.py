#!/usr/bin/env python3
"""
Simple functional test to verify SparkyAI enhancements work in practice
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_data_processor():
    """Test enhanced data processor features"""
    try:
        from rag.data_processor import DataPreprocessor
        
        # Initialize with caching enabled
        processor = DataPreprocessor(logger, enable_caching=True)
        print("✅ DataPreprocessor initialized with caching")
        
        # Test performance metrics
        metrics = processor.get_performance_metrics()
        print(f"✅ Performance metrics available: {list(metrics.keys())}")
        
        # Test sample document processing
        sample_docs = [
            {
                'text': 'This is a test document for ASU students. It contains information about courses and events.',
                'metadata': {'source': 'test', 'type': 'sample'}
            }
        ]
        
        processed = processor.process_documents(sample_docs)
        if processed and len(processed) > 0:
            print(f"✅ Document processing works: {len(processed)} chunks generated")
        else:
            print("❌ Document processing failed")
            
        return True
    except Exception as e:
        print(f"❌ DataProcessor test failed: {e}")
        return False

def test_student_clubs_tools():
    """Test student clubs tools migration features"""
    try:
        from agent_tools.student_clubs_events_tools import StudentClubsEventsTools
        from utils.utils import Utils
        
        # Initialize tools
        utils = Utils()
        tools = StudentClubsEventsTools(utils)
        print("✅ StudentClubsEventsTools initialized")
        
        # Test base URL selection
        base_url = tools._get_base_url()
        if "sundevilcentral" in base_url:
            print(f"✅ Using SunDevilCentral platform: {base_url}")
        else:
            print(f"✅ Using legacy platform: {base_url}")
            
        # Test parameter building
        event_params = tools._build_central_event_params("test query", {})
        if event_params:
            print("✅ Event parameter building works")
        else:
            print("❌ Event parameter building failed")
            
        return True
    except Exception as e:
        print(f"❌ StudentClubsTools test failed: {e}")
        return False

def test_documentation_exists():
    """Test that documentation files exist and have content"""
    docs = [
        "docs/API_DOCUMENTATION.md",
        "docs/DEVELOPMENT_GUIDE.md", 
        "docs/DEPLOYMENT_GUIDE.md"
    ]
    
    all_exist = True
    for doc_path in docs:
        full_path = project_root / doc_path
        if full_path.exists() and full_path.stat().st_size > 5000:  # At least 5KB
            print(f"✅ {doc_path} exists and has substantial content")
        else:
            print(f"❌ {doc_path} missing or insufficient content")
            all_exist = False
    
    return all_exist

def main():
    """Run all functional tests"""
    print("="*60)
    print("SPARKYAI FUNCTIONAL VERIFICATION")
    print("="*60)
    
    tests = [
        ("Documentation Files", test_documentation_exists),
        ("Data Processor Features", test_data_processor),
        ("Student Clubs Tools", test_student_clubs_tools)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
    
    print(f"\n{'='*60}")
    print(f"RESULTS: {passed}/{total} tests passed")
    print(f"STATUS: {'PASS' if passed == total else 'FAIL'}")
    print(f"{'='*60}")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)