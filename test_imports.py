#!/usr/bin/env python3
"""Test imports to find errors"""
import sys

print("Testing imports...")
print()

modules = [
    'fastapi',
    'uvicorn',
    'gradio',
    'model_router',
    'nvidia_integration',
    'jareth2_agent',
    'jareth2_daemon',
    'web_ui',
    'api_server'
]

for module in modules:
    try:
        __import__(module)
        print(f"✓ {module}")
    except Exception as e:
        print(f"✗ {module}: {e}")
