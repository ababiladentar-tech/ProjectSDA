"""Flask backend untuk Bubble-Sort Star Graph Visualization"""

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import os
from bsn_logic import (
    build_bsn,
    theorem_cut_set,
    closed_neighborhood,
    analyze_remaining_graph,
    exact_kappa_nb,
    exact_lambda_nb,
    cari_node_penyerang_otomatis,
    subversi_vertex,
    simulasi_edge_subversion_murni,
    vertex_attack,
    edge_attack,
)

app = Flask(__name__)
CORS(app)

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/')
def index():
    """Serve the HTML visualization"""
    html_path = os.path.join(os.path.dirname(__file__), 'preview (1).html')
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    return html_content


@app.route('/api/graph/<int:n>', methods=['GET'])
def api_build_graph(n):
    """Build BSn graph and return serializable data"""
    try:
        if n < 2 or n > 8:
            return jsonify({'error': 'n must be between 2 and 8'}), 400
        
        graph = build_bsn(n)
        
        # Convert graph data to JSON-serializable format
        vertices = [list(v) for v in graph['vertices']]
        
        # Convert adjacency sets to lists
        adjacency = [list(s) for s in graph['adjacency']]
        
        # Build edges list
        edges = []
        edges_seen = set()
        for u in range(len(adjacency)):
            for v in adjacency[u]:
                edge_key = tuple(sorted([u, v]))
                if edge_key not in edges_seen:
                    edges_seen.add(edge_key)
                    edges.append({'a': u, 'b': v})
        
        return jsonify({
            'n': n,
            'vertices': vertices,
            'vertex_count': graph['vertex_count'],
            'edge_count': graph['edge_count'],
            'degree': graph['degree'],
            'theoretical_kappa_nb': graph['theoretical_kappa_nb'],
            'theoretical_lambda_nb': graph['theoretical_lambda_nb'],
            'adjacency': adjacency,
            'edges': edges,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/theorem-cut/<int:n>', methods=['GET'])
def api_theorem_cut(n):
    """Get theorem-based cut set"""
    try:
        if n < 2 or n > 8:
            return jsonify({'error': 'n must be between 2 and 8'}), 400
        
        graph = build_bsn(n)
        cut_set = theorem_cut_set(graph)
        
        adjacency = [list(s) for s in graph['adjacency']]
        removed = closed_neighborhood(adjacency, cut_set)
        remaining = [i for i in range(graph['vertex_count']) if i not in removed]
        reason = analyze_remaining_graph(adjacency, remaining)
        
        return jsonify({
            'cut_set': cut_set,
            'removed_nodes': sorted(list(removed)),
            'remaining_nodes': remaining,
            'result': reason,
            'cut_set_size': len(cut_set),
            'removed_count': len(removed),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/exact-kappa/<int:n>', methods=['GET'])
def api_exact_kappa(n):
    """Get exact kappa (vertex connectivity)"""
    try:
        if n < 2 or n > 5:
            return jsonify({'info': 'Exact computation only available for n <= 5'}), 400
        
        graph = build_bsn(n)
        result = exact_kappa_nb(graph)
        
        if result is None:
            return jsonify({'error': 'No exact result found'}), 404
        
        return jsonify({
            'k': result['k'],
            'cut_set': result['cut_set'],
            'removed': sorted(result['removed']),
            'remaining': result['remaining'],
            'reason': result['reason'],
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/exact-lambda/<int:n>', methods=['GET'])
def api_exact_lambda(n):
    """Get exact lambda (edge connectivity)"""
    try:
        if n < 2 or n > 5:
            return jsonify({'info': 'Exact computation only available for n <= 5'}), 400
        
        graph = build_bsn(n)
        result = exact_lambda_nb(graph)
        
        if result is None:
            return jsonify({'error': 'No exact result found'}), 404
        
        return jsonify({
            'k': result['k'],
            'cut_edges': result['cut_edges'],
            'reason': result['reason'],
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/vertex-subversion/<int:n>', methods=['GET'])
def api_vertex_subversion(n):
    """Simulate vertex subversion (dari nodes.py)"""
    try:
        if n < 2 or n > 8:
            return jsonify({'error': 'n must be between 2 and 8'}), 400

        target_index = request.args.get('target', default=0, type=int)
        graph = build_bsn(n)

        if target_index < 0 or target_index >= graph['vertex_count']:
            return jsonify({'error': 'target index out of range'}), 400

        result = vertex_attack(graph, target_index)
        result['target_vertex'] = list(graph['vertices'][target_index])
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/edge-subversion/<int:n>', methods=['GET'])
def api_edge_subversion(n):
    """Simulate edge subversion (dari edges.py)"""
    try:
        if n < 2 or n > 8:
            return jsonify({'error': 'n must be between 2 and 8'}), 400

        target_index = request.args.get('target', default=0, type=int)
        graph = build_bsn(n)

        if target_index < 0 or target_index >= graph['vertex_count']:
            return jsonify({'error': 'target index out of range'}), 400

        result = edge_attack(graph, target_index)
        result['target_vertex'] = list(graph['vertices'][target_index])
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/summary/<int:n>', methods=['GET'])
def api_summary(n):
    """Get complete graph summary with all analyses"""
    try:
        if n < 2 or n > 8:
            return jsonify({'error': 'n must be between 2 and 8'}), 400
        
        graph = build_bsn(n)
        
        # Theorem cut
        theorem_cut = theorem_cut_set(graph)
        adjacency = [list(s) for s in graph['adjacency']]
        removed_theorem = closed_neighborhood(adjacency, theorem_cut)
        remaining_theorem = [i for i in range(graph['vertex_count']) if i not in removed_theorem]
        theorem_reason = analyze_remaining_graph(adjacency, remaining_theorem)
        
        # Exact kappa (if available)
        exact_kappa = exact_kappa_nb(graph) if n <= 5 else None
        
        # Exact lambda (if available)
        exact_lambda = exact_lambda_nb(graph) if n <= 5 else None
        
        # Vertex subversion
        attacker_nodes = cari_node_penyerang_otomatis(n, graph)
        removed_vertex = subversi_vertex(graph, attacker_nodes)
        remaining_vertex = [i for i in range(graph['vertex_count']) if i not in removed_vertex]
        vertex_reason = analyze_remaining_graph(adjacency, remaining_vertex)
        
        # Edge subversion
        target_node = 0
        neighbor_edges = []
        for neighbor in graph['adjacency'][target_node]:
            neighbor_edges.append((target_node, neighbor))
        edges_target = neighbor_edges[:graph['theoretical_lambda_nb']]
        nodes_terserang, edges_kedampak = simulasi_edge_subversion_murni(graph, edges_target)
        remaining_edge = [i for i in range(graph['vertex_count']) if i not in nodes_terserang]
        edge_reason = analyze_remaining_graph(adjacency, remaining_edge)
        
        return jsonify({
            'n': n,
            'vertex_count': graph['vertex_count'],
            'edge_count': graph['edge_count'],
            'degree': graph['degree'],
            'theoretical_kappa': graph['theoretical_kappa_nb'],
            'theoretical_lambda': graph['theoretical_lambda_nb'],
            'theorem_cut': {
                'size': len(theorem_cut),
                'nodes': theorem_cut,
                'removed_count': len(removed_theorem),
                'result': theorem_reason,
            },
            'exact_kappa': {
                'k': exact_kappa['k'],
                'result': exact_kappa['reason'],
            } if exact_kappa else None,
            'exact_lambda': {
                'k': exact_lambda['k'],
                'result': exact_lambda['reason'],
            } if exact_lambda else None,
            'vertex_subversion': {
                'attacker_count': len(attacker_nodes),
                'removed_count': len(removed_vertex),
                'result': vertex_reason,
            },
            'edge_subversion': {
                'attacked_edges': len(edges_target),
                'attacked_nodes': len(nodes_terserang),
                'result': edge_reason,
            },
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("BSn Graph Visualization Backend")
    print("=" * 60)
    print("\n✓ Flask server starting on http://localhost:5000")
    print("\nAPI Endpoints:")
    print("  GET  /api/graph/<n>")
    print("  GET  /api/theorem-cut/<n>")
    print("  GET  /api/exact-kappa/<n>")
    print("  GET  /api/exact-lambda/<n>")
    print("  GET  /api/vertex-subversion/<n>")
    print("  GET  /api/edge-subversion/<n>")
    print("  GET  /api/summary/<n>")
    print("\n" + "=" * 60 + "\n")
    
    app.run(debug=True, port=5000, host='127.0.0.1')
