import numpy as np
from OpenGL.GL import *
from OpenGL.arrays import vbo
from RenderWindow import *

CURVE_POINT_CHANGE = 5
DEFAULT_WEIGHT = 1
MIN_WEIGHT = 1
MAX_WEIGHT = 10
MIN_ORDER = 3

class Point:
    def __init__(self, x, y, z=1, weight=DEFAULT_WEIGHT):
        self.x = x
        self.y = y
        self.z = z
        self.weight = weight

    def getPosList(self):
        return[self.x, self.y]

class PointList:
    def __init__(self):
        self.points = []

    def append(self, point):
        self.points.append(point)

    def __len__(self):
        return len(self.points)

    def array(self): #for drawing
        return [point.getPosList() for point in self.points]

    def __getitem__(self, i):
        return self.points[i]

    def getCalcPoints(self):
        return [[p.x*p.weight, p.y*p.weight, p.z*p.weight] for p in self.points]

    def clear(self):
        self.points = []

class Scene:
    """ OpenGL 2D scene class """
    def __init__(self, order, curvePointCount):
        self.order = order
        self.curvePointCount = curvePointCount
        self.controlPoints = PointList()
        self.curvePoints = PointList()
        self.clickedPoint = None
        self.clickedYCoord = 0
        self.lastCalcedWeight = 0 # see changeWeight()

    def addControlPoint(self, x, y):
        self.controlPoints.append(Point(x,y))
        self.calcCurve()

    def increaseCurvePointCount(self):
        self.curvePointCount += CURVE_POINT_CHANGE
        self.calcCurve()

    def decreaseCurvePointCount(self):
        if self.curvePointCount > CURVE_POINT_CHANGE:
            self.curvePointCount -= CURVE_POINT_CHANGE
        self.calcCurve()

    def increaseOrder(self):
        self.order += 1
        self.calcCurve()
        print("Ordnung", self.order)

    def decreaseOrder(self):
        if self.order > MIN_ORDER:
            self.order -= 1
        self.calcCurve()
        print("Ordnung", self.order)

    def hasEnoughPoints(self):
        return len(self.controlPoints) >= self.order

    def changeWeight(self, newY):
        if (self.clickedPoint):
            val = int(self.clickedYCoord + (newY - self.clickedPoint.y) * 10)
            if val != self.lastCalcedWeight and MIN_WEIGHT < val <= MAX_WEIGHT:
                self.clickedPoint.weight = val
                print("Neues Gewicht:", self.clickedPoint.weight)
                self.calcCurve()
            self.lastCalcedWeight = val

    def findClickedPoint(self, x, y):
        self.clickedYCoord = y

        TOL = 0.025
        minX = x - TOL
        maxX = x + TOL
        minY = y - TOL
        maxY = y + TOL
        for point in self.controlPoints:
            if minX < point.x < maxX and minY < point.y < maxY:
                self.clickedPoint = point

    def resetClickedPoint(self):
        self.clickedPoint = None

    #pinned uniform
    def calcKnotVector(self):
        if self.hasEnoughPoints():
            return [0 for x in range(0, self.order)] + \
                [x for x in range(1, len(self.controlPoints) - (self.order - 2))] + \
                [len(self.controlPoints) - (self.order - 2) for x in range(self.order)]

    def deboor(self, i, j, controlpoints, knotvector, t):
        if j == 0:
            if i == len(controlpoints):
                return controlpoints[i - 1]
            else:
                return controlpoints[i]

        a = (t - knotvector[i])
        b = (knotvector[i - j + self.order] - knotvector[i])

        if b == 0:
            alpha = 0
        else:
            alpha = a / b

        left_term = self.deboor(i - 1, j - 1, controlpoints, knotvector, t)
        right_term = self.deboor(i, j - 1, controlpoints, knotvector, t)
        return (1 - alpha) * np.asarray(left_term) + alpha * np.asarray(right_term)

    def calcCurve(self):
        self.curvePoints.clear()
        if self.hasEnoughPoints():
            calcPointList = self.controlPoints.getCalcPoints()
            knotVector = self.calcKnotVector()
            for i in range(self.curvePointCount + 1):
                t = knotVector[-1] * (i / self.curvePointCount)
                r = None
                for j in range(len(knotVector)):
                    if (t == knotVector[-1]):
                        r = len(knotVector) - self.order -1
                        break
                    if knotVector[j] <= t < knotVector[j + 1]:
                        r = j
                        break
                    
                point = self.deboor(r, self.order-1, calcPointList, knotVector, t)
                self.curvePoints.append(Point(point[0] / point[2], point[1] / point[2]))

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT)
        vbos = vbo.VBO(np.array(self.controlPoints.array(), 'f'))
        vbos.bind()

        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(2, GL_FLOAT, 0, vbos)
        
        glPointSize(3)
        glColor3fv([0, 0, 0])
        glDrawArrays(GL_POINTS, 0 , len(self.controlPoints))

        if len(self.controlPoints) > 1:
            glColor3fv([.7, .7, .7])
            glDrawArrays(GL_LINE_STRIP, 0, len(self.controlPoints))

        if self.curvePoints and self.hasEnoughPoints():
            vbos = vbo.VBO(np.array(self.curvePoints.array(), 'f'))
            vbos.bind()
            glEnableClientState(GL_VERTEX_ARRAY)
            glVertexPointer(2, GL_FLOAT, 0, vbos)
            glColor3fv([0, 0, 0])
            glDrawArrays(GL_LINE_STRIP, 0, len(vbos))
            vbos.unbind()

        glDisableClientState(GL_VERTEX_ARRAY)

        glFlush()

if __name__ == '__main__':
    main()
    