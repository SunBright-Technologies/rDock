from dataclasses import dataclass, field

import numpy
from openbabel import pybel

Coordinate = tuple[float, float, float]
FloatArray = numpy.ndarray[(float, 1), float]
SingularValueDecomposition = tuple[FloatArray, FloatArray, FloatArray]
AutomorphismRMSD = tuple[float, FloatArray | None]
BoolArray = numpy.ndarray[bool]
CoordsArray = numpy.ndarray[(float, 3), float]
Superpose3DResult = tuple[FloatArray, float, FloatArray | None]


@dataclass
class SDRMSDData:
    skipped: list[int] = field(default_factory=list)
    molecules_dict: dict[int, pybel.Molecule] = field(default_factory=dict)  # Save all poses with their dockid
    population: dict[int, int] = field(default_factory=dict)  # Poses to be written
    out_dict: dict[int, tuple[pybel.Molecule, AutomorphismRMSD]] = field(default_factory=dict)


@dataclass
class PoseMatchData:
    pose_index: int
    docked_pose: pybel.Molecule
    sdrmsd_data: SDRMSDData
