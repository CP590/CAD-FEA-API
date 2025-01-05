from pydantic import BaseModel
from typing import List, Dict


class BeamSelection(BaseModel):
    cross_section: str


class MaterialSelection(BaseModel):
    name: str
    youngs_modulus: float
    poisson_ratio: float


class STEPParameters(BaseModel):
    cross_section: str
    width: float
    depth: float
    length: float
