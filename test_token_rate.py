#!/usr/bin/env python3
import json
from datetime import datetime

def analyze_transcript(filepath):
    """Analyze token rates using current wrong method and proposed correct method."""
    
    entries = []
    with open(filepath, 'r') as f:
        for line in f:
            entries.append(json.loads(line.strip()))
    
    print("=== Current (Wrong) Method ===")
    print("Calculates: output_tokens / (assistant_timestamp - user_timestamp)")
    print("Problem: Includes thinking time!\n")
    
    user_timestamps = []
    assistant_timestamps = []
    wrong_rates = []
    
    for entry in entries:
        timestamp_str = entry.get("timestamp")
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        
        if entry.get("type") == "user":
            user_timestamps.append(timestamp)
        elif entry.get("type") == "assistant":
            assistant_timestamps.append(timestamp)
            
            if user_timestamps and len(assistant_timestamps) <= len(user_timestamps):
                user_time = user_timestamps[len(assistant_timestamps) - 1]
                response_time = (timestamp - user_time).total_seconds()
                
                if "message" in entry and "usage" in entry["message"]:
                    output_tokens = entry["message"]["usage"].get("output_tokens", 0)
                    if response_time > 0 and output_tokens > 0:
                        rate = output_tokens / response_time
                        wrong_rates.append(rate)
                        print(f"Assistant response {len(assistant_timestamps)}:")
                        print(f"  Output tokens: {output_tokens}")
                        print(f"  Response time: {response_time}s (includes thinking!)")
                        print(f"  Rate: {rate:.1f} t/s\n")
    
    if wrong_rates:
        avg_wrong = sum(wrong_rates) / len(wrong_rates)
        print(f"Average (wrong): {avg_wrong:.1f} t/s\n")
    
    print("=== Proposed (Correct) Method ===")
    print("For entries with output tokens, measure actual generation time")
    print("Problem: We don't have intermediate timestamps!\n")
    
    print("The transcript only has timestamps when messages are complete.")
    print("We cannot accurately measure token generation rate without:")
    print("1. Start and end timestamps for token generation, OR")
    print("2. A 'duration' field indicating generation time")
    print("\nThe best we can do is assume the entire response time is generation time,")
    print("which gives us the same (incorrect) result as the current method.")

if __name__ == "__main__":
    analyze_transcript("test_transcript.jsonl")