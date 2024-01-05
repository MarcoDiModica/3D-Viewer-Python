import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import threading

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

class Tetrahedron:
    vertices = (
        (0, 1, 0), (-1, -1, 1), (1, -1, 1), (0, -1, -1)
    )

    edges = (
        (0, 1), (0, 2), (0, 3), (1, 2), (2, 3), (3, 1)
    )

    faces = (
        (0, 1, 2), (0, 2, 3), (0, 3, 1), (1, 3, 2)
    )

    colors = (
        (1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1), (1, 1, 1, 1)
    )

    def draw(self):
        glBegin(GL_TRIANGLES)
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

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    fov = 45  # Campo de visión inicial
    gluPerspective(fov, (display[0]/display[1]), 0.1, 100.0)
    glTranslatef(0.0, 0.0, -5)

    figures = {
    1: Cube(),
    2: Tetrahedron(),
}

    current_figure = figures[1]  # Figura actual

    cube_rotation = [0, 0]  # Rotación inicial del cubo
    cube_quaternion = euler_to_quaternion(cube_rotation[0], cube_rotation[1], 0) # Quaternion inicial del cubo
    cube_euler_principal = quaternion_to_euler_principal(cube_quaternion[0], cube_quaternion[1], cube_quaternion[2], cube_quaternion[3]) # Euler principal inicial del cubo
    cube_rotation_matrix = euler_to_rotation_matrix(cube_rotation[0], cube_rotation[1], 0) # Matriz de rotación inicial del cubo
    cube_rotation_vector = rotation_matrix_to_rotation_vector(cube_rotation_matrix) # Vector de rotación inicial del cubo
    mouse_down = False  # El mouse inicialmente no está presionado
    last_mouse_pos = (0, 0)  # Posición inicial del mouse

    info_window_thread = threading.Thread(target=start_info_window, args=(cube_rotation, cube_quaternion, cube_euler_principal, cube_rotation_vector, cube_rotation_matrix))
    info_window_thread.start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:  # Si se presiona una tecla
                if event.key == pygame.K_ESCAPE:  # Si la tecla es ESC
                    pygame.quit()  # Cierra pygame
                    quit()  # Cierra la ventana
                elif event.key == pygame.K_1:  # Si la tecla es 1, 2, 3 o 4
                    current_figure = figures[1]
                elif event.key == pygame.K_2:  # Si la tecla es 1, 2, 3 o 4
                    current_figure = figures[2]  # Cambia la figura actual
                elif event.key == pygame.K_r:  # Si la tecla 'R' se presiona
                    cube_rotation[:] = [0, 0]
                    cube_quaternion[:] = euler_to_quaternion(0, 0, 0)
                    cube_euler_principal[:] = quaternion_to_euler_principal(*cube_quaternion)
                    cube_rotation_matrix[:] = euler_to_rotation_matrix(0, 0, 0)
                    cube_rotation_vector[:] = rotation_matrix_to_rotation_vector(cube_rotation_matrix)
                elif event.key == pygame.K_LEFT:
                    cube_rotation[1] -= 5  # Rotar a la izquierda
                elif event.key == pygame.K_RIGHT:
                    cube_rotation[1] += 5  # Rotar a la derecha
                elif event.key == pygame.K_UP:
                    cube_rotation[0] -= 5  # Rotar hacia arriba
                elif event.key == pygame.K_DOWN:
                    cube_rotation[0] += 5  # Rotar hacia abajo
                elif event.key == pygame.K_q:  # Si la tecla 'Q' se presiona
                    controls_window = tk.Tk()
                    controls_window.title("Controls")

                    control1_label = tk.Label(controls_window, text="Si mantienes click izquierdo en la figura y mueves el mouse podras mover la figura")
                    control1_label.pack()

                    control2_label = tk.Label(controls_window, text="Tambien podras mover la figura con las flechas direccionales")
                    control2_label.pack()

                    control3_label = tk.Label(controls_window, text="Presiona 'R' para reiniciar la rotacion de la figura")
                    control3_label.pack()

                    control5_label = tk.Label(controls_window, text="Presiona 'M' para ingresar una rotacion en euler")
                    control5_label.pack()

                    control6_label = tk.Label(controls_window, text="Presiona 'N' para ingresar un quaternion")
                    control6_label.pack()

                    control7_label = tk.Label(controls_window, text="Presiona 'B' para ingresar un euler principal")
                    control7_label.pack()

                    control8_label = tk.Label(controls_window, text="Presiona 'V' para ingresar un vector de rotacion")
                    control8_label.pack()

                    control9_label = tk.Label(controls_window, text="Presiona 'C' para ingresar una matriz de rotacion")
                    control9_label.pack()
                    # Agrega mas

                    controls_window.mainloop()
                elif event.key == pygame.K_m:  # Si la tecla 'M' se presiona
                    root = tk.Tk()
                    root.withdraw()  # Oculta la ventana de Tkinter
                    rotation_input_x = simpledialog.askstring("Input", "Enter rotation for x-axis:",
                                                              parent=root)
                    rotation_input_y = simpledialog.askstring("Input", "Enter rotation for y-axis:",
                                                              parent=root)
                    x = int(rotation_input_x)
                    y = int(rotation_input_y)
                    cube_rotation[:] = [x, y]
                    root.destroy()  # Destruye la ventana de Tkinter
                elif event.key == pygame.K_n:  # Si la tecla 'N' se presiona
                    root = tk.Tk()
                    root.withdraw()  # Oculta la ventana de Tkinter
                    quaternion_input_w = simpledialog.askstring("Input", "Enter quaternion w component:",
                                                                parent=root)
                    quaternion_input_x = simpledialog.askstring("Input", "Enter quaternion x component:",
                                                                parent=root)
                    quaternion_input_y = simpledialog.askstring("Input", "Enter quaternion y component:",
                                                                parent=root)
                    quaternion_input_z = simpledialog.askstring("Input", "Enter quaternion z component:",
                                                                parent=root)
                    w = float(quaternion_input_w)
                    x = float(quaternion_input_x)
                    y = float(quaternion_input_y)
                    z = float(quaternion_input_z)
                    cube_rotation[:] = quaternion_to_euler(x, y, z, w)
                    root.destroy()  # Destruye la ventana de Tkinter
                elif event.key == pygame.K_b:
                    root = tk.Tk()
                    root.withdraw()
                    euler_principal_input_x = simpledialog.askstring("Input", "Enter euler principal for x-axis:",
                                                                         parent=root)
                    euler_principal_input_y = simpledialog.askstring("Input", "Enter euler principal for y-axis:",
                                                                         parent=root)
                    euler_principal_input_z = simpledialog.askstring("Input", "Enter euler principal for z-axis:",
                                                                         parent=root)
                    x = float(euler_principal_input_x)
                    y = float(euler_principal_input_y)
                    z = float(euler_principal_input_z)
                    cube_rotation[:] = quaternion_to_euler_principal(x, y, z, 0) 
                    root.destroy()
                elif event.key == pygame.K_v:
                    root = tk.Tk()
                    root.withdraw()
                    rotation_vector_input_x = simpledialog.askstring("Input", "Enter rotation vector for x-axis:",
                                                                         parent=root)
                    rotation_vector_input_y = simpledialog.askstring("Input", "Enter rotation vector for y-axis:",
                                                                         parent=root)
                    rotation_vector_input_z = simpledialog.askstring("Input", "Enter rotation vector for z-axis:",
                                                                         parent=root)
                    x = float(rotation_vector_input_x)
                    y = float(rotation_vector_input_y)
                    z = float(rotation_vector_input_z)
                    cube_rotation[:] = rotation_matrix_to_rotation_vector(np.array([[x], [y], [z]]))
                    root.destroy()
                elif event.key == pygame.K_c:
                    root = tk.Tk()
                    root.withdraw()
                    rotation_matrix_input_11 = simpledialog.askstring("Input", "Enter rotation matrix for 1,1:",
                                                                         parent=root)
                    rotation_matrix_input_12 = simpledialog.askstring("Input", "Enter rotation matrix for 1,2:",
                                                                         parent=root)
                    rotation_matrix_input_13 = simpledialog.askstring("Input", "Enter rotation matrix for 1,3:",
                                                                         parent=root)
                    rotation_matrix_input_21 = simpledialog.askstring("Input", "Enter rotation matrix for 2,1:",
                                                                         parent=root)
                    rotation_matrix_input_22 = simpledialog.askstring("Input", "Enter rotation matrix for 2,2:",
                                                                         parent=root)
                    rotation_matrix_input_23 = simpledialog.askstring("Input", "Enter rotation matrix for 2,3:",
                                                                         parent=root)
                    rotation_matrix_input_31 = simpledialog.askstring("Input", "Enter rotation matrix for 3,1:",
                                                                         parent=root)
                    rotation_matrix_input_32 = simpledialog.askstring("Input", "Enter rotation matrix for 3,2:",
                                                                         parent=root)
                    rotation_matrix_input_33 = simpledialog.askstring("Input", "Enter rotation matrix for 3,3:",
                                                                         parent=root)
                    x = np.array([[float(rotation_matrix_input_11), float(rotation_matrix_input_12), float(rotation_matrix_input_13)], 
                                  [float(rotation_matrix_input_21), float(rotation_matrix_input_22), float(rotation_matrix_input_23)],
                                  [float(rotation_matrix_input_31), float(rotation_matrix_input_32), float(rotation_matrix_input_33)]])
                    cube_rotation[:] = rotation_matrix_to_rotation_vector(x)
                    root.destroy()              
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

        cube_rotation[0] %= 360  # Limita la rotación en el eje x a 360 grados
        cube_rotation[1] %= 360  # Limita la rotación en el eje y a 360 grados
        cube_quaternion = euler_to_quaternion(cube_rotation[0], cube_rotation[1], 0)  # Actualiza el quaternion del cubo
        cube_euler_principal = quaternion_to_euler_principal(cube_quaternion[0], cube_quaternion[1], cube_quaternion[2], cube_quaternion[3])  # Actualiza el euler principal del cubo
        cube_rotation_matrix = euler_to_rotation_matrix(cube_rotation[0], cube_rotation[1], 0)  # Actualiza la matriz de rotación del cubo
        cube_rotation_vector = rotation_matrix_to_rotation_vector(cube_rotation_matrix)  # Actualiza el vector de rotación del cubo

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

        pygame.display.set_caption("Ventana 3D: Presiona Q para ver los controles")

        pygame.display.flip()
        pygame.time.wait(10)

