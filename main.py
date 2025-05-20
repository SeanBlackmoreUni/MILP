""" 
Main File

This file holds the main flow of the model. It initialises the variables 
for a scenario, sets the constraints, and optimizes following the structure
of the article.

"""

from gurobipy import Model,GRB, quicksum
from constraints import add_constraints
import pandas as pd


class MILPModel():
    """ 
    The model class for the taxi scheduling problem. 
    """
    def __init__(self):
        self.model = Model()

    def model_setup(self, file_path):
        """
        This function reads the datasheet from excel and sets up the parameters
        """
        df_vertices = pd.read_excel(file_path, sheet_name = 'NL_vertices', engine='openpyxl')
        df_arcs = pd.read_excel(file_path, sheet_name = 'NL_arcs')
        df_other = pd.read_excel(file_path, sheet_name = 'Other')

        # Set up the data dictionary
        self.data = {
            'vertices': [],
            'vertices_prime': [],
            'arcs': [],
            'other': {},
        }

        # Fill the vertex values
        self.data['vertices'] = {
            row['Vertex']: {'N_i': row['N_i'], 'S_i': row['S_i']}
            for _, row in df_vertices.iterrows()
        }

        # Fill vertex_prime (excluding the depot)
        self.data['vertices_prime'] = {
            row['Vertex']: {'N_i': row['N_i'], 'S_i': row['S_i']}
            for _, row in df_vertices.iterrows()
            if row['Vertex'] != 0
        }

        # Fill the arc values
        self.data['arcs'] = {
            (row['From'], row['To']): {'distance': row['D_ij'], 'time': row['T_ij']}
            for _, row in df_arcs.iterrows()
        }

        # Fill other parameters
        self.data['other'] = {
            'Q': df_other.loc[0, 'Q'],
            'D_bar': df_other.loc[0, 'D_bar'],
            'T_bar': df_other.loc[0, 'T_bar']
        }

        # Set up the decision variables
        self.variables = {
            'x': {},        # binary arc usage
            'y': {},        # package flow
            'z': {},        # travel time
            'z_prime': {},  # travel distance (for BEV range)
        }

        # Create decision variables
        for (i, j) in self.data['arcs']:
            # Binary variable: x[i,j] = 1 if arc (i,j) is used
            # print(f'##############{i, j}')
            self.variables['x'][i, j] = self.model.addVar(
                vtype=GRB.BINARY,
                name=f"x_{i}_{j}"
            )

            # Continuous: y[i,j] = number of packages on arc (i,j)
            self.variables['y'][i, j] = self.model.addVar(
                vtype=GRB.INTEGER,
                lb=0,
                name=f"y_{i}_{j}"
            )

            # Continuous: z[i,j] = cumulative travel time from depot to j via i
            self.variables['z'][i, j] = self.model.addVar(
                vtype=GRB.INTEGER,
                lb=0,
                name=f"z_{i}_{j}"
            )

            # Continuous: z_prime[i,j] = cumulative travel distance from depot to j via i
            self.variables['z_prime'][i, j] = self.model.addVar(
                vtype=GRB.INTEGER,
                lb=0,
                name=f"zprime_{i}_{j}"
            )
        
        # Add k
        self.variables['k'] = self.model.addVar(vtype=GRB.INTEGER, lb=0, name="k")

        # Update Model
        self.model.update()

        # Objective: Minimize total distance traveled
        self.model.setObjective(
            quicksum(
                self.data['arcs'][(i, j)]['distance'] * self.variables['x'][i, j]
                for (i, j) in self.data['arcs']
            ),
            GRB.MINIMIZE
        )


    def setup_contraints(self):
        """
        Add the constraints to the model
        """
        add_constraints(self.model, self.data, self.variables)


    def optimize_model(self):
        """
        Optimize the model
        """
        self.model.optimize()

        if self.model.Status == GRB.OPTIMAL:
            print("Optimization was successful!")
            self.analyze_results()
            self.model.write("solution.sol")
            print("Solution written to solution.sol")
        elif self.model.Status == GRB.INFEASIBLE:
            print("Model is infeasible")
            self.model.computeIIS()  # Compute the Irreducible Inconsistent Subsystem
            self.model.write("infeasible_model.ilp")  # Write the IIS to a file for debugging
            print("IIS written to infeasible_model.ilp")
        elif self.model.Status == GRB.UNBOUNDED:
            print("Model is unbounded.")
        else:
            print(f"Optimization ended with status {self.model.Status}")

    
    def analyze_results(self):
        """
        Method to print the results of the optimized model.
        """   
        # Compute the Vehicle Miles Traveled (VMT)
        VMT = 0
        for (i, j) in self.data['arcs']:
            VMT += self.variables['z_prime'][i, j]

        # Compute Vehicle Hours Traveled (VHT)
        VHT = 0
        for (i, j), var in self.variables['x'].items():
            if var.X > 0.5:
                T_ij = self.data['arcs'][(i, j)]['time']
                S_i = self.data['vertices'][i]['S_i'] if i != 0 else 0
                VHT += T_ij + S_i

        # Compute Vehicle Miles Traveled (VMT)
        VMT = 0
        for (i, j), var in self.variables['x'].items():
            if var.X > 0.5:
                D_ij = self.data['arcs'][(i, j)]['distance']
                VMT += D_ij

        # Find the routes per vehicle
        # Step 1: extract active arcs
        arcs_used = {(i, j) for (i, j), var in self.variables['x'].items() if var.X > 0.5}

        # Step 2: find starting nodes from depot
        starts = [j for (i, j) in arcs_used if i == 0]

        routes = {}
        route_id = 1

        for start in starts:
            route = [0, start]
            current = start
            while current != 0:
                next_node = next((j for (i, j) in arcs_used if i == current), 0)
                if next_node == 0:
                    route.append(0)
                    break
                route.append(next_node)
                current = next_node
            routes[route_id] = route
            route_id += 1

        # Print the results
        print(f"####   The model finished with objective value: {self.model.ObjVal}")
        print(f"####   The amount of vehicles used: {self.variables['k']}")
        print(f"####   VMT: {VMT}")
        print(f"####   VHT: {VHT}")

        # Print the routes
        for key, value in routes.items():
            print(f"####   Route {key}: {value}")


if __name__ == "__main__":
    file_path = 'datasheet.xlsx'

    model = MILPModel()
    model.model_setup(file_path)
    model.setup_contraints()
    model.optimize_model()
