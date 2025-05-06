""" 
Main File

This file holds the main flow of the model. It initialises the variables 
for a scenario, sets the constraints, and optimizes following the structure
of the taxi scheduling report.

"""

from gurobipy import Model,GRB, quicksum
import pandas as pd


class MILPModel():
    """ 
    The model class for the taxi scheduling problem. 
    """
    def __init__(self):
        self.model = Model()

    def model_setup(self):
        """
        This function reads the datasheet from excel and sets up the parameters
        """
        file_path = "datasheet.xls"
        df_vertices = pd.read_excel(file_path, sheet_name = 'vertices')
        df_arcs = pd.read_excel(file_path, sheet_name = 'arcs')
        df_other = pd.read_excel(file_path, sheet_name = 'vertices')


if __name__ == "__main__":
    model = MILPModel()
    model.model_setup()