#!/usr/bin/env python

## -*-Pyth-*-
 # ###################################################################
 #  FiPy - Python-based finite volume PDE solver
 # 
 #  FILE: "levelSetDiffusionVariable.py"
 #                                    created: 9/8/04 {10:39:23 AM} 
 #                                last update: 4/7/05 {5:07:06 PM} 
 #  Author: Jonathan Guyer <guyer@nist.gov>
 #  Author: Daniel Wheeler <daniel.wheeler@nist.gov>
 #  Author: James Warren   <jwarren@nist.gov>
 #    mail: NIST
 #     www: http://www.ctcms.nist.gov/fipy/
 #  
 # ========================================================================
 # This software was developed at the National Institute of Standards
 # and Technology by employees of the Federal Government in the course
 # of their official duties.  Pursuant to title 17 Section 105 of the
 # United States Code this software is not subject to copyright
 # protection and is in the public domain.  PFM is an experimental
 # system.  NIST assumes no responsibility whatsoever for its use by
 # other parties, and makes no guarantees, expressed or implied, about
 # its quality, reliability, or any other characteristic.  We would
 # appreciate acknowledgement if the software is used.
 # 
 # This software can be redistributed and/or modified freely
 # provided that any derivative works bear some notice that they are
 # derived from it, and any modified versions bear some notice that
 # they have been modified.
 # ========================================================================
 #  
 #  Description: 
 # 
 #  History
 # 
 #  modified   by  rev reason
 #  ---------- --- --- -----------
 #  2003-11-12 JEG 1.0 original
 # ###################################################################
 ##

__docformat__ = 'restructuredtext'

import Numeric

from fipy.variables.cellToFaceVariable import _CellToFaceVariable
from fipy.tools.inline import inline

class _LevelSetDiffusionVariable(_CellToFaceVariable):
    """

    This variable sets it's face value to zero if either of the
    surrounding cell values are zero else it uses the value of the
    diffusion coefficient. The diffusion coefficient is given by,

    .. raw:: latex

        $$ D = D_c \\;\\; \\text{when} \\;\\; \\phi > 0 $$
        $$ D = 0   \\;\\; \\text{when} \\;\\; \\phi \\le 0 $$

    Here is a simple 1D test case:

       >>> from fipy.meshes.grid2D import Grid2D
       >>> mesh = Grid2D(dx = 1., nx = 3)
       >>> from fipy.variables.cellVariable import CellVariable
       >>> var = CellVariable(mesh = mesh, value = (-1, 1, 1))
       >>> arr = Numeric.array(_LevelSetDiffusionVariable(var, 1))
       >>> Numeric.allclose(arr, (0,1,1,0,1,1,0,0,1,1))
       1

    """
    def __init__(self, distanceVariable = None, diffusionCoeff = None):
        """
        Creates a `_LevelSetDiffusionVariable`.

        :Parameters:
          - `distanceVariable` : A `DistanceVariable` object
          - `diffusionCoeff` : The `coeff` value.

        """
        _CellToFaceVariable.__init__(self, distanceVariable)
        self.diffusionCoeff = diffusionCoeff
    
    def _calcValuePy(self, alpha, id1, id2):
        distance = Numeric.array(self.var)
        cell1 = Numeric.take(distance, id1)
        cell2 = Numeric.take(distance, id2)

        self.value = Numeric.where(cell1 < 0 or cell2 < 0,
                                   0,
                                   self.diffusionCoeff)
                                   
    def _calcValueIn(self, alpha, id1, id2):
        inline._runInlineLoop1("""
	    double	cell1 = var(id1(i));
	    double	cell2 = var(id2(i));

	    if (cell1 < 0 || cell2 < 0) {
		val(i) = 0;
	    } else {
		val(i) = diffusionCoeff;
	    }
	""",
	var = Numeric.array(self.var),
	val = self._getArray(), 
	id1 = id1, id2 = id2,
        diffusionCoeff = self.diffusionCoeff,
	ni = len(self.mesh.getFaces())
	)

def _test(): 
    import doctest
    return doctest.testmod()
    
if __name__ == "__main__": 
    _test() 
