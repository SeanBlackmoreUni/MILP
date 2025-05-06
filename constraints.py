"""
File for constraints
"""

"""
File for constraints
"""
def add_constraints(model, data, variables):
    vertices = data["vertices"]
    arcs = data["arcs"]
    D_max = data["other"]["D_bar"]
    Q = data["other"]["Q"]
    Tmax = data["other"]["T_bar"]

    V = list(vertices.keys())
    V_prime = list(data["vertices_prime"].keys())
    E = list(arcs.keys())

    # Lookup dictionaries
    N_i = {v_id: vertices[v_id]['N_i'] for v_id in V}
    S_i = {v_id: vertices[v_id]['S_i'] for v_id in V}
    T_ij = {(i, j): arcs[(i, j)]['time'] for (i, j) in E}
    D_ij = {(i, j): arcs[(i, j)]['distance'] for (i, j) in E}

    x = variables["x"]
    y = variables["y"]
    z = variables["z"]
    z_prime = variables["z_prime"]
    k = variables['k']

    # --- Constraints ---

   # (2) Each customer has exactly one incoming arc
    for j in V_prime:
        model.addConstr(sum(x[i, j] for i in V if (i, j) in E) == 1,
                        name=f"incoming_arc_{j}")

    # (3) Each customer has exactly one outgoing arc
    for i in V_prime:
        model.addConstr(sum(x[i, j] for j in V if (i, j) in E) == 1,
                        name=f"outgoing_arc_{i}")

    # (4) Vehicles leave depot k times
    model.addConstr(sum(x[0, i] for i in V_prime if (0, i) in E) == k,
                    name="depot_departures")

    # (5) Vehicles return to depot k times
    model.addConstr(sum(x[i, 0] for i in V_prime if (i, 0) in E) == k,
                    name="depot_returns")

    # (6) Package capacity constraint
    for i, j in E:
        model.addConstr(y[i, j] <= Q * x[i, j],
                        name=f"capacity_arc_{i}_{j}")

    # (7) Flow conservation for packages
    for i in V_prime:
        model.addConstr(
            sum(y[i, j] for j in V if (i, j) in E) - 
            sum(y[j, i] for j in V if (j, i) in E) == N_i[i],
            name=f"package_flow_{i}"
        )

    # (8) Travel time flow conservation
    for i in V_prime:
        model.addConstr(
            sum(z[i, j] for j in V if (i, j) in E) - 
            sum(z[j, i] for j in V if (j, i) in E) == 
            sum((T_ij[i, j] + S_i[i]) * x[i, j] for j in V if (i, j) in E),
            name=f"time_flow_{i}"
        )

    # (9) Total travel time upper bound
    for i in V:
        for j in V_prime:
            if (i, j) in E:
                model.addConstr(z[i, j] <= Tmax * x[i, j],
                                name=f"time_upper_{i}_{j}")

    # (10) Lower bound on travel time if arc is used
    for i in V_prime:
        for j in V:
            if (i, j) in E:
                model.addConstr(z[i, j] >= (T_ij[i, j] + S_i[i]) * x[i, j],
                                name=f"time_lower_{i}_{j}")

    # (11) End-of-route time constraint
    for i in V_prime:
        if (i, 0) in E:
            model.addConstr(z[i, 0] <= Tmax * x[i, 0],
                            name=f"time_back_{i}_0")

    # (12) Initial travel time from depot
    for i in V_prime:
        if (0, i) in E:
            model.addConstr(z[0, i] == T_ij[0, i] * x[0, i],
                            name=f"time_start_0_{i}")

    # (13) Distance flow conservation
    for i in V_prime:
        model.addConstr(
            sum(z_prime[i, j] for j in V if (i, j) in E) -
            sum(z_prime[j, i] for j in V if (j, i) in E) ==
            sum(D_ij[i, j] * x[i, j] for j in V if (i, j) in E),
            name=f"distance_flow_{i}"
        )

    # (14) Max distance upper bound
    for i in V:
        for j in V_prime:
            if (i, j) in E:
                model.addConstr(z_prime[i, j] <= D_max * x[i, j],
                                name=f"dist_upper_{i}_{j}")

    # (15) Lower bound if arc is used
    for i in V_prime:
        for j in V:
            if (i, j) in E:
                model.addConstr(z_prime[i, j] >= D_ij[i, j] * x[i, j],
                                name=f"dist_lower_{i}_{j}")

    # (16) Final distance back to depot
    for i in V_prime:
        if (i, 0) in E:
            model.addConstr(z_prime[i, 0] <= D_max * x[i, 0],
                            name=f"dist_back_{i}_0")

    # (17) Initial distance from depot
    for i in V_prime:
        if (0, i) in E:
            model.addConstr(z_prime[0, i] == D_ij[0, i] * x[0, i],
                            name=f"dist_start_0_{i}")
