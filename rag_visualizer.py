def build_rag_data(P, R, alloc, req, avail):
    nodes = []
    edges = []

    coords = {
        "p1": (0, -150),
        "p2": (0, 150),
        "r1": (250, 0),
        "r2": (-250, 0),
    }

    # Processes (rectangles)
    for i in range(P):
        key = f"p{i+1}"
        x, y = coords.get(key, (0, i*150))
        nodes.append({
            "id": f"p{i}",
            "label": f"P{i+1}",
            "shape": "box",
            "group": "process",
            "color": {"background": "#73a7ff", "border": "#1b5fde"},
            "x": x,
            "y": y,
            "font": {"color": "#000"}
        })

    # Resources (circles)
    for j in range(R):
        key = f"r{j+1}"
        x, y = coords.get(key, (300, j*120))
        nodes.append({
            "id": f"r{j}",
            "label": f"R{j+1}",
            "shape": "dot",
            "group": "resource",
            "size": 35,
            "color": {"background": "#b2ffb8", "border": "#37b34a"},
            "x": x,
            "y": y,
            "font": {"color": "#000"}
        })

    # Edges: R -> P (allocation), P -> R (request)
    for i in range(P):
        for j in range(R):
            if int(alloc[i][j]) > 0:
                edges.append({"from": f"r{j}", "to": f"p{i}", "label": f"A{int(alloc[i][j])}", "arrows": "to"})
            if int(req[i][j]) > 0:
                edges.append({"from": f"p{i}", "to": f"r{j}", "label": f"N{int(req[i][j])}", "arrows": "to"})
    return {"nodes": nodes, "edges": edges}
