"""
Flask API Server for Fees Explainer Agent
Simulates n8n webhook integration for local testing
"""

from flask import Flask, request, jsonify
from fees_explainer_agent import FeesExplainerAgent
from datetime import datetime

app = Flask(__name__)

# In-memory session storage (use Redis in production)
sessions = {}


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})


@app.route('/api/fees-explainer/start', methods=['POST'])
def start_conversation():
    """
    Start fee explanation conversation.
    Endpoint: POST /api/fees-explainer/start
    Body: {"query": "What is ELSS exit load?"}
    """
    try:
        data = request.get_json()
        query = data.get('query')

        if not query:
            return jsonify({"error": "Missing 'query' field"}), 400

        # Initialize agent
        agent = FeesExplainerAgent()
        response = agent.start_conversation(query)

        # Store session
        session_id = str(datetime.now().timestamp())
        sessions[session_id] = agent

        response['session_id'] = session_id

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/fees-explainer/answers', methods=['POST'])
def process_answers():
    """
    Process clarifying answers.
    Endpoint: POST /api/fees-explainer/answers
    Body: {"session_id": "...", "answers": {...}}
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        answers = data.get('answers')

        if not session_id or not answers:
            return jsonify({"error": "Missing 'session_id' or 'answers'"}), 400

        # Get agent from session
        agent = sessions.get(session_id)
        if not agent:
            return jsonify({"error": "Invalid session_id"}), 404

        # Process answers
        response = agent.process_clarifiers(answers)
        response['session_id'] = session_id

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/fees-explainer/approvals', methods=['POST'])
def process_approvals():
    """
    Process MCP action approvals.
    Endpoint: POST /api/fees-explainer/approvals
    Body: {"session_id": "...", "approved_actions": [...]}
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        approved_actions = data.get('approved_actions', [])

        if not session_id:
            return jsonify({"error": "Missing 'session_id'"}), 400

        # Get agent from session
        agent = sessions.get(session_id)
        if not agent:
            return jsonify({"error": "Invalid session_id"}), 404

        # Approve actions
        for approval in approved_actions:
            action_id = approval.get('action_id')
            is_approved = approval.get('approved', False)

            if is_approved:
                agent.approve_mcp_action(action_id)

        # Execute approved actions
        results = agent.execute_approved_mcp_actions()
        results['session_id'] = session_id

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/fees-explainer/session/<session_id>', methods=['GET'])
def get_session_summary(session_id):
    """Get session summary."""
    agent = sessions.get(session_id)
    if not agent:
        return jsonify({"error": "Invalid session_id"}), 404

    summary = agent.get_conversation_summary()
    summary['session_id'] = session_id

    return jsonify(summary), 200


if __name__ == '__main__':
    print("=" * 60)
    print("Fees Explainer Agent API Server")
    print("=" * 60)
    print("\nEndpoints:")
    print("  GET  /health")
    print("  POST /api/fees-explainer/start")
    print("  POST /api/fees-explainer/answers")
    print("  POST /api/fees-explainer/approvals")
    print("  GET  /api/fees-explainer/session/<session_id>")
    print("\nStarting server on http://localhost:5000")
    print("=" * 60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
