#!/usr/bin/env python

## -*-Pyth-*-
 # ###################################################################
 #  FiPy - Python-based finite volume PDE solver
 # 
 #  FILE: "uniformGrid1D.py"
 #                                    created: 2/28/06 {2:30:24 PM} 
 #                                last update: 3/5/06 {4:54:47 PM} 
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
 #  2006-02-28 JEG 1.0 original
 # ###################################################################
 ##

"""
2D rectangular Mesh with constant spacing in x and constant spacing in y
"""
__docformat__ = 'restructuredtext'


import MA

from fipy.meshes.numMesh.grid2D import Grid2D
from fipy.meshes.meshIterator import FaceIterator
from fipy.tools import numerix
from fipy.tools.dimensions.physicalField import PhysicalField

class UniformGrid2D(Grid2D):
    """
    Creates a 2D grid mesh with horizontal faces numbered
    first and then vertical faces.
    """
    def __init__(self, dx = 1., dy = 1., nx = 1, ny = 1, origin = (0,0)):
        self.dim = 2
        
	self.dx = PhysicalField(value = dx)
	scale = PhysicalField(value = 1, unit = self.dx.getUnit())
	self.dx /= scale
        
        self.nx = nx
        
	self.dy = PhysicalField(value = dy)
	if self.dy.getUnit().isDimensionless():
	    self.dy = dy
	else:
	    self.dy /= scale
            
        self.ny = ny
        
        self.origin = PhysicalField(value = origin)
        self.origin /= scale

        self.numberOfVertices = (self.nx + 1) * (self.ny + 1)
        self.numberOfHorizontalFaces = self.nx * (self.ny + 1)
        self.numberOfVerticalFaces = (self.nx + 1) * self.ny
        self.numberOfFaces = self.numberOfHorizontalFaces + self.numberOfVerticalFaces
        self.numberOfCells = self.nx * self.ny
        
        
        self.scale = {
            'length': 1.,
            'area': 1.,
            'volume': 1.
        }

	self.setScale(value = scale)
        
    def _translate(self, vector):
        return UniformGrid2D(dx = self.dx, nx = self.nx, 
                             dy = self.dy, ny = self.ny, 
                             origin = self.origin + vector)

    def __mul__(self, factor):
        return UniformGrid2D(dx = self.dx * factor, nx = self.nx, 
                             dy = self.dy * factor, ny = self.ny, 
                             origin = self.origin * factor)

    def _getConcatenableMesh(self):
        from fipy.meshes.numMesh.mesh2D import Mesh2D
        return Mesh2D(vertexCoords = self.getVertexCoords(), 
                      faceVertexIDs = self._createFaces(), 
                      cellFaceIDs = self._createCells())
                      
    def _concatenate(self, other, smallNumber):
        return self._getConcatenableMesh()._concatenate(other = other, smallNumber = smallNumber)
        
##     get topology methods

##         from common/mesh
        
    def _getCellFaceIDs(self):
        return MA.array(self._createCells())
        
    def getExteriorFaces(self):
        return FaceIterator(mesh=self,
                            ids=numerix.concatenate((numerix.arange(0, self.nx),
                                                     numerix.arange(0, self.nx) + self.nx * self.ny,
                                                     numerix.arange(0, self.ny) * (self.nx + 1) + self.numberOfHorizontalFaces,
                                                     numerix.arange(0, self.ny) * (self.nx + 1) + self.numberOfHorizontalFaces + self.nx)))
        
    def getInteriorFaces(self):
        Hids = numerix.arange(0, self.numberOfHorizontalFaces)
        Hids = numerix.reshape(Hids, (self.ny + 1, self.nx))
        Hids = Hids[1:-1,...]
        
        Vids = numerix.arange(self.numberOfHorizontalFaces, self.numberOfFaces)
        Vids = numerix.reshape(Vids, (self.ny, self.nx + 1))
        Vids = Vids[...,1:-1]
        
        return FaceIterator(mesh=self,
                            ids=numerix.concatenate((numerix.reshape(Hids, (self.nx * (self.ny - 1),)), 
                                                     numerix.reshape(Vids, ((self.nx - 1) * self.ny,)))))

    def _getCellFaceOrientations(self):
        # needs fix?
        tmp = numerix.MAtake(self.getFaceCellIDs()[...,0], self._getCellFaceIDs())
        return (tmp == MA.indices(tmp.shape)[0]) * 2 - 1

    def _getAdjacentCellIDs(self):
        # needs fix?
        faceCellIDs = self.getFaceCellIDs()
        return (MA.filled(faceCellIDs[...,0]), 
                MA.filled(MA.where(faceCellIDs[...,1].mask(), 
                                   faceCellIDs[...,0], 
                                   faceCellIDs[...,1])))

    def _getCellToCellIDs(self):
        ids = MA.zeros((self.ny, self.nx, 4))
        indices = numerix.indices((self.ny, self.nx))
        ids[...,0] = indices[1] + (indices[0] - 1) * self.nx
        ids[...,1] = (indices[1] + 1) + indices[0] * self.nx
        ids[...,2] = indices[1] + (indices[0] + 1) * self.nx
        ids[...,3] = (indices[1] - 1) + indices[0] * self.nx
        
        ids[ 0,...,0] = MA.masked
        ids[-1,...,2] = MA.masked
        ids[...,-1,1] = MA.masked
        ids[..., 0,3] = MA.masked
        
        return MA.reshape(ids, (self.numberOfCells, 4))
        
    def _getCellToCellIDsFilled(self):
        # needs fix?
        N = self.getNumberOfCells()
        M = self._getMaxFacesPerCell()
        cellIDs = numerix.reshape(numerix.repeat(numerix.arange(N), M), (N, M))
        cellToCellIDs = self._getCellToCellIDs()
        return MA.where(MA.getmaskarray(cellToCellIDs), cellIDs, cellToCellIDs)
        
    def _getMaxFacesPerCell(self):
        return 4
        
