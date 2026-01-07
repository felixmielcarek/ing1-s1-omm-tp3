import pyray as pr
from pyray import Vector3

from tp1_functions import *

def initialize_camera():
    """Initialise la caméra 3D."""
    camera = pr.Camera3D(
        Vector3(0, 10, 10),  # position
        Vector3(0, 0, 0),    # cible
        Vector3(0, 1, 0),    # haut
        45,                  # fovy (champ de vision dans la direction y)
        pr.CAMERA_PERSPECTIVE
    )
    return camera

def update_camera_position(camera, movement_speed):
    """Met à jour la position de la caméra en fonction des touches pressées."""
    if pr.is_key_down(pr.KEY_W):
        camera.position.z -= movement_speed
    if pr.is_key_down(pr.KEY_S):
        camera.position.z += movement_speed
    if pr.is_key_down(pr.KEY_A):
        camera.position.x -= movement_speed
    if pr.is_key_down(pr.KEY_D):
        camera.position.x += movement_speed
    if pr.is_key_down(pr.KEY_Q):
        camera.position.y += movement_speed
    if pr.is_key_down(pr.KEY_E):
        camera.position.y -= movement_speed

def draw_vector_3(start, end, color, thickness=0.05, head_size_factor=0.8):
    """Dessine un vecteur en utilisant un cylindre et un cône."""
    direction = Vector3(end.x - start.x, end.y - start.y, end.z - start.z)
    length = vector_length(direction)
    head_size = length * head_size_factor
    
    n_direction = vector_normalize(direction)
    
    arrow_start = Vector3(start.x + n_direction.x * head_size, 
                          start.y + n_direction.y * head_size, 
                          start.z + n_direction.z * head_size)
    
    pr.draw_cylinder_ex(start, end, thickness / 2, thickness / 2, 8, color)
    pr.draw_cylinder_ex(arrow_start, end, thickness * 2, thickness / 5, 8, color)

def draw_plane(axis, size=5, color=pr.GRAY):
    """Dessine un plan basé sur un vecteur normal et une taille."""
    axis = vector_normalize(axis)
    orthogonal_vector = Vector3(1, 0, 0) if abs(axis.x) < abs(axis.y) else Vector3(0, 1, 0)
    v1 = cross_product(axis, orthogonal_vector)
    v2 = cross_product(axis, v1)

    for i in range(-size, size + 1):
        start1 = Vector3(v1.x * -size + v2.x * i, v1.y * -size + v2.y * i, v1.z * -size + v2.z * i)
        end1 = Vector3(v1.x * size + v2.x * i, v1.y * size + v2.y * i, v1.z * size + v2.z * i)
        start2 = Vector3(v2.x * -size + v1.x * i, v2.y * -size + v1.y * i, v2.z * -size + v1.z * i)
        end2 = Vector3(v2.x * size + v1.x * i, v2.y * size + v1.y * i, v2.z * size + v1.z * i)
        
        pr.draw_line_3d(start1, end1, color)
        pr.draw_line_3d(start2, end2, color)

def draw_coordinate_axes(origin, scale=3):
    """Dessine les axes de coordonnées standard X, Y, Z à partir de l'origine."""
    # X-axis (Rouge)
    draw_vector_3(origin, Vector3(origin.x + scale, origin.y, origin.z), pr.RED, thickness=0.05)
    
    # Y-axis (Vert)
    draw_vector_3(origin, Vector3(origin.x, origin.y + scale, origin.z), pr.GREEN, thickness=0.05)
    
    # Z-axis (Bleu)
    draw_vector_3(origin, Vector3(origin.x, origin.y, origin.z + scale), pr.BLUE, thickness=0.05)

def draw_transformation_axis(origin, axis, scale=3):
    """Dessine l'axe de transformation personnalisé à partir de l'origine dans la direction de l'axe donné."""
    # Mettre à l'échelle le vecteur d'axe pour la visualisation
    scaled_axis = Vector3(origin.x + axis.x * scale, origin.y + axis.y * scale, origin.z + axis.z * scale)
    draw_vector_3(origin, scaled_axis, pr.PURPLE, thickness=0.05)