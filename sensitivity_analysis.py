"""
Sensitivity Analysis File

This file performs a sensitivity analysis
"""

from main import MILPModel
from gurobipy import GRB
import pandas as pd
import numpy as np

class SensitivityAnalysis():
    """
    Class that performs the sensitivity analysis.
    """
    def __init__(self):
        self.filepath = "datasheet_kopie.xlsx"
        self.ranges = {
            'Q': np.arange(0, 40, 5),
            'T_bar': np.arange(50, 200, 10),
            'D_bar': np.arange(0, 40, 5),
            'S_i': np.arange(0, 50, 5)
        }


    def optimize_models(self, parameter_choice: str):
        """
        Optimizes the model for each parameter specified in the range.
        Saves the result to a csv file
        """
        # Set file path
        filepath = f"sensitivity_results/{parameter_choice}_sens.csv"

        # Set up data frame
        columns = [parameter_choice, 'obj_val', 'VMT', 'VTT', 'k', 'routes']
        result_df = pd.DataFrame(columns=columns)
        
        # Loop to optimize the model for all the values in the range
        for value in self.ranges[parameter_choice]:
            # print(f"Bbbbbbbb: {value}")

            self.model = MILPModel()                                            # Initialise and set up model
            self.model.model_setup(self.filepath)
            if parameter_choice == 'S_i':
                for vertex in self.model.data['vertices'].values():
                    vertex['S_i'] = value
            else: 
                self.model.data['other'][parameter_choice] = value              # Override the value

            # print(f"NEW VALUE: {self.model.data['other'][parameter_choice]}")

            self.model.setup_contraints()
            self.model.optimize_model()             # Optimize

            if self.model.status == 1:
                obj_val, k, VMT, VTT, routes = self.model.analyze_results()
                print(f"!!!!!!!    For {parameter_choice} = {value}: k= {k}, VMT= {VMT}, VTT= {VTT}")
                result_df.loc[len(result_df)] = [value, obj_val, VMT, VTT, k, '']
            else:
                print("Model Infeasible!")
                result_df.loc[len(result_df)] = [value, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA]

            print('')
            print('#######################################################################################')
            print('')

        # Export the dataframe to a csv to store results
        result_df.to_csv(filepath, index=False)


    def cross_vary_models(self, parameter1, parameter2):
        """
        Allows for a choice of two parameters to cross vary.
        You cannot choose S_i in this method.
        """
        # First order the two variables s.t. there are no ambiguous csv files
        param1, param2 = sorted([parameter1, parameter2])

        # Set file path
        filepath = f"sensitivity_results/cv_{param1}_{param2}_sens.csv"

        # Set up data frame
        columns = [param1, param2, 'obj_val', 'VMT', 'VTT', 'k', 'routes']
        result_df = pd.DataFrame(columns=columns)

        # Loop to optimize the model for all the values in the range
        for value1 in self.ranges[param1]:
            for value2 in self.ranges[param2]:
                # print(f"Bbbbbbbb: {value}")

                self.model = MILPModel()                                        # Initialise and set up model
                self.model.model_setup(self.filepath)
                if param1 == 'S_i' or param2 == 'S_i':
                    raise ValueError("You cannot choose S_i")
                
                self.model.data['other'][param1] = value1              # Override the value for param1
                self.model.data['other'][param2] = value2              # Override the value for param2

                # print(f"NEW VALUE: {self.model.data['other'][parameter_choice]}")

                self.model.setup_contraints()
                self.model.optimize_model()             # Optimize

                if self.model.status == 1:
                    obj_val, k, VMT, VTT, routes = self.model.analyze_results()
                    print(f"!!!!!!!    For {param1, param2} = {value1, value2}: k= {k}, VMT= {VMT}, VTT= {VTT}")
                    result_df.loc[len(result_df)] = [value1, value2, obj_val, VMT, VTT, k, '']
                else:
                    print("Model Infeasible!")
                    result_df.loc[len(result_df)] = [value1, value2, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA]

                print('')
                print('#######################################################################################')
                print('')

        # Export the dataframe to a csv to store results
        result_df.to_csv(filepath, index=False)



if __name__ == '__main__':
    sens_analysis = SensitivityAnalysis()

    # The code for the bar charts
    parameter_choice = ['Q', 'T_bar', 'D_bar', 'S_i']
    for param in parameter_choice:   
        sens_analysis.optimize_models(param)      

    # The code for the contour plots 
    parameter1 = ['D_bar', 'T_bar']       # 'Q', 'T_bar', 'D_bar', 
    parameter2 = 'Q'           # 'Q', 'T_bar', 'D_bar', 'S_i'

    for param1 in parameter1:    
        sens_analysis.cross_vary_models(param1, parameter2)
