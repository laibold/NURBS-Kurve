
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import os
from Scene import *

SCENE_ORDER = 4
SCENE_CURVEPOINTS = 50

class RenderWindow:
    """GLFW Rendering window class"""
    def __init__(self):
        cwd = os.getcwd()
        if not glfw.init():
            return
        os.chdir(cwd)
        
        # buffer hints
        glfw.window_hint(glfw.DEPTH_BITS, 32)

        # make a window
        self.width, self.height = 600, 600

        self.window = glfw.create_window(self.width, self.height, "B-Spline", None, None)
        if not self.window:
            glfw.terminate()
            return

        # Make the window's context current
        glfw.make_context_current(self.window)
    
        # initialize GL
        glViewport(0, 0, self.width, self.height)
        glEnable(GL_DEPTH_TEST)
        glClearColor(1, 1, 1, 1)
        glMatrixMode(GL_PROJECTION)
        glMatrixMode(GL_MODELVIEW)

        # set window callbacks
        glfw.set_mouse_button_callback(self.window, self.onMouseButton)
        glfw.set_key_callback(self.window, self.onKeyboard)
        glfw.set_cursor_pos_callback(self.window, self.onMouseMove)
        
        # create 3D
        self.scene = Scene(SCENE_ORDER, SCENE_CURVEPOINTS)
        
        # exit flag
        self.exitNow = False

        self.startP = (0,0,0)
        self.shiftPressed = False

    def onMouseMove(self, win, x, y):
        self.currX = x / self.width * 2 - 1
        self.currY = (y / self.width * 2 - 1) * -1
        self.scene.changeWeight(self.currY)
    
    def onMouseButton(self, win, button, action, mods):
        if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
            if self.shiftPressed:
                self.scene.findClickedPoint(self.currX, self.currY)
            else:
                self.scene.addControlPoint(self.currX, self.currY)#
        elif button == glfw.MOUSE_BUTTON_LEFT and action == glfw.RELEASE:
            self.scene.resetClickedPoint()

    def onKeyboard(self, win, key, scancode, action, mods):
        if action == glfw.PRESS:
            if key == glfw.KEY_LEFT_SHIFT or key == glfw.KEY_RIGHT_SHIFT:
                self.shiftPressed = True
            elif key == glfw.KEY_M:
                if self.shiftPressed:
                    self.scene.increaseCurvePointCount()
                else:
                    self.scene.decreaseCurvePointCount()
            elif key == glfw.KEY_K:
                if self.shiftPressed:
                    self.scene.increaseOrder()
                else:
                    self.scene.decreaseOrder()
        elif action == glfw.RELEASE:
            if key == glfw.KEY_LEFT_SHIFT or key == glfw.KEY_RIGHT_SHIFT:
                self.shiftPressed = False

    def run(self):
        while not glfw.window_should_close(self.window) and not self.exitNow:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.scene.render()
            glfw.swap_buffers(self.window)
            glfw.poll_events()
        glfw.terminate()

# main() function
def main():
    rw = RenderWindow()
    rw.run()

# call main
if __name__ == '__main__':
    main()