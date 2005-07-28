#!/usr/bin/env python

## -*-Pyth-*-
 # ###################################################################
 #  FiPy - Python-based finite volume PDE solver
 # 
 #  FILE: "mPhiVariable.py"
 #                                    created: 12/24/03 {10:39:23 AM} 
 #                                last update: 7/6/05 {3:57:36 PM} 
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
 # protection and is in the public domain.  FiPy is an experimental
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

from fipy.variables.cellVariable import CellVariable

class MPhiVariable(CellVariable):
    """
    .. attention:: This class is abstract. Always create one of its subclasses.
    """
    def __init__(self, phase = None, temperature = None, parameters = None):
        """
        Base class for `MPhiVariable` objects

        :Parameters:
          - `phase` : The phase field.
          - `temperature` : The temperature.
          - `parameters` : A dictionary with keys `'kappa1'` and `'kappa2'`.

        """    
        CellVariable.__init__(self, mesh = phase.getMesh())
        if type(temperature) is (type(0.) or type(0)):
            self.temperature = (temperature,)
        else:
            self.temperature = self._requires(temperature)
        self.phase = self._requires(phase)
        self.parameters = parameters


        
