#!/usr/bin/env python

## 
 # -*-Pyth-*-
 # ###################################################################
 #  FiPy - Python-based finite volume PDE solver
 # 
 #  FILE: "mesh1D.py"
 #                                    created: 11/10/03 {2:44:42 PM} 
 #                                last update: 4/1/05 {5:39:10 PM} 
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
 #  See the file "license.terms" for information on usage and  redistribution
 #  of this file, and for a DISCLAIMER OF ALL WARRANTIES.
 #  
 # ###################################################################
 ##

"""Generic mesh class using Numeric to do the calculations

    Meshes contain cells, faces, and vertices.

    This is built for a non-mixed element mesh.
"""

import Numeric
import MA

from fipy.meshes.numMesh.mesh import Mesh
from fipy.tools import vector

class Mesh1D(Mesh):
    def _calcFaceAreas(self):
        self.faceAreas = Numeric.ones(self.numberOfFaces, 'd')

    def _calcFaceCenters(self):
        faceVertexIDs = MA.filled(self.faceVertexIDs, 0)
        faceVertexCoords = Numeric.take(self.vertexCoords, faceVertexIDs)
        if self.faceVertexIDs.mask() == None:
            faceVertexCoordsMask = Numeric.zeros(Numeric.shape(faceVertexCoords))
        else:
            faceVertexCoordsMask = Numeric.reshape(Numeric.repeat(self.faceVertexIDs.mask().flat, self.dim), Numeric.shape(faceVertexCoords))
            
        self.faceCenters = MA.array(data = faceVertexCoords, mask = faceVertexCoordsMask)
        
    def _calcFaceNormals(self):
        self.faceNormals = Numeric.transpose(Numeric.array((Numeric.ones(self.numberOfFaces, 'd'),)))
        # The left-most face has neighboring cells None and the left-most cell.
        # We must reverse the normal to make fluxes work correctly.
        self.faceNormals[0] = -self.faceNormals[0]

    def _calcFaceTangents(self):
        self.faceTangents1 = Numeric.zeros(self.numberOfFaces, 'd')[:, Numeric.NewAxis]
        self.faceTangents2 = Numeric.zeros(self.numberOfFaces, 'd')[:, Numeric.NewAxis]

    def _calcHigherOrderScalings(self):
	self.scale['area'] = 1.
	self.scale['volume'] = self.scale['length']

    def _translate(self, vector):
        newCoords = self.vertexCoords + vector
        newmesh = Mesh1D(newCoords, Numeric.array(self.faceVertexIDs), Numeric.array(self.cellFaceIDs))
        return newmesh

    def __mul__(self, factor):
        newCoords = self.vertexCoords * factor
        newmesh = Mesh1D(newCoords, Numeric.array(self.faceVertexIDs), Numeric.array(self.cellFaceIDs))
        return newmesh

    def _concatenate(self, other, smallNumber):
        return Mesh1D(**self._getAddedMeshValues(other, smallNumber))
