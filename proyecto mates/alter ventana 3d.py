import tkinter as tk
#from tkinter import filedialog
from tkinter import simpledialog
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import threading
import math

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

class Rotation:
    def __init__(self):
        # Inicializa la rotación a una identidad (sin rotación)
        self.quaternion = [1, 0, 0, 0]
        self.update_all_from_quaternion()

    def update_all_from_quaternion(self):
        # Actualiza todas las representaciones a partir del cuaternión
        self.euler_principal = self.quaternion_to_euler_principal()
        self.euler_angles = self.quaternion_to_euler_angles()
        self.rotation_vector = self.quaternion_to_rotation_vector()
        self.rotation_matrix = self.quaternion_to_rotation_matrix()

    def quaternion_to_euler_principal(self):
        # Convierte el cuaternión a Euler Principal (Ángulo y Eje)
        w, x, y, z = self.quaternion
        angle = 2 * math.acos(w)
        norm = x*x + y*y + z*z
        if norm < 0.001:  # when all euler angles are zero angle =0 so we can set axis to anything to avoid divide by zero
            x=1
            y=z=0
        else:
            norm = math.sqrt(norm)
            x /= norm
            y /= norm
            z /= norm
        return (angle, x, y, z)

    def quaternion_to_euler_angles(self):
        # Convierte el cuaternión a Ángulos de Euler
        w, x, y, z = self.quaternion
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        X = math.atan2(t0, t1)

        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        Y = math.asin(t2)

        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        Z = math.atan2(t3, t4)

        return X, Y, Z  # in radians

    def quaternion_to_rotation_vector(self):
        # Convierte el cuaternión a Vector de Rotación
        angle, x, y, z = self.quaternion_to_euler_principal()
        return (x*angle, y*angle, z*angle)

    def quaternion_to_rotation_matrix(self):
        # Convierte el cuaternión a Matriz de Rotación
        w, x, y, z = self.quaternion
        return [[1 - 2*y*y - 2*z*z, 2*x*y - 2*z*w, 2*x*z + 2*y*w],
                [2*x*y + 2*z*w, 1 - 2*x*x - 2*z*z, 2*y*z - 2*x*w],
                [2*x*z - 2*y*w, 2*y*z + 2*x*w, 1 - 2*x*x - 2*y*y]]

    def set_from_quaternion(self, quaternion):
        # Establece la rotación a partir de un cuaternión
        self.quaternion = quaternion
        self.update_all_from_quaternion()

    def set_from_euler_principal(self, angle, x, y, z):
        # Establece la rotación a partir de un ángulo y eje
        self.quaternion = [math.cos(angle/2), x*math.sin(angle/2), y*math.sin(angle/2), z*math.sin(angle/2)]
        self.update_all_from_quaternion()

    def set_from_euler_angles(self, x, y, z):
        # Establece la rotación a partir de ángulos de Euler
        X = math.cos(x/2)
        Y = math.sin(x/2)
        Z = math.cos(y/2)
        W = math.sin(y/2)
        A = math.cos(z/2)
        B = math.sin(z/2)

        self.quaternion = [X*Z*A + Y*W*B, X*Z*B - Y*W*A, Y*Z*A + X*W*B, Y*Z*B - X*W*A]
        self.update_all_from_quaternion()
    
    def set_from_rotation_vector(self, x, y, z):
        # Establece la rotación a partir de un vector de rotación
        angle = math.sqrt(x*x + y*y + z*z)
        self.quaternion = [math.cos(angle/2), x*math.sin(angle/2)/angle, y*math.sin(angle/2)/angle, z*math.sin(angle/2)/angle]
        self.update_all_from_quaternion()
    
    def set_from_rotation_matrix(self, R):
        # Establece la rotación a partir de una matriz de rotación
        w = math.sqrt(1 + R[0][0] + R[1][1] + R[2][2]) / 2
        w4 = 4*w
        x = (R[2][1] - R[1][2]) / w4
        y = (R[0][2] - R[2][0]) / w4
        z = (R[1][0] - R[0][1]) / w4
        self.quaternion = [w, x, y, z]
        self.update_all_from_quaternion()
    
    


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

    cube_rotation = Rotation()  # Rotación inicial del cubo
    mouse_down = False  # El mouse inicialmente no está presionado
    last_mouse_pos = (0, 0)  # Posición inicial del mouse

    MAX_ROTATION_SPEED = 5

    # Inicializa la ventana de información en un thread para que no se sobreponga con la ventana principal
    info_window_thread = threading.Thread(target=start_info_window, args=(cube_rotation,))
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
                    cube_rotation.set_from_quaternion([1, 0, 0, 0])
                elif event.key == pygame.K_LEFT:
                    roll, pitch, yaw = cube_rotation.euler_angles
                    desired_pitch = pitch - 5  # Para rotar a la izquierda
                    pitch_difference = desired_pitch - pitch
                    pitch_difference = max(min(pitch_difference, MAX_ROTATION_SPEED), -MAX_ROTATION_SPEED)
                    pitch += pitch_difference
                    cube_rotation.set_from_euler_angles(roll, pitch, yaw)
                elif event.key == pygame.K_RIGHT:
                    roll, pitch, yaw = cube_rotation.euler_angles
                    desired_pitch = pitch + 5  # Para rotar a la derecha
                    pitch_difference = desired_pitch - pitch
                    pitch_difference = max(min(pitch_difference, MAX_ROTATION_SPEED), -MAX_ROTATION_SPEED)
                    pitch += pitch_difference
                    cube_rotation.set_from_euler_angles(roll, pitch, yaw)
                elif event.key == pygame.K_UP:
                    roll, pitch, yaw = cube_rotation.euler_angles
                    desired_roll = roll - 5  # Para rotar hacia arriba
                    roll_difference = desired_roll - roll
                    roll_difference = max(min(roll_difference, MAX_ROTATION_SPEED), -MAX_ROTATION_SPEED)
                    roll += roll_difference
                    cube_rotation.set_from_euler_angles(roll, pitch, yaw)
                elif event.key == pygame.K_DOWN:
                    roll, pitch, yaw = cube_rotation.euler_angles
                    desired_roll = roll + 5  # Para rotar hacia abajo
                    roll_difference = desired_roll - roll
                    roll_difference = max(min(roll_difference, MAX_ROTATION_SPEED), -MAX_ROTATION_SPEED)
                    roll += roll_difference
                    cube_rotation.set_from_euler_angles(roll, pitch, yaw)
                elif event.key == pygame.K_q:  # Si la tecla 'Q' se presiona
                    controls_window = tk.Tk()
                    controls_window.title("Controls")

                    control1_label = tk.Label(controls_window, text="Si mantienes click izquierdo en la figura y mueves el mouse podras mover la figura")
                    control1_label.pack()

                    control2_label = tk.Label(controls_window, text="Tambien podras mover la figura con las flechas direccionales")
                    control2_label.pack()

                    control3_label = tk.Label(controls_window, text="Presiona 'R' para reiniciar la rotacion de la figura")
                    control3_label.pack()

                    control4_label = tk.Label(controls_window, text="Presiona '1' para cambiar a un cubo")
                    control4_label.pack()

                    control5_label = tk.Label(controls_window, text="Presiona '2' para cambiar a un tetraedro")
                    control5_label.pack()

                    control6_label = tk.Label(controls_window, text="Presiona 'Q' para ver los controles")
                    control6_label.pack()


                    # Agrega mas

                    controls_window.mainloop()
                elif event.key == pygame.K_m:  # Si la tecla 'M' se presiona
                    root = tk.Tk()
                    root.withdraw()  # Oculta la ventana de Tkinter
                    angle_input = simpledialog.askstring("Input", "Enter angle in degrees:", parent=root)
                    x_input = simpledialog.askstring("Input", "Enter x component:", parent=root)
                    y_input = simpledialog.askstring("Input", "Enter y component:", parent=root)
                    z_input = simpledialog.askstring("Input", "Enter z component:", parent=root)
                    angle = float(angle_input)
                    x = float(x_input)
                    y = float(y_input)
                    z = float(z_input)
                    cube_rotation.set_from_euler_principal(angle, x, y, z)
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
                    cube_rotation.set_from_quaternion([w, x, y, z])
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
                    cube_rotation.set_from_euler_angles(x, y, z)
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
                    cube_rotation.set_from_rotation_vector(x, y, z)
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
                    cube_rotation.set_from_rotation_matrix(x)
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
                    mouse_pos = pygame.mouse.get_pos()  # Guarda la posición actual del mouse
                    mouse_delta = (mouse_pos[0] - last_mouse_pos[0], mouse_pos[1] - last_mouse_pos[1])  # Calcula el cambio en la posición del mouse
                    last_mouse_pos = mouse_pos  # Actualiza la última posición del mouse
                    roll, pitch, yaw = cube_rotation.euler_angles
                    roll -= mouse_delta[1]  # Rota el cubo en el eje x
                    pitch -= mouse_delta[0]  # Rota el cubo en el eje y
                    cube_rotation.set_from_euler_angles(roll, pitch, yaw)

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        glRotatef(cube_rotation.euler_angles[0], 1, 0, 0)  # Rota el cubo en el eje x
        glRotatef(cube_rotation.euler_angles[1], 0, 1, 0)  # Rota el cubo en el eje y
        glRotatef(cube_rotation.euler_angles[2], 0, 0, 1)  # Rota el cubo en el eje z

        glLoadIdentity()
        gluPerspective(fov, (display[0]/display[1]), 0.1, 100.0)  # Actualiza el campo de visión
        glTranslatef(0.0, 0.0, -5)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        if current_figure is not None:  # Si hay una figura seleccionada
            glPushMatrix()  # Guarda la matriz de transformación actual
            roll, pitch, yaw = cube_rotation.euler_angles
            glRotatef(roll, 1, 0, 0)  # Rota la figura en el eje x
            glRotatef(pitch, 0, 1, 0)  # Rota la figura en el eje y
            current_figure.draw()  # Dibuja la figura
            glPopMatrix()  # Restaura la matriz de transformación      

        pygame.display.set_caption("Ventana 3D: Presiona Q para ver los controles")

        pygame.display.flip()
        pygame.time.wait(10)