##         from numMesh/mesh

    def getVertexCoords(self):
        return self._createVertices() + self.origin

    def getFaceCellIDs(self):
        Hids = MA.zeros((self.nx, self.ny + 1, 2))
        indices = numerix.indices((self.nx, self.ny + 1))
        Hids[...,1] = indices[0] + indices[1] * self.nx
        Hids[...,0] = Hids[...,1] - self.nx
        Hids[...,0,0] = Hids[...,0,1]
        Hids[...,0,1] = MA.masked
        Hids[...,-1,1] = MA.masked

        Vids = MA.zeros((self.nx + 1, self.ny, 2))
        indices = numerix.indices((self.nx + 1, self.ny))
        Vids[...,1] = indices[0] + indices[1] * self.nx
        Vids[...,0] = Vids[...,1] - 1
        Vids[0,...,0] = Vids[0,...,1]
        Vids[0,...,1] = MA.masked
        Vids[-1,...,1] = MA.masked

        return MA.concatenate((numerix.reshape(MA.transpose(Hids,(1,0,2)), (self.numberOfHorizontalFaces, 2)), 
                                    numerix.reshape(MA.transpose(Vids,(1,0,2)), (self.numberOfFaces - self.numberOfHorizontalFaces, 2))))

##     get geometry methods
        