def start_info_window(cube_rotation, cube_quaternion, cube_euler_principal, cube_rotation_vector, cube_rotation_matrix):
    def update_info_window():
        rotation_label.config(text="Euler Angles: " + str(cube_rotation))

        print_quaternion = euler_to_quaternion(cube_rotation[0], cube_rotation[1], 0)
        quaternion_label.config(text="Quaternion: (" + ", ".join(f"{i:.4f}" for i in print_quaternion) + ")")

        print_euler_principal = quaternion_to_euler_principal(print_quaternion[0], print_quaternion[1], print_quaternion[2], print_quaternion[3])
        euler_principal_label.config(text="Euler Principal: (" + ", ".join(f"{i:.4f}" for i in print_euler_principal) + ")")

        print_rotation_matrix = euler_to_rotation_matrix(cube_rotation[0], cube_rotation[1], 0)
        rotation_matrix_string = '\n'.join(['\t'.join([str(cell) for cell in row]) for row in print_rotation_matrix])
        rotation_matrix_label.config(text="Rotation Matrix:\n" + rotation_matrix_string)

        print_rotation_vector = rotation_matrix_to_rotation_vector(print_rotation_matrix)
        rotation_vector_string = ', '.join([str(i[0]) for i in print_rotation_vector])
        rotation_vector_label.config(text="Rotation Vector: " + rotation_vector_string)
        
        info_window.after(100, update_info_window)  # Actualiza la ventana de información cada 100 ms

    info_window = tk.Tk()
    info_window.title("Information")

    rotation_label = tk.Label(info_window)
    rotation_label.pack()

    quaternion_label = tk.Label(info_window)
    quaternion_label.pack()

    euler_principal_label = tk.Label(info_window)
    euler_principal_label.pack()

    rotation_vector_label = tk.Label(info_window)
    rotation_vector_label.pack()

    rotation_matrix_label = tk.Label(info_window)
    rotation_matrix_label.pack()

    info_window.after(100, update_info_window)
    info_window.mainloop()