def start_info_window(rotation):
    def update_info_window():
        rotation_label.config(text="Euler Angles: " + str(rotation.euler_angles))

        quaternion_label.config(text="Quaternion: (" + ", ".join(f"{i:.4f}" for i in rotation.quaternion) + ")")

        euler_principal_label.config(text="Euler Principal: (" + ", ".join(f"{i:.4f}" for i in rotation.euler_principal) + ")")

        rotation_matrix_string = '\n'.join(['\t'.join([format(cell, ".4f") for cell in row]) for row in rotation.rotation_matrix])
        rotation_matrix_label.config(text="Rotation Matrix:\n" + rotation_matrix_string)

        rotation_vector_string = ', '.join([format(i[0], ".4f") for i in rotation.rotation_vector])
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

if __name__ == "__main__":
    main()

# def euler_to_quaternion(roll, pitch, yaw):
#     cos_roll_2 = np.cos(roll/2)
#     sin_roll_2 = np.sin(roll/2)
#     cos_pitch_2 = np.cos(pitch/2)
#     sin_pitch_2 = np.sin(pitch/2)
#     cos_yaw_2 = np.cos(yaw/2)
#     sin_yaw_2 = np.sin(yaw/2)

#     qx = sin_roll_2 * cos_pitch_2 * cos_yaw_2 - cos_roll_2 * sin_pitch_2 * sin_yaw_2
#     qy = cos_roll_2 * sin_pitch_2 * cos_yaw_2 + sin_roll_2 * cos_pitch_2 * sin_yaw_2
#     qz = cos_roll_2 * cos_pitch_2 * sin_yaw_2 - sin_roll_2 * sin_pitch_2 * cos_yaw_2
#     qw = cos_roll_2 * cos_pitch_2 * cos_yaw_2 + sin_roll_2 * sin_pitch_2 * sin_yaw_2
#     return [qx, qy, qz, qw]