##         from common/mesh
        
    def _getFaceAreas(self):
        return numerix.concatenate((numerix.repeat((self.dx,), self.numberOfHorizontalFaces),
                                    numerix.repeat((self.dy,), self.numberOfFaces - self.numberOfHorizontalFaces)))

    def _getFaceNormals(self):
        Hnor = numerix.zeros((self.nx, self.ny + 1, 2), 'd')
        Hnor[...,1] = 1
        Hnor[...,0,1] = -1
        
        Vnor = numerix.zeros((self.nx + 1, self.ny, 2), 'd')
        Vnor[...,0] = 1
        Vnor[0,...,0] = -1
        
        return numerix.concatenate((numerix.reshape(numerix.swapaxes(Hnor, 0, 1), (self.nx * (self.ny + 1), 2)),
                                    numerix.reshape(numerix.swapaxes(Vnor, 0, 1), ((self.nx + 1) * self.ny, 2))))
        
    def getCellVolumes(self):
        return numerix.ones(self.numberOfCells, 'd') * self.dx * self.dy

    def getCellCenters(self):
        centers = numerix.zeros((self.nx, self.ny, 2), 'd')
        indices = numerix.indices((self.nx, self.ny))
        centers[...,0] = (indices[0] + 0.5) * self.dx
        centers[...,1] = (indices[1] + 0.5) * self.dy
        return numerix.reshape(numerix.swapaxes(centers, 0, 1), (self.numberOfCells, 2)) + self.origin

    def _getCellDistances(self):
        Hdis = numerix.repeat((self.dy,), self.numberOfHorizontalFaces)
        Hdis = numerix.reshape(Hdis, (self.nx, self.ny + 1))
        Hdis[...,0] = self.dy / 2.
        Hdis[...,-1] = self.dy / 2.
        
        Vdis = numerix.repeat((self.dx,), self.numberOfFaces - self.numberOfHorizontalFaces)
        Vdis = numerix.reshape(Vdis, (self.nx + 1, self.ny))
        Vdis[0,...] = self.dx / 2.
        Vdis[-1,...] = self.dx / 2.

        return numerix.concatenate((numerix.reshape(numerix.swapaxes(Hdis,0,1), (self.numberOfHorizontalFaces,)), 
                                    numerix.reshape(numerix.swapaxes(Vdis,0,1), (self.numberOfFaces - self.numberOfHorizontalFaces,))))

    def _getFaceToCellDistanceRatio(self):
        Hdis = numerix.ones((self.nx, self.ny + 1), 'd') * 0.5
        Hdis[...,0] = 1
        Hdis[...,-1] = 1
        
        Vdis = numerix.ones((self.nx + 1, self.ny), 'd') * 0.5
        Vdis[0,...] = 1
        Vdis[-1,...] = 1
        
        return numerix.concatenate((numerix.reshape(numerix.swapaxes(Hdis,0,1), (self.numberOfHorizontalFaces,)), 
                                    numerix.reshape(numerix.swapaxes(Vdis,0,1), (self.numberOfFaces - self.numberOfHorizontalFaces,))))
        
    def _getOrientedAreaProjections(self):
        return self._getAreaProjections()

    def _getAreaProjections(self):
        return self._getFaceNormals() * self._getFaceAreas()[..., numerix.NewAxis]

    def _getOrientedFaceNormals(self):
        return self._getFaceNormals()

    def _getFaceTangents1(self):
        Htan = numerix.zeros((self.nx, self.ny + 1, 2), 'd')
        Htan[...,0] = -1
        Htan[...,0,0] = 1
        
        Vtan = numerix.zeros((self.nx + 1, self.ny, 2), 'd')
        Vtan[...,1] = 1
        Vtan[0,...,1] = -1
        
        return numerix.concatenate((numerix.reshape(numerix.swapaxes(Htan, 0, 1), (self.nx * (self.ny + 1), 2)),
                                    numerix.reshape(numerix.swapaxes(Vtan, 0, 1), ((self.nx + 1) * self.ny, 2))))
        
    def _getFaceTangents2(self):
        return numerix.zeros((self.numberOfFaces, 2), 'd')
        
    def _getFaceAspectRatios(self):
        return self._getFaceAreas() / self._getCellDistances()
    
    def _getCellToCellDistances(self):
        distances = numerix.zeros((self.ny, self.nx, 4), 'd')
        distances[...,0] = self.dy
        distances[...,1] = self.dx
        distances[...,2] = self.dy
        distances[...,3] = self.dx
        
        distances[0,...,0] = self.dy / 2.
        distances[-1,...,2] = self.dy / 2.
        distances[...,0,3] = self.dx / 2.
        distances[...,-1,1] = self.dx / 2.
        
        return numerix.reshape(distances, (self.numberOfCells, 4))


    def _getCellNormals(self):
        normals = numerix.zeros((self.numberOfCells, 4, 2), 'd')
        normals[...,0,...] = ( 0, -1)
        normals[...,1,...] = ( 1,  0)
        normals[...,2,...] = ( 0,  1)
        normals[...,3,...] = (-1,  0)

        return normals
        
    def _getCellAreas(self):
        areas = numerix.ones((self.numberOfCells,4), 'd')
        areas[...,0] = self.dx
        areas[...,1] = self.dy
        areas[...,2] = self.dx
        areas[...,3] = self.dy
        return areas

    def _getCellAreaProjections(self):
        return self._getCellAreas()[...,numerix.NewAxis] * self._getCellNormals()

