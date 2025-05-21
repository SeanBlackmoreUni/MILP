"""
Sensitivity Analysis File

This file performs a sensitivity analysis
"""

from main import MILPModel
from gurobipy import GRB
import pandas as pd

class SensitivityAnalysis():
    """
    Class that performs the sensitivity analysis.
    """
    def __init__(self):
        self.filepath = "datasheet_kopie.xlsx"
        self.ranges = {
            'Q': [50, 100],
            'T_bar': [],
            'D_bar': [],
            'S_i': []
        }


    def optimize_models(self, parameter_choice: str):
        """
        Optimizes the model for each parameter specified in the range.
        Saves the result to a csv file
        """
        # Set file path
        filepath = f"sensitivity_results/{parameter_choice}_sens.csv"

        # Set up data frame
        columns = [parameter_choice, 'obj_val', 'VMT', 'VHT', 'k', 'routes']
        result_df = pd.DataFrame(columns=columns)
        
        # Loop to optimize the model for all the values in the range
        for value in self.ranges[parameter_choice]:
            # print(f"Bbbbbbbb: {value}")
            self.model = MILPModel()                                        # Initialise and set up model
            self.model.model_setup(self.filepath)
            self.model.data['other'][parameter_choice] = value              # Override the value
            # print(f"NEW VALUE: {self.model.data['other'][parameter_choice]}")
            self.model.setup_contraints()
            self.model.optimize_model()             # Optimize

            if self.model.status == 1:
                obj_val, k, VMT, VHT, routes = self.model.analyze_results()
                print(f"!!!!!!!    For {parameter_choice} = {value}: k= {k}, VMT= {VMT}, VHT= {VHT}")

                result_df.loc[len(result_df)] = [value, obj_val, VMT, VHT, k, '']
            else:
                print("Model Infeasible!")
            
            print('')
            print('#######################################################################################')
            print('')

            # Export the dataframe to a csv to store results
            result_df.to_csv(filepath, index=False)



    def build_csv(self, param: str):
        """
        Builds the csv file with the results 
        """
        


if __name__ == '__main__':
    sens_analysis = SensitivityAnalysis()
    parameter_choice = 'Q'    # 1: Q, 2: T, 3: D, 4: S    # 'Q', 'T_bar', 'D_bar', 'S_i'
    sens_analysis.optimize_models(parameter_choice)              
