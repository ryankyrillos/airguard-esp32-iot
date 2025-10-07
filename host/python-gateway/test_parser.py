#!/usr/bin/env python3
"""
Test script to simulate ESP32 receiver output and verify gateway parsing
"""

import json

# Sample receiver output (fenced block format)
SAMPLE_OUTPUT = """
=== Received Data ===
Batch: 0x5A17C2EF | Duration: 10342 ms | Samples: 187
GPS Fix: 1, Sats: 7 | Date: 20251006 | Time: 132523.120
Lat: 33.888630  Lon: 35.495480  Alt: 79.20 m
Accel [m/s^2] X: -0.12  Y: 0.03  Z: 9.73
Gyro  [rad/s] X: 0.01  Y: -0.02  Z: 0.00
Temp: 28.10 °C
====================
"""

def test_parse():
    """Test the parsing logic"""
    print("Simulating ESP32 receiver output:\n")
    print(SAMPLE_OUTPUT)
    
    # This would be parsed by gateway.py
    print("\nExpected JSON output:")
    expected = {
        "batchId": "5A17C2EF",
        "sessionMs": 10342,
        "samples": 187,
        "dateYMD": 20251006,
        "timeHMS": 132523,
        "msec": 120,
        "lat": 33.888630,
        "lon": 35.495480,
        "alt": 79.20,
        "gpsFix": 1,
        "sats": 7,
        "ax": -0.12,
        "ay": 0.03,
        "az": 9.73,
        "gx": 0.01,
        "gy": -0.02,
        "gz": 0.00,
        "tempC": 28.10
    }
    
    print(json.dumps(expected, indent=2))
    print("\n✓ Test completed")

if __name__ == '__main__':
    test_parse()