# def queaternion_to_cube_rotationxy(qx, qy, qz, qw):
#     roll = np.arctan2(2*(qw*qx + qy*qz), 1 - 2*(qx**2 + qy**2))
#     pitch = np.arcsin(2*(qw*qy - qz*qx))
#     yaw = np.arctan2(2*(qw*qz + qx*qy), 1 - 2*(qy**2 + qz**2))
#     return [roll, pitch, yaw]

# def quaternion_to_euler_principal(x, y, z, w):
#     roll = np.arctan2(2*(w*x + y*z), 1 - 2*(x**2 + y**2))
#     pitch = np.arcsin(2*(w*y - z*x))
#     yaw = np.arctan2(2*(w*z + x*y), 1 - 2*(y**2 + z**2))
#     return [roll, pitch, yaw]

# def euler_principal_to_quaternion(roll, pitch, yaw):
#     cos_roll_2 = np.cos(roll/2)
#     sin_roll_2 = np.sin(roll/2)
#     cos_pitch_2 = np.cos(pitch/2)
#     sin_pitch_2 = np.sin(pitch/2)
#     cos_yaw_2 = np.cos(yaw/2)
#     sin_yaw_2 = np.sin(yaw/2)

#     qx = sin_roll_2 * cos_pitch_2 * cos_yaw_2 - cos_roll_2 * sin_pitch_2 * sin_yaw_2
#     qy = cos_roll_2 * sin_pitch_2 * cos_yaw_2 + sin_roll_2 * cos_pitch_2 * sin_yaw_2
#     qz = cos_roll_2 * cos_pitch_2 * sin_yaw_2 - sin_roll_2 * sin_pitch_2 * cos_yaw_2
#     qw = cos_roll_2 * cos_pitch_2 * cos_yaw_2 + sin_roll_2 * sin_pitch_2 * sin_yaw_2
#     return [qx, qy, qz, qw]