##         from numMesh/mesh

    def getFaceCenters(self):
        Hcen = numerix.zeros((self.nx, self.ny + 1, 2), 'd')
        indices = numerix.indices((self.nx, self.ny + 1))
        Hcen[...,0] = (indices[0] + 0.5) * self.dx
        Hcen[...,1] = indices[1] * self.dy
        
        Vcen = numerix.zeros((self.nx + 1, self.ny, 2), 'd')
        indices = numerix.indices((self.nx + 1, self.ny))
        Vcen[...,0] = indices[0] * self.dx
        Vcen[...,1] = (indices[1] + 0.5) * self.dy
        
        return numerix.concatenate((numerix.reshape(numerix.swapaxes(Hcen, 0, 1), (self.nx * (self.ny + 1), 2)),
                                    numerix.reshape(numerix.swapaxes(Vcen, 0, 1), ((self.nx + 1) * self.ny, 2)))) + self.origin
                                    
    def _getCellVertexIDs(self):
        ids = numerix.zeros((self.nx, self.ny, 4))
        indices = numerix.indices((self.nx, self.ny))
        ids[...,1] = indices[0] + (indices[1] + 1) * (self.nx + 1)
        ids[...,0] = ids[...,1] + 1
        ids[...,3] = indices[0] + indices[1] * (self.nx + 1)
        ids[...,2] = ids[...,3] + 1
        
        return numerix.reshape(ids, (self.numberOfCells, 4))
        
    def _getFaceVertexIDs(self):
        Hids = numerix.zeros((self.ny + 1, self.nx, 2))
        indices = numerix.indices((self.ny + 1, self.nx))
        Hids[...,0] = indices[1] + indices[0] * (self.nx + 1)
        Hids[...,1] = Hids[...,0] + 1

        Vids = numerix.zeros((self.ny, self.nx + 1, 2))
        indices = numerix.indices((self.ny, self.nx + 1))
        Vids[...,0] = indices[1] + indices[0] * (self.nx + 1)
        Vids[...,1] = Vids[...,0] + self.nx + 1
        
        return numerix.concatenate((numerix.reshape(Hids, (self.numberOfHorizontalFaces, 2)), 
                                    numerix.reshape(Vids, (self.numberOfFaces - self.numberOfHorizontalFaces, 2))))
                                    
    def _getOrderedCellVertexIDs(self):
        ids = numerix.zeros((self.ny, self.nx, 4))
        indices = numerix.indices((self.ny, self.nx))
        ids[...,1] = indices[1] + (indices[0] + 1) * (self.nx + 1)
        ids[...,0] = ids[...,1] + 1
        ids[...,2] = indices[1] + indices[0] * (self.nx + 1)
        ids[...,3] = ids[...,2] + 1
        
        return numerix.reshape(ids, (self.numberOfCells, 4))
        
