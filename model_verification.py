"""
Model Verification File

In this file, verification on the model is performed.
"""

from main import MILPModel

class ModelVerification():
    """
    Holds the methods for verifying the model
    """
    def __init__(self):
        filepath = "datasheet.xlsx"
        self.model = MILPModel()
        self.model.model_setup(filepath)
        self.model.setup_contraints()
    

    def run_model(self):
        self.model.optimize_model()
        self.model.analyze_results()


if __name__ == "__main__":
    model = ModelVerification()
    model.run_model()
