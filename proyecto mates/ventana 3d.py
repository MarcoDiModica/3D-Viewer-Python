import tkinter as tk
from tkinter import filedialog
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import pyassimp
import numpy as np

class Cube:
    vertices = (
        (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, -1),
        (1, -1, 1), (1, 1, 1), (-1, -1, 1), (-1, 1, 1)
    )

    edges = (
        (0, 1), (0, 3), (0, 4), (2, 1), (2, 3), (2, 7),
        (6, 3), (6, 4), (6, 7), (5, 1), (5, 4), (5, 7)
    )

    faces = [
        (0, 1, 2, 3), (3, 2, 7, 6), (6, 7, 5, 4),
        (4, 5, 1, 0), (1, 5, 7, 2), (4, 0, 3, 6)
    ]

    colors = (
        (1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1),
        (1, 1, 1, 1), (1, 1, 0, 1), (1, 0, 1, 1)
    )

    def draw(self):
        glBegin(GL_QUADS)
        for face_color, face in enumerate(self.faces):
            glColor4fv(self.colors[face_color])
            for vertex in face:
                glVertex3fv(self.vertices[vertex])
        glEnd()

        glColor3fv((0, 0, 0))
        glBegin(GL_LINES)
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.vertices[vertex])
        glEnd()

class Pyramid:
    vertices = (
        (0, 1, 0), (1, -1, 1), (1, -1, -1), (-1, -1, -1), (-1, -1, 1)
    )

    edges = (
        (0, 1), (0, 2), (0, 3), (0, 4), (1, 2),
        (2, 3), (3, 4), (4, 1)
    )

    faces = (
        (0, 1, 2, 3), (0, 1, 4), (0, 3, 4), (0, 2, 3), (1, 2, 4)
    )

    colors = (
        (1, 0, 0), (0, 1, 0), (0, 0, 1),
        (1, 1, 1), (1, 1, 0)
    )
    
    def draw(self):
        glBegin(GL_QUADS)
        for face_color, face in enumerate(self.faces):
            glColor3fv(self.colors[face_color])
            for vertex in face:
                glVertex3fv(self.vertices[vertex])
        glEnd()

        glColor3fv((0, 0, 0))
        glBegin(GL_LINES)
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.vertices[vertex])
        glEnd()

class Object3D:
    def __init__(self, filename):
        self.scene = None
        self.filename = filename

    def draw(self):
        with pyassimp.load(self.filename) as scene:
            self.scene = scene
            for mesh in scene.meshes:
                glBegin(GL_TRIANGLES)
                for face in mesh.faces:
                    for index in face.indices:
                        vertex = mesh.vertices[index]
                        if isinstance(vertex, (list, tuple)) and len(vertex) == 3:
                            glVertex3fv(vertex)
                        else:
                            print(f"Unexpected vertex data: {vertex}")
                glEnd()

    def __del__(self):
        # Es importante liberar los recursos cuando ya no se necesitan
        pyassimp.release(self.scene)