# def euler_principal_to_cube_rotationxy(roll, pitch, yaw):
#     roll = np.arctan2(np.sin(roll), np.cos(roll))
#     pitch = np.arctan2(np.sin(pitch), np.cos(pitch))
#     yaw = np.arctan2(np.sin(yaw), np.cos(yaw))
#     return [roll, pitch, yaw]

# def rotation_vector_to_quaternion(x, y, z):
#     theta = np.sqrt(x**2 + y**2 + z**2)
#     qx = x * np.sin(theta/2)/theta
#     qy = y * np.sin(theta/2)/theta
#     qz = z * np.sin(theta/2)/theta
#     qw = np.cos(theta/2)
#     return [qx, qy, qz, qw]

# def euler_to_rotation_matrix(roll, pitch, yaw):
#     R_x = np.array([[1, 0, 0],
#                     [0, np.cos(roll), -np.sin(roll)],
#                     [0, np.sin(roll), np.cos(roll)]])

#     R_y = np.array([[np.cos(pitch), 0, np.sin(pitch)],
#                     [0, 1, 0],
#                     [-np.sin(pitch), 0, np.cos(pitch)]])

#     R_z = np.array([[np.cos(yaw), -np.sin(yaw), 0],
#                     [np.sin(yaw), np.cos(yaw), 0],
#                     [0, 0, 1]])

#     R = np.dot(R_z, np.dot(R_y, R_x))
#     return R

# def rotation_matrix_to_rotation_vector(R):
#     theta = np.arccos((R[0, 0] + R[1, 1] + R[2, 2] - 1)/2)
#     k = 1/(2*np.sin(theta)) * np.array([[R[2, 1] - R[1, 2]],
#                                          [R[0, 2] - R[2, 0]],
#                                          [R[1, 0] - R[0, 1]]])
#     return theta*k

# def rotation_matrix_to_cube_rotationxy(R):
#     roll = np.arctan2(R[2, 1], R[2, 2])
#     pitch = np.arctan2(-R[2, 0], np.sqrt(R[2, 1]**2 + R[2, 2]**2))
#     yaw = np.arctan2(R[1, 0], R[0, 0])
#     return [roll, pitch, yaw]

# def rotation_vector_to_cube_rotationxy(x, y, z):
#     theta = np.sqrt(x**2 + y**2 + z**2)
#     roll = np.arctan2(z, y)
#     pitch = np.arctan2(-z, x)
#     yaw = np.arctan2(y, x)
#     return [roll, pitch, yaw]




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