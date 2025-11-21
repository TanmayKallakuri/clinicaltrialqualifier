# backend.py - COMPLETE Flask backend with Redis + Claude

from flask import Flask, jsonify, request
from flask_cors import CORS
import redis
import json
from anthropic import Anthropic
import os
from datetime import datetime

print("\n" + "="*60)
print("CLINICAL TRIALS API - STARTING")
print("="*60)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize Redis
print("Connecting to Redis...")
try:
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True, socket_connect_timeout=2)
    redis_client.ping()
    print("[OK] Redis: Connected")
except Exception as e:
    print(f"[WARN] Redis: Connection failed - {e}")
    redis_client = None

# Initialize Claude
print("Initializing Claude AI...")
api_key = os.getenv("ANTHROPIC_API_KEY")
if api_key:
    claude_client = Anthropic(api_key=api_key)
    print(f"[OK] Claude: API key set ({api_key[:20]}...)")
else:
    print("[WARN] Claude: API key not set")
    claude_client = None

print("="*60)
print("Server ready on http://localhost:5000")
print("="*60 + "\n")


# ============================================================
# ENDPOINTS
# ============================================================

@app.route('/')
def health_check():
    """Health check - shows system status"""
    redis_status = "disconnected"
    if redis_client:
        try:
            redis_client.ping()
            redis_status = "connected"
        except:
            pass

    claude_status = "ready" if claude_client else "not configured"

    # Get metadata if available
    metadata = None
    if redis_client:
        try:
            meta_str = redis_client.get('trials:metadata')
            if meta_str:
                metadata = json.loads(meta_str)
        except:
            pass

    return jsonify({
        "status": "active",
        "redis": redis_status,
        "claude": claude_status,
        "message": "Clinical Trials API is running",
        "data": metadata
    })


