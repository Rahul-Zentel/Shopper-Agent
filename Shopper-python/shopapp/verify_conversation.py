import sys
import os
import asyncio
from dotenv import load_dotenv

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shopapp.utils.region import get_region_from_ip
from shopapp.agent import analyze_prompt
from shopapp.models import ConversationMessage

load_dotenv()

def test_region_detection():
    print("\n--- Testing Region Detection ---")
    # Test with known IPs (using public DNS servers as proxies for location)
    # 8.8.8.8 is US (Google)
    # But get_region_from_ip uses an external API, so we can pass any IP.
    
    us_ip = "8.8.8.8"
    region_us = get_region_from_ip(us_ip)
    print(f"IP {us_ip} -> Region: {region_us}")
    
    # India IP (random one)
    in_ip = "103.25.231.0" 
    region_in = get_region_from_ip(in_ip)
    print(f"IP {in_ip} -> Region: {region_in}")

def test_conversation_flow():
    print("\n--- Testing Conversation Flow ---")
    
    # 1. Low Context
    print("\nTest 1: Low Context Query ('I need earbuds')")
    decision_low = analyze_prompt("I need earbuds", [], region="India")
    print(f"Action: {decision_low.action}")
    if decision_low.action == "ask":
        print(f"Questions: {decision_low.clarifying_questions}")
        print(f"Reply: {decision_low.reply_message}")
    else:
        print("FAILED: Should have asked questions.")

    # 2. High Context
    print("\nTest 2: High Context Query ('I need Sony XM5 earbuds under 25000')")
    decision_high = analyze_prompt("I need Sony XM5 earbuds under 25000", [], region="India")
    print(f"Action: {decision_high.action}")
    if decision_high.action == "search":
        print(f"Search Params: {decision_high.search_params}")
    else:
        print("FAILED: Should have searched.")

if __name__ == "__main__":
    test_region_detection()
    test_conversation_flow()