def euler_to_quaternion(roll, pitch, yaw):
    cos_roll_2 = np.cos(roll/2)
    sin_roll_2 = np.sin(roll/2)
    cos_pitch_2 = np.cos(pitch/2)
    sin_pitch_2 = np.sin(pitch/2)
    cos_yaw_2 = np.cos(yaw/2)
    sin_yaw_2 = np.sin(yaw/2)

    qx = sin_roll_2 * cos_pitch_2 * cos_yaw_2 - cos_roll_2 * sin_pitch_2 * sin_yaw_2
    qy = cos_roll_2 * sin_pitch_2 * cos_yaw_2 + sin_roll_2 * cos_pitch_2 * sin_yaw_2
    qz = cos_roll_2 * cos_pitch_2 * sin_yaw_2 - sin_roll_2 * sin_pitch_2 * cos_yaw_2
    qw = cos_roll_2 * cos_pitch_2 * cos_yaw_2 + sin_roll_2 * sin_pitch_2 * sin_yaw_2
    return [qx, qy, qz, qw]

def quaternion_to_euler(x, y, z, w):
    roll = np.arctan2(2*(w*x + y*z), 1 - 2*(x**2 + y**2))
    pitch = np.arcsin(2*(w*y - z*x))
    yaw = np.arctan2(2*(w*z + x*y), 1 - 2*(y**2 + z**2))
    return [roll, pitch, yaw]

