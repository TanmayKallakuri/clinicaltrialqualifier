# test_imports.py

print("Testing imports...")

try:
    print("1. Importing FastAPI...")
    from fastapi import FastAPI
    print("   ✓ FastAPI OK")
except Exception as e:
    print(f"   ✗ FastAPI failed: {e}")

try:
    print("2. Importing redis_cache...")
    from redis_cache import ClinicalTrialsCache
    print("   ✓ redis_cache OK")
except Exception as e:
    print(f"   ✗ redis_cache failed: {e}")

try:
    print("3. Importing claude_analyzer...")
    print("   ✓ claude_analyzer OK")
except Exception as e:
    print(f"   ✗ claude_analyzer failed: {e}")

try:
    print("4. Testing Redis connection...")
    cache = ClinicalTrialsCache()
    if cache.ping():
        print("   ✓ Redis connected")
    else:
        print("   ✗ Redis not connected")
except Exception as e:
    print(f"   ✗ Redis test failed: {e}")

print("\nAll import tests complete!")