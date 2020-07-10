import numpy as np
from OpenGL.GL import *
from OpenGL.arrays import vbo
from RenderWindow import *

CURVE_POINT_CHANGE = 5
DEFAULT_WEIGHT = 2

class Point:
    def __init__(self, x, y, z=1, weight=DEFAULT_WEIGHT):
        self.x = x
        self.y = y
        self.z = z
        self.weight = weight

    def increaseWeight(self):
        self.weight += 1

    def decreaseWeight(self):
        if self.weight > 1:
            self.weight -= 1

    def resetWeight(self):
        self.weight = 1

    def getPosList(self):
        return[self.x, self.y]

    def getPosWeightList(self):
        return[self.x, self.y, self.z]

class PointList:
    def __init__(self):
        self.points = []

    def append(self, point):
        self.points.append(point)

    def __len__(self):
        return len(self.points)

    def array(self):
        lst = []
        for point in self.points:
            lst.append(point.getPosList())
        return lst

    def __getitem__(self, i):
        return self.points[i]

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

        self.curve = []

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
        if self.order > 2:
            self.order -= 1
        self.calcCurve()
        print("Ordnung", self.order)

    def hasEnoughPoints(self):
        return len(self.controlPoints) >= self.order

    def changeWeight(self, newY):
        if (self.clickedPoint):
            val = int(self.clickedYCoord + (newY - self.clickedPoint.y) * 10)
            if 0 < val <= 10:
                self.clickedPoint.weight = val
                print("Neues Gewicht:", self.clickedPoint.weight)
                self.calcCurve()

    def findClickedPoint(self, x, y):
        self.clickedYCoord = y
        print("Clicked at", x,",",y)

        TOL = 0.025
        minX = x - TOL
        maxX = x + TOL
        minY = y - TOL
        maxY = y + TOL
        for point in self.controlPoints:
            if minX < point.x < maxX and minY < point.y < maxY:
                print("Punkt gefunden: ", point.getPosList())
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
            return controlpoints[i]

        a = (t - knotvector[i])
        b = (knotvector[i - j + self.order] - knotvector[i])

        if b == 0:
            alpha = 0
        else:
            alpha = a / b

        left_term = self.deboor(i - 1, j - 1, controlpoints, knotvector, t)
        right_term = self.deboor(i, j - 1, controlpoints, knotvector, t)

        #x = ((1 - alpha) * left_term.x) + (alpha * right_term.x)
        #y = ((1 - alpha) * left_term.y) + (alpha * right_term.y)

        leftArray = np.asarray(left_term)
        rightArray = np.asarray(right_term)

        p = (1 - alpha) * leftArray + alpha * rightArray

        return p

    def getCalcPoints(self):
        calcPoints = []
        for p in self.controlPoints:
            calcPoints.append(Point(p.x * p.weight, p.y * p.weight))
        return calcPoints

    def calcCurve(self):
        #print("Anzahl Punkte: {}, Ordnung {}".format(len(self.controlPoints), self.order))
        self.curvePoints.clear()
        
        calcPointList = self.calcPointList()
        #calcedPoints = self.calcPoints(calcPointList)
        
        if self.hasEnoughPoints():
            calcPoints = self.getCalcPoints()
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
                    
                self.curvePoints.append(self.deboor(r, self.order-1, calcPointList, knotVector, t))
            self.calcCurvePoints()

    def calcPointList(self):
        calcPointList = []
        for p in self.controlPoints:
            calcPointList.append([p.x*p.weight, p.y*p.weight, p.z*p.weight])
            #calcPointList.append(Point(p.x*p.weight, p.y*p.weight, p.z*p.weight))
        return calcPointList

    def calcPoints(self, calcPointList):
        points = []
        for p in calcPointList:
            points.append(Point(p.x/p.weight, p.y/p.weight))
        return calcPointList

    def calcCurvePoints(self):
        self.curve.clear()
        for p in self.curvePoints:
            self.curve.append([p[0] / p[2], p[1] / p[2]])

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

        if self.curve and self.hasEnoughPoints():
            vbos = vbo.VBO(np.array(self.curve, 'f'))
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