def quaternion_to_euler_principal(x, y, z, w):
    roll = np.arctan2(2*(w*x + y*z), 1 - 2*(x**2 + y**2))
    pitch = np.arcsin(2*(w*y - z*x))
    yaw = np.arctan2(2*(w*z + x*y), 1 - 2*(y**2 + z**2))
    return [roll, pitch, yaw]

def euler_to_rotation_matrix(roll, pitch, yaw):
    R_x = np.array([[1, 0, 0],
                    [0, np.cos(roll), -np.sin(roll)],
                    [0, np.sin(roll), np.cos(roll)]])

    R_y = np.array([[np.cos(pitch), 0, np.sin(pitch)],
                    [0, 1, 0],
                    [-np.sin(pitch), 0, np.cos(pitch)]])

    R_z = np.array([[np.cos(yaw), -np.sin(yaw), 0],
                    [np.sin(yaw), np.cos(yaw), 0],
                    [0, 0, 1]])

    R = np.dot(R_z, np.dot(R_y, R_x))
    return R

def rotation_matrix_to_rotation_vector(R):
    theta = np.arccos((R[0, 0] + R[1, 1] + R[2, 2] - 1)/2)
    k = 1/(2*np.sin(theta)) * np.array([[R[2, 1] - R[1, 2]],
                                         [R[0, 2] - R[2, 0]],
                                         [R[1, 0] - R[0, 1]]])
    return theta*k

if __name__ == "__main__":
    main()


# info_window = tk.Tk()
#         info_window.title("Information")

#         rotation_label = tk.Label(info_window, text="Euler Angles: " + str(cube_rotation))
#         rotation_label.pack()

#         quaternion_label = tk.Label(info_window, text="Quaternion: (" + ", ".join(f"{i:.4f}" for i in cube_quaternion) + ")")
#         quaternion_label.pack()

#         euler_principal_label = tk.Label(info_window, text="Euler Principal: (" + ", ".join(f"{i:.4f}" for i in cube_euler_principal) + ")")
#         euler_principal_label.pack()

#         rotation_vector_string = ', '.join([str(i[0]) for i in cube_rotation_vector])

#         rotation_vector_label = tk.Label(info_window, text="Rotation Vector: " + rotation_vector_string)
#         rotation_vector_label.pack()

#         rotation_matrix_string = '\n'.join(['\t'.join([str(cell) for cell in row]) for row in cube_rotation_matrix])

#         rotation_vector_label = tk.Label(info_window, text="Rotation Matrix:\n" + rotation_matrix_string)
#         rotation_vector_label.pack()

#         info_window.mainloop()