@app.route('/api/cache', methods=['POST'])
def cache_data():
    """
    Cache clinical trials data in Redis

    Your teammate POSTs their JSON here:
    {
        "condition": "cancer",
        "studies": [...]
    }
    """
    if not redis_client:
        return jsonify({"error": "Redis not connected"}), 503
    
    try:
        data = request.json
        condition = data.get('condition', 'unknown')
        studies = data.get('studies', [])
        
        if not studies:
            return jsonify({"error": "No studies provided"}), 400
        
        print(f"\n{'='*60}")
        print(f"CACHING DATA")
        print(f"Condition: {condition}")
        print(f"Studies: {len(studies)}")
        
        # Cache by condition
        key = f"trials:{condition.lower()}"
        redis_client.set(key, json.dumps(studies))
        redis_client.expire(key, 3600)  # 1 hour TTL
        print(f"[OK] Cached as: {key}")

        # Cache all studies
        redis_client.set('trials:all', json.dumps(studies))
        redis_client.expire('trials:all', 3600)
        print(f"[OK] Cached as: trials:all")

        # Store metadata
        metadata = {
            "total_studies": len(studies),
            "last_updated": datetime.utcnow().isoformat(),
            "condition": condition
        }
        redis_client.set('trials:metadata', json.dumps(metadata))
        redis_client.expire('trials:metadata', 3600)
        print(f"[OK] Metadata stored")
        
        print(f"{'='*60}\n")
        
        return jsonify({
            "status": "success",
            "message": f"Cached {len(studies)} studies in Redis",
            "condition": condition,
            "studies_cached": len(studies)
        })
        
    except Exception as e:
        print(f"[ERROR] Caching error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/studies')
def get_studies():
    """
    Get cached studies from Redis

    Query params:
    - condition: filter by condition (optional)
    - limit: max results (default 50)
    """
    if not redis_client:
        return jsonify({"error": "Redis not connected"}), 503
    
    try:
        condition = request.args.get('condition')
        limit = int(request.args.get('limit', 50))
        
        # Get from cache
        if condition:
            key = f"trials:{condition.lower()}"
        else:
            key = 'trials:all'
        
        cached = redis_client.get(key)
        
        if not cached:
            return jsonify({
                "error": "No cached data available",
                "message": "Use POST /api/cache to load data first"
            }), 404
        
        studies = json.loads(cached)
        
        return jsonify({
            "total": len(studies),
            "returned": min(len(studies), limit),
            "studies": studies[:limit],
            "source": "Redis Cache"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/ask', methods=['POST'])
def ask_claude():
    """
    Ask Claude AI to analyze clinical trials data

    THIS IS YOUR MAIN FEATURE!

    Request body:
    {
        "question": "What are the most common Phase 3 cancer trials?"
    }
    """
    if not redis_client:
        return jsonify({"error": "Redis not connected"}), 503

    if not claude_client:
        return jsonify({"error": "Claude API not configured. Set ANTHROPIC_API_KEY"}), 503
    
    try:
        data = request.json
        question = data.get('question', '')
        
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        # Get data from Redis
        cached = redis_client.get('trials:all')
        
        if not cached:
            return jsonify({
                "error": "No data in cache",
                "message": "Use POST /api/cache to load data first"
            }), 404
        
        studies = json.loads(cached)
        
        print(f"\n{'='*60}")
        print(f"CLAUDE ANALYSIS REQUEST")
        print(f"{'='*60}")
        print(f"Question: {question}")
        print(f"Studies in cache: {len(studies)}")
        
        # Limit to 40 studies for token management
        sample = studies[:40]
        
        print(f"Analyzing {len(sample)} studies...")
        
        # Build context for Claude
        context = f"""You are a medical research AI assistant analyzing clinical trials data.

DATASET INFORMATION:
- Total studies available: {len(studies)}
- Studies in this analysis: {len(sample)}

CLINICAL TRIALS DATA:
{json.dumps(sample, indent=2)}

RESEARCHER QUESTION:
{question}

INSTRUCTIONS:
1. Provide a detailed, data-driven analysis
2. Reference specific NCT IDs when relevant
3. Identify patterns across trials
4. Be concise but thorough
5. Use medical research terminology appropriately"""

        # Call Claude API
        message = claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{
                "role": "user",
                "content": context
            }]
        )
        
        answer = message.content[0].text

        print("[OK] Analysis complete!")
        print(f"{'='*60}\n")
        
        return jsonify({
            "question": question,
            "answer": answer,
            "total_studies": len(studies),
            "analyzed_studies": len(sample),
            "model": "claude-sonnet-4-20250514",
            "data_source": "Redis Cache"
        })
        
    except Exception as e:
        print(f"[ERROR] Analysis error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/cache-stats')
def cache_stats():
    """
    Get Redis cache statistics

    SHOW THIS IN YOUR DEMO!
    Displays performance metrics
    """
    if not redis_client:
        return jsonify({"error": "Redis not connected"}), 503
    
    try:
        # Get Redis info
        info = redis_client.info()
        
        # Get all trial keys
        keys = redis_client.keys('trials:*')
        
        # Get metadata
        meta_str = redis_client.get('trials:metadata')
        metadata = json.loads(meta_str) if meta_str else None
        
        return jsonify({
            "redis": {
                "redis_version": info.get('redis_version'),
                "connected_clients": info.get('connected_clients'),
                "used_memory_human": info.get('used_memory_human'),
                "total_keys": len(keys),
                "cached_keys": [k for k in keys],
                "uptime_seconds": info.get('uptime_in_seconds')
            },
            "data": metadata
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/summary')
def get_summary():
    """
    Get AI-generated summary of entire dataset
    """
    if not redis_client:
        return jsonify({"error": "Redis not connected"}), 503
    if not claude_client:
        return jsonify({"error": "Claude API not configured. Set ANTHROPIC_API_KEY"}), 503
    
    try:
        cached = redis_client.get('trials:all')
        
        if not cached:
            return jsonify({"error": "No data in cache"}), 404
        
        studies = json.loads(cached)
        
        question = "Provide a comprehensive summary of this clinical trials dataset, including total studies, key conditions, trial phases, and notable patterns."
        
        message = claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": f"Data: {json.dumps(studies[:30])}\n\nQuestion: {question}"
            }]
        )
        
        return jsonify({
            "question": question,
            "answer": message.content[0].text,
            "studies_analyzed": len(studies)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/sponsors')
def get_sponsors():
    """
    Show sponsor technology integrations
    For demo purposes
    """
    return jsonify({
        "sponsors": [
            {
                "name": "Redis",
                "role": "High-performance caching",
                "status": "Integrated" if redis_client else "Not connected",
                "proof": "Memurai running on localhost:6379"
            },
            {
                "name": "Claude AI",
                "role": "AI-powered research analysis",
                "status": "Integrated" if claude_client else "Not configured",
                "proof": "Claude Sonnet 4 API connected"
            },
            {
                "name": "Postman",
                "role": "API testing & documentation",
                "status": "Utilized",
                "proof": "Used for ClinicalTrials.gov API exploration"
            }
        ],
        "architecture": "ClinicalTrials.gov -> Redis Cache -> Claude Analysis -> Research Dashboard"
    })


@app.route('/api/clear', methods=['DELETE'])
def clear_cache():
    """Clear all cached data"""
    if not redis_client:
        return jsonify({"error": "Redis not connected"}), 503
    
    try:
        keys = redis_client.keys('trials:*')
        if keys:
            redis_client.delete(*keys)
            return jsonify({
                "status": "success",
                "message": f"Cleared {len(keys)} keys from cache"
            })
        else:
            return jsonify({
                "status": "success",
                "message": "Cache was already empty"
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True
    )