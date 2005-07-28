#!/usr/bin/env python

## 
 # -*-Pyth-*-
 # ###################################################################
 #  FiPy - Python-based finite volume PDE solver
 # 
 #  FILE: "adaptiveMesh.py"
 #                                    created: 11/10/03 {2:44:42 PM} 
 #                                last update: 6/7/05 {4:26:43 PM} 
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

__docformat__ = 'restructuredtext'

import Numeric

from fipy.meshes.numMesh.gmshImport import GmshImporter2D

def _removeDuplicates(list):
    dict = {}
    for item in list:
        dict[item] = None
    return dict.keys()

def _orderVertices(vertexCoords, vertices):
    coordinates = Numeric.take(vertexCoords, vertices)
    centroid = Numeric.add.reduce(coordinates) / coordinates.shape[0]
    coordinates = coordinates - centroid
    coordinates = Numeric.where(coordinates == 0, 1.e-100, coordinates) ## to prevent division by zero
    angles = Numeric.arctan(coordinates[:, 1] / coordinates[:, 0]) + Numeric.where(coordinates[:, 0] < 0, Numeric.pi, 0) ## angles go from -pi / 2 to 3*pi / 2
    sortorder = Numeric.argsort(angles)
    return Numeric.take(vertices, sortorder)

def _bracedList(l):
    return "{%s}" % ', '.join([str(i) for i in l])

def _parenList(l):
    return "(%s)" % ', '.join([str(i) for i in l])
       
