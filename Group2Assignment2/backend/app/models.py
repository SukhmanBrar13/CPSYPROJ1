from pydantic import BaseModel
from typing import List, Optional

# -------------------------------------------------------------
# Core data models used for API responses and validation
# -------------------------------------------------------------

class Insight(BaseModel):
    """
    Represents a single recipe's macronutrient information.
    (Used for general analysis or extensions)
    """
    diet_type: str
    protein_g: float
    carbs_g: float
    fat_g: float


class AvgInsight(BaseModel):
    """
    Represents the average macronutrient values (Protein, Carbs, Fat)
    for a specific diet type.
    """
    diet_type: str
    avg_protein_g: float
    avg_carbs_g: float
    avg_fat_g: float


class Recipe(BaseModel):
    """
    Represents an individual recipe record with its diet type,
    cuisine type, and macronutrient breakdown.
    """
    diet_type: str
    recipe_name: str
    cuisine_type: str
    protein_g: float
    carbs_g: float
    fat_g: float


class ClusterPoint(BaseModel):
    """
    Represents a single data point used for K-Means clustering,
    including its (x, y) position and assigned cluster label.
    """
    x: float
    y: float
    label: int


# -------------------------------------------------------------
# Response wrapper models for specific API endpoints
# -------------------------------------------------------------

class TopProteinResponse(BaseModel):
    """
    Response model for the /recipes/top_protein endpoint.
    Returns the top protein-rich recipes for a selected diet type.
    """
    diet_type: str
    recipes: List[Recipe]


class AvgResponse(BaseModel):
    """
    Response model for the /insights/avg endpoint.
    Contains a list of average macronutrient insights by diet.
    """
    items: List[AvgInsight]


class ClusterResponse(BaseModel):
    """
    Response model for the /clusters endpoint.
    Contains the clustered data points with their labels.
    """
    points: List[ClusterPoint]