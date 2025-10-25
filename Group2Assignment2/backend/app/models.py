from pydantic import BaseModel
from typing import List, Optional


class Insight(BaseModel):
	diet_type: str
	protein_g: float
	carbs_g: float
	fat_g: float


class AvgInsight(BaseModel):
	diet_type: str
	avg_protein_g: float
	avg_carbs_g: float
	avg_fat_g: float


class Recipe(BaseModel):
	diet_type: str
	recipe_name: str
	cuisine_type: str
	protein_g: float
	carbs_g: float
	fat_g: float


class ClusterPoint(BaseModel):
	x: float
	y: float
	label: int


class TopProteinResponse(BaseModel):
	diet_type: str
	recipes: List[Recipe]


class AvgResponse(BaseModel):
	items: List[AvgInsight]


class ClusterResponse(BaseModel):
	points: List[ClusterPoint]