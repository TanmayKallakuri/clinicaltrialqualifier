# flask_backend.py

from flask import Flask, jsonify, request
from flask_cors import CORS
import redis
import json
from anthropic import Anthropic
import os

print("Starting Flask backend...")

app = Flask(__name__)
CORS(app)  # Enable CORS

# Initialize
print("Connecting to Redis...")
try:
    r = redis.Redis(host='localhost', port=6379, decode_responses=True, socket_connect_timeout=2)
    r.ping()
    print("[OK] Redis connected!")
except Exception as e:
    print(f"[WARN] Redis not available: {e}")
    print("       Cache endpoints will not work.")
    r = None

print("Setting up Claude...")
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("[WARN] ANTHROPIC_API_KEY not set!")
    print("       AI endpoints will not work.")
    claude = None
else:
    claude = Anthropic(api_key=api_key)
    print("[OK] Claude ready!")

print("Routes registered!\n")

@app.route('/')
def home():
    """Health check"""
    redis_ok = False
    if r:
        try:
            redis_ok = r.ping()
        except:
            pass

    return jsonify({
        "status": "active",
        "redis": "connected" if redis_ok else "disconnected",
        "claude": "ready" if claude else "not configured",
        "message": "Clinical Trials API is running"
    })

@app.route('/api/cache', methods=['POST'])
def cache_data():
    """Cache clinical trials data"""
    if not r:
        return jsonify({"error": "Redis not available"}), 503

    try:
        data = request.json
        condition = data['condition']
        studies = data['studies']

        # Cache all studies
        r.set('trials:all', json.dumps(studies))

        # Cache by condition
        r.set(f'trials:{condition}', json.dumps(studies))

        # Metadata
        from datetime import datetime
        metadata = {
            "total_studies": len(studies),
            "last_updated": datetime.utcnow().isoformat(),
            "condition": condition
        }
        r.set('trials:metadata', json.dumps(metadata))

        return jsonify({
            "status": "success",
            "message": f"Cached {len(studies)} studies",
            "condition": condition,
            "studies_cached": len(studies)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/studies')
def get_studies():
    """Get cached studies"""
    if not r:
        return jsonify({"error": "Redis not available"}), 503

    try:
        condition = request.args.get('condition')
        limit = int(request.args.get('limit', 50))

        if condition:
            key = f'trials:{condition}'
        else:
            key = 'trials:all'

        cached = r.get(key)

        if not cached:
            return jsonify({"error": "No cached data. Use POST /api/cache first"}), 404

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
    """Ask Claude to analyze data"""
    if not r:
        return jsonify({"error": "Redis not available"}), 503
    if not claude:
        return jsonify({"error": "Claude API not configured. Set ANTHROPIC_API_KEY"}), 503

    try:
        question = request.json['question']

        # Get data from cache
        cached = r.get('trials:all')
        if not cached:
            return jsonify({"error": "No data in cache"}), 404

        studies = json.loads(cached)

        print(f"\n{'='*60}")
        print(f"CLAUDE ANALYSIS")
        print(f"Question: {question}")
        print(f"Studies: {len(studies)}")

        # Limit to first 40 studies for token management
        sample = studies[:40]

        # Call Claude
        message = claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{
                "role": "user",
                "content": f"""You are analyzing clinical trials data.

Dataset: {len(studies)} total studies
Sample: {len(sample)} studies

Data:
{json.dumps(sample, indent=2)}

Question: {question}

Provide a detailed analysis with specific NCT IDs when relevant."""
            }]
        )

        answer = message.content[0].text

        print("Analysis complete!")
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
        return jsonify({"error": str(e)}), 500

@app.route('/api/cache-stats')
def cache_stats():
    """Get Redis cache statistics"""
    if not r:
        return jsonify({"error": "Redis not available"}), 503

    try:
        info = r.info()
        keys = r.keys('trials:*')

        metadata_str = r.get('trials:metadata')
        metadata = json.loads(metadata_str) if metadata_str else None

        return jsonify({
            "redis": {
                "redis_version": info.get('redis_version'),
                "connected_clients": info.get('connected_clients'),
                "used_memory_human": info.get('used_memory_human'),
                "total_keys": len(keys),
                "uptime_seconds": info.get('uptime_in_seconds')
            },
            "data": metadata
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/summary')
def get_summary():
    """Get dataset summary"""
    if not r:
        return jsonify({"error": "Redis not available"}), 503
    if not claude:
        return jsonify({"error": "Claude API not configured. Set ANTHROPIC_API_KEY"}), 503

    try:
        cached = r.get('trials:all')
        if not cached:
            return jsonify({"error": "No data"}), 404

        studies = json.loads(cached)

        question = "Provide a comprehensive summary of this clinical trials dataset."

        message = claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": f"Data: {json.dumps(studies[:30])}\n\n{question}"
            }]
        )

        return jsonify({
            "question": question,
            "answer": message.content[0].text
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sponsors')
def get_sponsors():
    """Show sponsor integrations"""
    return jsonify({
        "sponsors": [
            {"name": "Redis", "status": "Integrated"},
            {"name": "Claude AI", "status": "Integrated"},
            {"name": "Postman", "status": "Utilized"}
        ]
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("SERVER STARTING ON http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True
    )