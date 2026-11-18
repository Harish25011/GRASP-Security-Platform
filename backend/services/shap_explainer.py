import torch
import numpy as np

class SHAPExplainer:
    """
    Explainable AI (XAI) Wrapper using SHAP to interpret the 30-dimensional
    Attention-MLP decisions in real-time.
    """
    def __init__(self, model: torch.nn.Module, background_data: torch.Tensor):
        # We delay import shap because it's heavy, but okay to import here 
        import shap
        self.model = model
        self.model.eval()
        
        # DeepExplainer is ideal for PyTorch DL models like our Attention-MLP
        self.explainer = shap.DeepExplainer(self.model, background_data)

    def explain(self, feature_vector: np.ndarray, agent_names: list) -> dict:
        """
        Calculates and maps exactly how much each feature contributed to the final score.
        Positive value -> Drove score towards Attack
        Negative value -> Drove score towards Benign/Normal
        """
        import shap
        
        # Ensure correct shape: (1, 30)
        if feature_vector.ndim == 1:
            feature_vector = feature_vector.reshape(1, -1)
            
        tensor_input = torch.FloatTensor(feature_vector)
        
        # Compute shap values
        shap_values = self.explainer.shap_values(tensor_input)
        
        # shap_values[0] because we are explaining a single sample
        vals = shap_values[0]
        
        return {
            name: float(val)
            for name, val in zip(agent_names, vals)
        }
