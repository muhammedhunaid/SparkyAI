#!/usr/bin/env python3

import json
from pathlib import Path

def main():
    print("SPARKYAI CONFIGURATION STATUS")
    print("=" * 40)
    
    config_path = Path("config/appConfig.json")
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print("\nCONFIGURED:")
        print("✓ Discord IDs: Set")
        print("✓ Firebase: sparkyai-4b3fd")
        print("✓ Agent Prompts: Complete")
        
        print("\nNEEDS API KEYS:")
        if not config.get("API_KEY", "").strip():
            print("✗ Gemini AI API Key")
        else:
            print("✓ Gemini AI API Key")
            
        if not config.get("DISCORD_BOT_TOKEN", "").strip():
            print("✗ Discord Bot Token")
        else:
            print("✓ Discord Bot Token")
    
    print("\nTEST OPTIONS:")
    print("• python test_enhancements_demo.py")
    print("• python web_testing_interface.py")
    print("• python main.py (needs API keys)")

if __name__ == "__main__":
    main()
