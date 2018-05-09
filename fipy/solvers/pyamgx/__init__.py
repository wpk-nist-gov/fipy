import atexit

import pyamgx

from fipy.solvers.pyamgx.pyAMGXSolver import *
from fipy.solvers.pyamgx.linearPCGSolver import *
from fipy.solvers.pyamgx.linearGMRESSolver import *
from fipy.solvers.pyamgx.linearLUSolver import *
from fipy.solvers.pyamgx.aggregationAMGSolver import *
from fipy.solvers.pyamgx.classicalAMGSolver import *

pyamgx.initialize()
atexit.register(pyamgx.finalize)

DefaultSolver = linearPCGSolver
DefaultAsymmetricSolver = linearGMRESolver
DummySolver = linearGMRESolver
GeneralSolver = linearGMRESolver

__all__ = ["DefaultSolver",
           "DummySolver",
           "DefaultAsymmetricSolver",
           "GeneralSolver"
          ]

__all__.extend(linearPCGSolver.__all__)
__all__.extend(linearGMRESSolver.__all__)
__all__.extend(linearLUSolver.__all__)
__all__.extend(aggregationAMGSolver.__all__)
