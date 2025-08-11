#!/usr/bin/env python3
"""Verify the token rate calculation is working correctly."""

import json
from datetime import datetime

def verify_calculation(filepath):
    """Manually calculate token rates to verify the algorithm."""
    
    entries = []
    with open(filepath, 'r') as f:
        for line in f:
            entries.append(json.loads(line.strip()))
    
    print("=== Manual Token Rate Calculation ===\n")
    
    last_user_timestamp = None
    token_rates = []
    
    for i, entry in enumerate(entries):
        timestamp_str = entry.get("timestamp")
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        entry_type = entry.get("type")
        
        # Track last user message
        if entry_type == "user":
            last_user_timestamp = timestamp
            print(f"Entry {i}: User message at {timestamp_str}")
        
        # Check for output tokens
        output_tokens = 0
        if entry_type == "assistant" and "message" in entry:
            usage = entry["message"].get("usage", {})
            output_tokens = usage.get("output_tokens", 0)
            print(f"Entry {i}: Assistant message at {timestamp_str}")
            print(f"         Output tokens: {output_tokens}")
        
        # Calculate rate if we have output tokens and a prior user message
        if output_tokens > 0 and last_user_timestamp:
            time_since_user = (timestamp - last_user_timestamp).total_seconds()
            if time_since_user > 0:
                rate = output_tokens / time_since_user
                token_rates.append(rate)
                print(f"         Time since user: {time_since_user}s")
                print(f"         Rate: {rate:.1f} t/s\n")
    
    if token_rates:
        avg_rate = sum(token_rates) / len(token_rates)
        print(f"Calculated rates: {[f'{r:.1f}' for r in token_rates]}")
        print(f"Average rate: {avg_rate:.1f} t/s")
        print(f"\nExpected output: ⚙ {int(round(avg_rate))}t/s")
    else:
        print("No token rates calculated")

if __name__ == "__main__":
    verify_calculation("test_transcript.jsonl")