class AdaptiveMesh2D(GmshImporter2D):
    """

    The `AdaptiveMesh` classes allow meshes to be created "on-the-fly" using a
    variable specified by the user.  The `AdaptiveMesh` classes use Gmsh, a free
    open-source meshing utility (http://www.geuz.org/gmsh). To do this, pass in a
    variable to the initializer function that has a mesh with the same
    boundaries (though not necessarily the same interior geometry) as the mesh
    you want to create and values that are equal to the approximate mesh sizes
    you want at any given point.  For example, if you want the mesh to be finer
    in areas where a concentration gradient is steeper, create a variable whose
    value is equal to some constant times the reciprocal of the concentration
    gradient and pass it to the initializer.  The following will create a mesh
    that is finer toward the upper right hand corner:

       >>> from fipy.meshes.numMesh.tri2D import Tri2D
       >>> baseMesh = Tri2D(nx = 2, ny = 2, dx = 1.0, dy = 1.0)
       
       >>> from fipy.variables.cellVariable import CellVariable
       >>> var = CellVariable(mesh = baseMesh, 
       ...     value = 0.05 - (0.01 * Numeric.add.reduce(baseMesh.getCellCenters(), 
       ...                                               axis = 1)), 
       ...     name = "characteristic lengths")

    Since the value of `var` is smaller in the upper right hand corner, the mesh
    will be finer there.  To create the mesh, do this:

       >>> newMesh = AdaptiveMesh2D(var)

    .. note:: 
        
       At present, AdaptiveMesh supports triangular meshes only.

    """
    
    def __init__(self, variable):
        self.variable = variable
        self._calcExteriorVertexIDs()
        self._calcGeometryPoints()
        self._calcExteriorLines()
        geomFile = self._writeGeometryFile()
        self._createBackgroundMesh()
        bgMesh = self._writeBackgroundMesh()
        
        
        import os
        import tempfile
        import sys
        if sys.platform == 'win32':
            meshFile = 'tmp.msh'
        else:
            (f, meshFile) = tempfile.mkstemp('.msh')
        os.system("gmsh -v 0 %s -bgm %s -format msh -2 -o %s" % (geomFile, bgMesh, meshFile))
        
        GmshImporter2D.__init__(self, meshFile)
        if sys.platform != 'win32':
            os.close(f)
        os.remove(geomFile)
        os.remove(bgMesh)
        os.remove(meshFile)

    def _calcExteriorVertexIDs(self):
        ## get the exterior vertex IDs
        self.varMesh = self.variable.getMesh()
        exteriorFaces = self.varMesh.getExteriorFaceIDs()
        exteriorFaceVertexIDs = Numeric.take(self.varMesh.faceVertexIDs, exteriorFaces)
        exteriorVertexIDs = Numeric.ravel(exteriorFaceVertexIDs)
        exteriorVertexIDs = _removeDuplicates(exteriorVertexIDs)
        ## sort the exterior vertex IDs going counterclockwise
        exteriorVertexIDs = _orderVertices(self.varMesh.getVertexCoords(), exteriorVertexIDs)
        self.exteriorVertexIDs = exteriorVertexIDs

    def _calcGeometryPoints(self):
        ## get the points to put in the geometry file
        geometryPoints = Numeric.zeros((len(self.varMesh.getVertexCoords()), 4)).astype(Numeric.Float)
        geometryPoints[:, :2] = self.varMesh.getVertexCoords()
        geometryPoints[:, 2] = 0
        geometryPoints[:, 3] = 1
        geometryPoints = Numeric.take(geometryPoints, self.exteriorVertexIDs)
        self.geometryPoints = geometryPoints

    def _calcExteriorLines(self):
        ## get the exterior lines to put in the geometry file
        exteriorLines = Numeric.zeros((len(self.exteriorVertexIDs), 2))
        exteriorLines[:, 0] = Numeric.arange(len(self.exteriorVertexIDs))
        exteriorLines[:-1, 1] = Numeric.arange(1, len(self.exteriorVertexIDs))
        exteriorLines[-1, 1] = 0
        exteriorLines = exteriorLines + 1
        ## get the line loop to put in the geometry file
        lineLoop = Numeric.arange(len(self.exteriorVertexIDs))
        lineLoop = lineLoop + 1
        self.exteriorLines = exteriorLines
        self.lineLoop = lineLoop

    def _writeGeometryFile(self):
        ## do the geometry file
        import tempfile
	(f, filename) = tempfile.mkstemp('.geo')
	
        geomFile = open(filename, mode = 'w')
        ## create the points
        pointList = ["Point(" + str(i + 1) + ") = " + _bracedList(self.geometryPoints[i]) + " ; \n" for i in range(len(self.geometryPoints))]
        for i in pointList:
            geomFile.write(i)
        index = 1
        ## create the lines
        for j in self.exteriorLines:
            geomFile.write("Line(" + str(index) + ") = " + _bracedList(j) + " ; \n")
            index = index + 1
        ## create the line-loop
        geomFile.write("Line Loop(" + str(index) + ") = " + _bracedList(self.lineLoop) + " ; \n")
        LLindex = index
        index = index + 1
        ## create the plane surface
        geomFile.write("Plane Surface(" + str(index) + ") = {" + str(LLindex) + "} ; \n")
        index = index + 1
        ## close the file
        geomFile.close()
	
	return filename
    
    def _createBackgroundMesh(self):
        ## create the background mesh (this works for Triangular Meshes ONLY)
        cellFaceVertexIDs = Numeric.take(self.varMesh.faceVertexIDs, self.varMesh.cellFaceIDs)
        cellVertexIDs = Numeric.reshape(cellFaceVertexIDs, (len(self.varMesh.getCellCenters()), 6))
        cellVertexIDs = Numeric.sort(cellVertexIDs)
        cellVertexIDs = cellVertexIDs[:, ::2]
        fullVertexCoords = Numeric.zeros((len(self.varMesh.getVertexCoords()), 3)).astype(Numeric.Float)
        fullVertexCoords[:, :2] = self.varMesh.getVertexCoords()
        cellVertexCoords = Numeric.take(fullVertexCoords, cellVertexIDs)
        cellOutputs = Numeric.reshape(cellVertexCoords, (len(self.varMesh.getCellCenters()), 9))
        vertexValues = self.variable.getValue(points = self.varMesh.getVertexCoords())
        cellVertexValues = Numeric.take(vertexValues, cellVertexIDs)
        self.cellOutputs = cellOutputs
        self.cellVertexValues = cellVertexValues

    def _writeBackgroundMesh(self):
        ## write the mesh
        import tempfile
	(f, bgFile) = tempfile.mkstemp('.pos')
	
        bgmeshFile = open(bgFile, mode = 'w')
        bgmeshFile.write("View \"characteristic lengths\" {")
        for i in range(len(self.varMesh.getCellCenters())):
            bgmeshFile.write("ST" + _parenList(self.cellOutputs[i]) + _bracedList(self.cellVertexValues[i]) + ";\n")
        bgmeshFile.write("};")
        bgmeshFile.close()
	
	return bgFile

def _test():
    import doctest
    return doctest.testmod()

if __name__ == "__main__":
    _test()

