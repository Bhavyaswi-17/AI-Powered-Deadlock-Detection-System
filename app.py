from flask import Flask, render_template, request, jsonify
import numpy as np
from rag_visualizer import build_rag_data
from bankers import bankers_algorithm
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    processes = int(data.get('processes'))
    resources = int(data.get('resources'))
    alloc = np.array(data.get('allocation'), dtype=int)
    req = np.array(data.get('request'), dtype=int)
    avail = np.array(data.get('available'), dtype=int)

    safe, sequence, deadlocked = bankers_algorithm(alloc, req, avail.copy())
    graph = build_rag_data(processes, resources, alloc, req, avail)
    return jsonify({'safe': bool(safe), 'sequence': sequence, 'deadlocked': deadlocked, 'graph': graph})

def resolve_by_termination(alloc, req, avail):
    alloc = alloc.copy()
    req = req.copy()
    avail = avail.copy()
    steps = []
    kill_order = []
    P, R = alloc.shape

    def run_bank():
        safe, seq, dead = bankers_algorithm(alloc, req, avail.copy())
        return safe, seq, dead

    safe, seq, dead = run_bank()
    if safe:
        return steps, seq, kill_order, dead, alloc

    # choose victims iteratively (least allocated resources)
    iteration = 0
    while not safe and len(dead) > 0 and iteration < P:
        costs = sorted([(int(alloc[i].sum()), i) for i in dead])
        cost, victim = costs[0]
        kill_order.append(victim)
        steps.append(f"Terminate P{victim+1} — frees {list(map(int, alloc[victim]))}")
        # free resources
        avail = avail + alloc[victim]
        alloc[victim] = np.zeros(R, dtype=int)
        req[victim] = np.zeros(R, dtype=int)
        safe, seq, dead = run_bank()
        iteration += 1

    return steps, seq if safe else [], kill_order, dead, alloc

@app.route('/resolve', methods=['POST'])
def resolve():
    data = request.json
    processes = int(data.get('processes'))
    resources = int(data.get('resources'))
    alloc = np.array(data.get('allocation'), dtype=int)
    req = np.array(data.get('request'), dtype=int)
    avail = np.array(data.get('available'), dtype=int)

    steps, final_seq, kill_order, final_deadlocked, final_alloc = resolve_by_termination(alloc, req, avail.copy())

    # human-friendly explanation
    explanation_lines = []
    if kill_order:
        explanation_lines.append("Deadlock detected.\n")
        for idx, p in enumerate(kill_order):
            explanation_lines.append(f"{idx+1}. Terminate P{p+1} (chosen because it holds few resources).")
            explanation_lines.append(f"   Freed resources: {list(map(int, alloc[p]))}")
            explanation_lines.append("")
        if final_seq:
            explanation_lines.append("Final safe sequence after recovery: " + " -> ".join([f"P{p+1}" for p in final_seq]))
        else:
            explanation_lines.append("No safe sequence found after recovery.")
    else:
        explanation_lines.append("No deadlock detected. No recovery needed.")

    graph = build_rag_data(processes, resources, final_alloc, req, avail)
    return jsonify({'steps': steps, 'explanation': "\\n".join(explanation_lines), 'final_sequence': final_seq, 'deadlocked': final_deadlocked, 'graph': graph})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
