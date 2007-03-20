#!/usr/bin/env python

## -*-Pyth-*-
 # ###################################################################
 #  FiPy - Python-based finite volume PDE solver
 # 
 #  FILE: "transientVariable.py"
 #                                    created: 11/12/03 {10:39:23 AM} 
 #                                last update: 9/3/04 {10:40:01 PM}
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

import Numeric
from fipy.tools.inline import inline

from fipy.variables.cellVariable import CellVariable

class TransientVariable(CellVariable):

    def __init__(self, phase = None, theta = None, parameters = None):

        CellVariable.__init__(self, phase.getMesh(), hasOld = 0)

        self.parameters = parameters
        self.phase = self.requires(phase)
        self.theta = self.requires(theta)

    def _calcValue(self):
        inline.optionalInline(self._calcValueInline, self._calcValuePy)

    def _calcValuePy(self):

        smallValue = self.parameters['small value']
        epsilon = self.parameters['epsilon']

        phaseMod = self.phase[:] + ( self.phase[:] < smallValue ) * smallValue
        phaseSq = phaseMod * phaseMod
        expo = epsilon * self.parameters['beta'] * self.theta.getGrad().getMag()[:]
        expo = (expo < 100.) * (expo - 100.) + 100.
        pFunc = 1. + Numeric.exp(-expo) * (self.parameters['mu'] / epsilon - 1.)

        
        self.value = self.parameters['tau'] * phaseSq * pFunc

    def _calcValueInline(self):
        
        inline.runInlineLoop1("""
        phaseMod = phase(i);
        if(phaseMod < smallValue)
          phaseMod += smallValue;
        phaseSq = phaseMod * phaseMod;

        expo = epsilon * beta * thetaGradMag(i);
        pFunc = 1. + exp(-expo) * (mu / epsilon - 1.);
        value(i) = tau * phaseSq * pFunc;""",
                              phaseMod = 0.,
                              phase = self.phase.getNumericValue(),
                              smallValue = self.parameters['small value'],
                              phaseSq = 0.,
                              expo = 0.,
                              epsilon = self.parameters['epsilon'],
                              beta = self.parameters['beta'],
                              thetaGradMag = self.theta.getGrad().getMag().getNumericValue(),
                              pFunc = 0.,
                              mu = self.parameters['mu'],
                              tau = self.parameters['tau'],
                              value = self._getArray(),
                              ni = len(self.phase.getNumericValue())
                              )
                              
        
        
          
        