##     scaling
    
    def _calcScaledGeometry(self):
        pass
        
    def _test(self):
        """
        These tests are not useful as documentation, but are here to ensure
        everything works as expected.

            >>> dx = 0.5
            >>> dy = 2.
            >>> nx = 3
            >>> ny = 2
            
            >>> mesh = UniformGrid2D(nx = nx, ny = ny, dx = dx, dy = dy)     
            
            >>> vertices = numerix.array(((0., 0.), (1., 0.), (2., 0.), (3., 0.),
            ...                           (0., 1.), (1., 1.), (2., 1.), (3., 1.),
            ...                           (0., 2.), (1., 2.), (2., 2.), (3., 2.)))
            >>> vertices *= numerix.array((dx, dy))
            >>> numerix.allequal(vertices, mesh._createVertices())
            1
        
            >>> faces = numerix.array(((1, 0), (2, 1), (3, 2),
            ...                        (4, 5), (5, 6), (6, 7),
            ...                        (8, 9), (9, 10), (10, 11),
            ...                        (0, 4), (5, 1), (6, 2), (7, 3),
            ...                        (4, 8), (9, 5), (10, 6), (11, 7)))
            >>> numerix.allequal(faces, mesh._createFaces())
            1

            >>> cells = numerix.array(((0, 10, 3, 9),
            ...                       (1 , 11, 4, 10),
            ...                       (2, 12, 5, 11),
            ...                       (3, 14, 6, 13),
            ...                       (4, 15, 7, 14),
            ...                       (5, 16, 8, 15)))
            >>> numerix.allequal(cells, mesh._createCells())
            1

            >>> externalFaces = numerix.array((0, 1, 2, 6, 7, 8, 9 , 13, 12, 16))
            >>> numerix.allequal(externalFaces, [face.getID() for face in mesh.getExteriorFaces()])
            1

            >>> internalFaces = numerix.array((3, 4, 5, 10, 11, 14, 15))
            >>> numerix.allequal(internalFaces, mesh.getInteriorFaces())
            1

            >>> import MA
            >>> faceCellIds = MA.masked_values(((0, -1), (1, -1), (2, -1),
            ...                                 (0, 3), (1, 4), (2, 5),
            ...                                 (3, -1), (4, -1), (5, -1),
            ...                                 (0, -1), (0, 1), (1, 2), (2, -1),
            ...                                 (3, -1), (3, 4), (4, 5), (5, -1)), -1)
            >>> numerix.allequal(faceCellIds, mesh.getFaceCellIDs())
            1
            
            >>> faceAreas = numerix.array((dx, dx, dx, dx, dx, dx, dx, dx, dx,
            ...                            dy, dy, dy, dy, dy, dy, dy, dy))
            >>> numerix.allclose(faceAreas, mesh._getFaceAreas(), atol = 1e-10, rtol = 1e-10)
            1
            
            >>> faceCoords = numerix.take(vertices, faces)
            >>> faceCenters = (faceCoords[:,0] + faceCoords[:,1]) / 2.
            >>> numerix.allclose(faceCenters, mesh.getFaceCenters(), atol = 1e-10, rtol = 1e-10)
            1

            >>> faceNormals = numerix.array(((0., -1.), (0., -1.), (0., -1.),
            ...                              (0., 1.), (0., 1.), (0., 1.),
            ...                              (0., 1.), (0., 1.), (0., 1.),
            ...                              (-1., 0), (1., 0), (1., 0), (1., 0),
            ...                              (-1., 0), (1., 0), (1., 0), (1., 0)))
            >>> numerix.allclose(faceNormals, mesh._getFaceNormals(), atol = 1e-10, rtol = 1e-10)
            1

            >>> cellToFaceOrientations = numerix.array(((1, 1, 1, 1), (1, 1, 1, -1), (1, 1, 1, -1),
            ...                                         (-1, 1, 1, 1), (-1, 1, 1, -1), (-1, 1, 1, -1)))
            >>> numerix.allequal(cellToFaceOrientations, mesh._getCellFaceOrientations())
            1
                                             
            >>> cellVolumes = numerix.array((dx*dy, dx*dy, dx*dy, dx*dy, dx*dy, dx*dy))
            >>> numerix.allclose(cellVolumes, mesh.getCellVolumes(), atol = 1e-10, rtol = 1e-10)
            1

            >>> cellCenters = numerix.array(((dx/2.,dy/2.), (3.*dx/2.,dy/2.), (5.*dx/2.,dy/2.),
            ...                              (dx/2.,3.*dy/2.), (3.*dx/2.,3.*dy/2.), (5.*dx/2.,3.*dy/2.)))
            >>> numerix.allclose(cellCenters, mesh.getCellCenters(), atol = 1e-10, rtol = 1e-10)
            1
                                              
            >>> cellDistances = numerix.array((dy / 2., dy / 2., dy / 2.,
            ...                                dy, dy, dy,
            ...                                dy / 2., dy / 2., dy / 2.,
            ...                                dx / 2., dx, dx,
            ...                                dx / 2.,
            ...                                dx / 2., dx, dx,
            ...                                dx / 2.))
            >>> numerix.allclose(cellDistances, mesh._getCellDistances(), atol = 1e-10, rtol = 1e-10)
            1
            
            >>> faceToCellDistances = MA.masked_values(((dy / 2., -1), (dy / 2., -1), (dy / 2., -1),
            ...                                         (dy / 2., dy / 2.), (dy / 2., dy / 2.), (dy / 2., dy / 2.),
            ...                                         (dy / 2., -1), (dy / 2., -1), (dy / 2., -1),
            ...                                         (dx / 2., -1), (dx / 2., dx / 2.), (dx / 2., dx / 2.),
            ...                                         (dx / 2., -1),
            ...                                         (dx / 2., -1), (dx / 2., dx / 2.), (dx / 2., dx / 2.),
            ...                                         (dx / 2., -1)), -1)
            >>> faceToCellDistanceRatios = faceToCellDistances[...,0] / cellDistances
            >>> numerix.allclose(faceToCellDistanceRatios, mesh._getFaceToCellDistanceRatio(), atol = 1e-10, rtol = 1e-10)
            1

            >>> areaProjections = faceNormals * faceAreas[...,numerix.NewAxis]
            >>> numerix.allclose(areaProjections, mesh._getAreaProjections(), atol = 1e-10, rtol = 1e-10)
            1

            >>> tangents1 = numerix.array(((1., 0), (1., 0),(1., 0),
            ...                            (-1., 0), (-1., 0),(-1., 0),
            ...                            (-1., 0), (-1., 0),(-1., 0),
            ...                            (0., -1.), (0., 1.), (0., 1.), (0., 1.),
            ...                            (0., -1.), (0., 1.), (0., 1.), (0., 1.)))
            >>> numerix.allclose(tangents1, mesh._getFaceTangents1(), atol = 1e-10, rtol = 1e-10)
            1

            >>> tangents2 = numerix.array(((0., 0), (0., 0),(0., 0),
            ...                            (-0., 0), (-0., 0),(-0., 0),
            ...                            (-0., 0), (-0., 0),(-0., 0),
            ...                            (0., -0.), (0., 0.), (0., 0.), (0., 0.),
            ...                            (0., -0.), (0., 0.), (0., 0.), (0., 0.)))
            >>> numerix.allclose(tangents2, mesh._getFaceTangents2(), atol = 1e-10, rtol = 1e-10)
            1

            >>> cellToCellIDs = MA.masked_values(((-1, 1, 3, -1),
            ...                                   (-1, 2, 4, 0),
            ...                                   (-1, -1, 5, 1),
            ...                                   (0, 4, -1, -1),
            ...                                   (1, 5, -1, 3),
            ...                                   (2, -1, -1, 4)), -1)
            >>> numerix.allequal(cellToCellIDs, mesh._getCellToCellIDs())
            1

            >>> cellToCellDistances = MA.masked_values(((dy / 2., dx, dy, dx / 2.),
            ...                                         (dy/ 2., dx, dy, dx),
            ...                                         (dy / 2., dx / 2., dy, dx),
            ...                                         (dy, dx, dy / 2., dx / 2.),
            ...                                         (dy, dx, dy / 2., dx),
            ...                                         (dy, dx / 2., dy / 2., dx)), -1)
            >>> numerix.allclose(cellToCellDistances, mesh._getCellToCellDistances(), atol = 1e-10, rtol = 1e-10)
            1

            >>> cellNormals = numerix.array((((0, -1), (1, 0), (0, 1), (-1, 0)),
            ...                              ((0, -1), (1, 0), (0, 1), (-1, 0)),
            ...                              ((0, -1), (1, 0), (0, 1), (-1, 0)),
            ...                              ((0, -1), (1, 0), (0, 1), (-1, 0)),
            ...                              ((0, -1), (1, 0), (0, 1), (-1, 0)),
            ...                              ((0, -1), (1, 0), (0, 1), (-1, 0)) ))
            >>> numerix.allclose(cellNormals, mesh._getCellNormals(), atol = 1e-10, rtol = 1e-10)
            1

            >>> vv = numerix.array(((0, -dx), (dy, 0), (0, dx), (-dy, 0)))
            >>> cellAreaProjections = numerix.array(((vv,vv,vv,vv,vv,vv)))
            >>> numerix.allclose(cellAreaProjections, mesh._getCellAreaProjections(), atol = 1e-10, rtol = 1e-10)
            1

            >>> cellVertexIDs = MA.masked_array(((5, 4, 1, 0),
            ...                                  (6, 5, 2, 1),
            ...                                  (7, 6, 3, 2),
            ...                                  (9, 8, 5, 4),
            ...                                  (10, 9, 6, 5),
            ...                                  (11, 10, 7, 6)), -1000) 

            >>> numerix.allclose(mesh._getCellVertexIDs(), cellVertexIDs)
            1

            >>> import tempfile
            >>> import os
            >>> from fipy.tools import dump
            
            >>> (f, filename) = tempfile.mkstemp('.gz')
            >>> pickledMesh = dump.write(mesh, filename)
            
            >>> unpickledMesh = dump.read(filename)
            >>> os.close(f)
            >>> os.remove(filename)

            >>> numerix.allequal(mesh.getCellCenters(), unpickledMesh.getCellCenters())
            1
            
            >>> print mesh._getFaceVertexIDs()
            [[ 0, 1,]
             [ 1, 2,]
             [ 2, 3,]
             [ 4, 5,]
             [ 5, 6,]
             [ 6, 7,]
             [ 8, 9,]
             [ 9,10,]
             [10,11,]
             [ 0, 4,]
             [ 1, 5,]
             [ 2, 6,]
             [ 3, 7,]
             [ 4, 8,]
             [ 5, 9,]
             [ 6,10,]
             [ 7,11,]]
        """

def _test():
    import doctest
    return doctest.testmod()

if __name__ == "__main__":
    _test()