def open_file_dialog():
    root = tk.Tk()
    root.withdraw()
    filename = filedialog.askopenfilename()
    return filename

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    fov = 45  # Campo de visión inicial
    gluPerspective(fov, (display[0]/display[1]), 0.1, 100.0)
    glTranslatef(0.0, 0.0, -5)

    figures = {
    1: Cube(),
    2: Pyramid(),
}

    current_figure = figures[1]  # Figura actual
    obj3d = None  # Inicialmente no hay ningún objeto 3D cargado

    cube_rotation = [0, 0]  # Rotación inicial del cubo
    cube_quaternion = euler_to_quaternion(cube_rotation[0], cube_rotation[1], 0) # Quaternion inicial del cubo
    mouse_down = False  # El mouse inicialmente no está presionado
    last_mouse_pos = (0, 0)  # Posición inicial del mouse

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:  # Si se presiona una tecla
                if event.key == pygame.K_ESCAPE:  # Si la tecla es ESC
                    pygame.quit()  # Cierra pygame
                    quit()  # Cierra la ventana
                if event.key == pygame.K_o:  # Si la tecla 'O' se presiona
                    root = tk.Tk()
                    root.withdraw()  # Oculta la ventana de Tkinter
                    file_path = filedialog.askopenfilename()  # Abre la ventana de diálogo de archivo
                    print(file_path)  # Imprime el camino del archivo seleccionado
                    root.destroy()  # Destruye la ventana de Tkinter
                    obj3d = Object3D(file_path)  # Crea un objeto 3D con el archivo seleccionado
                    current_figure = obj3d  # Establece el objeto 3D como la figura actual
                if event.key == pygame.K_1:  # Si la tecla es 1, 2, 3 o 4
                    current_figure = figures[1]
                if event.key == pygame.K_2:  # Si la tecla es 1, 2, 3 o 4
                    current_figure = figures[2]  # Cambia la figura actual
                if event.key == pygame.K_r:  # Si la tecla 'R' se presiona
                    cube_rotation = [0, 0]
            elif event.type == pygame.MOUSEBUTTONDOWN:  # Si el botón del mouse se presiona
                if event.button == 1:  # Si el botón izquierdo del mouse se presiona
                    mouse_down = True
                    last_mouse_pos = pygame.mouse.get_pos()  # Guarda la posición actual del mouse
                elif event.button == 4:  # Si se gira la rueda del mouse hacia arriba
                    fov = max(1, fov - 1)  # Disminuye el campo de visión para hacer zoom in
                elif event.button == 5:  # Si se gira la rueda del mouse hacia abajo
                    fov = min(180, fov + 1)  # Aumenta el campo de visión para hacer zoom out
            elif event.type == pygame.MOUSEBUTTONUP:  # Si el botón del mouse se suelta
                if event.button == 1:  # Si el botón izquierdo del mouse se suelta
                    mouse_down = False
            elif event.type == pygame.MOUSEMOTION:  # Si el mouse se mueve
                if mouse_down:  # Si el botón izquierdo del mouse está presionado
                    mouse_pos = pygame.mouse.get_pos()  # Obtiene la posición actual del mouse
                    dx, dy = mouse_pos[0] - last_mouse_pos[0], mouse_pos[1] - last_mouse_pos[1]  # Calcula el desplazamiento del mouse
                    cube_rotation[0] += dy  # Rota el cubo en el eje x según el desplazamiento vertical del mouse
                    cube_rotation[1] += dx  # Rota el cubo en el eje y según el desplazamiento horizontal del mouse
                    last_mouse_pos = mouse_pos  # Actualiza la última posición del mouse

        cube_quaternion = euler_to_quaternion(cube_rotation[0], cube_rotation[1], 0)  # Actualiza el quaternion del cubo

        glLoadIdentity()
        gluPerspective(fov, (display[0]/display[1]), 0.1, 100.0)  # Actualiza el campo de visión
        glTranslatef(0.0, 0.0, -5)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        if current_figure is not None:  # Si hay una figura seleccionada
            glPushMatrix()  # Guarda la matriz de transformación actual
            glRotatef(cube_rotation[0], 1, 0, 0)  # Rota la figura en el eje x
            glRotatef(cube_rotation[1], 0, 1, 0)  # Rota la figura en el eje y
            current_figure.draw()  # Dibuja la figura
            glPopMatrix()  # Restaura la matriz de transformación

        if obj3d is not None:  # Si hay un objeto 3D cargado, dibujarlo
            obj3d.draw()

        rotation_text = "Rotation: " + str(cube_rotation)
        quaternion_text = "Quaternion: " + str(cube_quaternion)

        pygame.display.set_caption(rotation_text + " | " + quaternion_text)

        pygame.display.flip()
        pygame.time.wait(10)

def euler_to_quaternion(roll, pitch, yaw):
    qx = np.sin(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) - np.cos(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)
    qy = np.cos(roll/2) * np.sin(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.cos(pitch/2) * np.sin(yaw/2)
    qz = np.cos(roll/2) * np.cos(pitch/2) * np.sin(yaw/2) - np.sin(roll/2) * np.sin(pitch/2) * np.cos(yaw/2)
    qw = np.cos(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)
    return [qx, qy, qz, qw]

def draw_text(text, position):
    font = pygame.font.Font(None, 24)
    text_surface = font.render(text, True, (255, 255, 255, 255), (0, 0, 0, 255))
    text_rect = text_surface.get_rect()
    text_rect.topleft = position
    pygame.display.get_surface().blit(text_surface, text_rect)

def draw_text_in_new_window(text):
    # Crea una nueva ventana
    info_window = pygame.display.set_mode((300, 200))  # Ajusta el tamaño según tus necesidades

    # Crea la fuente y la superficie del texto
    font = pygame.font.Font(None, 24)
    text_surface = font.render(text, True, (255, 255, 255, 255), (0, 0, 0, 255))

    # Dibuja el texto en la nueva ventana
    info_window.blit(text_surface, (10, 10))  # Ajusta la posición según tus necesidades

    # Actualiza la nueva ventana
    pygame.display.flip()

if __name__ == "__main__":
    main()

