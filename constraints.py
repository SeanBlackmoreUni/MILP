"""
File for constraints
"""

"""
File for constraints
"""
def add_constraints(self, model):
    vertices = self.data["vertices"]
    arcs = self.data["arcs"]
    D_max = self.data["other"]["D_max"]
    Q = self.data["other"]["Q"]
    Tmax = self.data["other"]["Tmax"]

    V = [v["id"] for v in vertices]
    V_prime = [v["id"] for v in vertices if v["id"] != 0]
    E = [(a["from"], a["to"]) for a in arcs]

    # Build lookup dictionaries
    N_i = {v["id"]: v["Ni"] for v in vertices}
    S_i = {v["id"]: v["Si"] for v in vertices}
    T_ij = {(a["from"], a["to"]): a["Time"] for a in arcs}
    D_ij = {(a["from"], a["to"]): a["distance"] for a in arcs}

    x = self.variables["x"]
    y = self.variables["y"]
    z = self.variables["z"]
    z_prime = self.variables["z_prime"]
    k = self.variables["k"]

    # --- Constraints ---

    # (2) Each customer has exactly one incoming arc
    for j in V_prime:
        model.addConstr(sum(x[i, j] for i in V if (i, j) in E) == 1)

    # (3) Each customer has exactly one outgoing arc
    for i in V_prime:
        model.addConstr(sum(x[i, j] for j in V if (i, j) in E) == 1)

    # (4) Vehicles leave depot k times
    model.addConstr(sum(x[0, i] for i in V_prime if (0, i) in E) == k)

    # (5) Vehicles return to depot k times
    model.addConstr(sum(x[i, 0] for i in V_prime if (i, 0) in E) == k)

    # (6) Package capacity constraint
    for i, j in E:
        model.addConstr(y[i, j] <= Q * x[i, j])

    # (7) Flow conservation for packages
    for i in V_prime:
        model.addConstr(
            sum(y[i, j] for j in V if (i, j) in E) - 
            sum(y[j, i] for j in V if (j, i) in E) == N_i[i]
        )

    # (8) Travel time flow conservation
    for i in V_prime:
        model.addConstr(
            sum(z[i, j] for j in V if (i, j) in E) - 
            sum(z[j, i] for j in V if (j, i) in E) == 
            sum((T_ij[i, j] + S_i[i]) * x[i, j] for j in V if (i, j) in E)
        )

    # (9) Total travel time upper bound
    for i in V:
        for j in V_prime:
            if (i, j) in E:
                model.addConstr(z[i, j] <= Tmax * x[i, j])

    # (10) Lower bound on travel time if arc is used
    for i in V_prime:
        for j in V:
            if (i, j) in E:
                model.addConstr(z[i, j] >= (T_ij[i, j] + S_i[i]) * x[i, j])

    # (11) End-of-route time constraint
    for i in V_prime:
        if (i, 0) in E:
            model.addConstr(z[i, 0] <= Tmax * x[i, 0])

    # (12) Initial travel time from depot
    for i in V_prime:
        if (0, i) in E:
            model.addConstr(z[0, i] == T_ij[0, i] * x[0, i])

    # BEV Range Constraints

    # (13) Distance flow conservation
    for i in V_prime:
        model.addConstr(
            sum(z_prime[i, j] for j in V if (i, j) in E) -
            sum(z_prime[j, i] for j in V if (j, i) in E) ==
            sum(D_ij[i, j] * x[i, j] for j in V if (i, j) in E)
        )

    # (14) Max distance upper bound
    for i in V:
        for j in V_prime:
            if (i, j) in E:
                model.addConstr(z_prime[i, j] <= D_max * x[i, j])

    # (15) Lower bound if arc is used
    for i in V_prime:
        for j in V:
            if (i, j) in E:
                model.addConstr(z_prime[i, j] >= D_ij[i, j] * x[i, j])

    # (16) Final distance back to depot
    for i in V_prime:
        if (i, 0) in E:
            model.addConstr(z_prime[i, 0] <= D_max * x[i, 0])

    # (17) Initial distance from depot
    for i in V_prime:
        if (0, i) in E:
            model.addConstr(z_prime[0, i] == D_ij[0, i] * x[0, i])

            hoi