import pyray as pr
import numpy as np
from pyray import Vector3

from tp1_functions import *
from basic_drawing_functions import *
from mesh_functions import *

def rotation_matrix_homogeneous(axis, theta):
    """Génère une matrice homogène de rotation autour d'un axe arbitraire (4x4)."""
    axis = vector_normalize(axis)
    nx, ny, nz = axis.x, axis.y, axis.z
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)
    
    # Rodrigues' rotation formula: R = I*cos(θ) + (1-cos(θ))*n⊗n + K*sin(θ)
    I = np.eye(3)
    n = np.array([nx, ny, nz])
    outer_product = np.outer(n, n)
    
    # Cross-product matrix K
    K = np.array([
        [0, -nz, ny],
        [nz, 0, -nx],
        [-ny, nx, 0]
    ])
    
    # 3x3 rotation matrix
    R3 = I * cos_theta + (1 - cos_theta) * outer_product + K * sin_theta
    
    # Convert to 4x4 homogeneous matrix
    R4 = np.eye(4)
    R4[:3, :3] = R3
    
    return R4

def scaling_matrix_homogeneous(axis, k):
    """Génère une matrice homogène de mise à l'échelle le long d'un axe arbitraire (4x4)."""
    axis = vector_normalize(axis)
    nx, ny, nz = axis.x, axis.y, axis.z
    
    # Scaling along arbitrary axis: S = I + (k-1)*n⊗n
    I = np.eye(3)
    n = np.array([nx, ny, nz])
    outer_product = np.outer(n, n)
    
    # 3x3 scaling matrix
    S3 = I + (k - 1) * outer_product
    
    # Convert to 4x4 homogeneous matrix
    S4 = np.eye(4)
    S4[:3, :3] = S3
    
    return S4

def translation_matrix(tx, ty, tz):
    """Génère une matrice homogène de translation (4x4)."""
    T = np.eye(4)
    T[0, 3] = tx
    T[1, 3] = ty
    T[2, 3] = tz
    return T

def orthographic_projection_matrix_homogeneous(axis):
    """Génère une matrice homogène de projection orthographique sur un plan normal à un axe donné (4x4)."""
    axis = vector_normalize(axis)
    nx, ny, nz = axis.x, axis.y, axis.z
    
    # Orthographic projection onto plane perpendicular to axis: P = I - n⊗n
    I = np.eye(3)
    n = np.array([nx, ny, nz])
    outer_product = np.outer(n, n)
    
    # 3x3 projection matrix
    P3 = I - outer_product
    
    # Convert to 4x4 homogeneous matrix
    P4 = np.eye(4)
    P4[:3, :3] = P3
    
    return P4

def perspective_projection_matrix(d):
    """Génère une matrice homogène de projection en perspective avec une distance focale d."""
    P = np.eye(4)
    P[3, 2] = 1.0 / d  # Perspective division component
    return P

def apply_transformations_homogeneous(mesh, translation_mat, rotation_mat, scaling_mat, projection_mat):
    """Applique les transformations de rotation, de mise à l'échelle et de projection aux sommets du mesh en utilisant des matrices 4x4."""
    vertices_homogeneous = np.hstack((mesh.original_vertices, np.ones((mesh.original_vertices.shape[0], 1))))
    transformed_vertices = vertices_homogeneous @ translation_mat.T @ rotation_mat.T @ scaling_mat.T @ projection_mat.T
    mesh.vertices = transformed_vertices[:, :3] / transformed_vertices[:, 3, np.newaxis]  # Revenir aux coordonnées 3D

def initialize_mesh_for_transforming(mesh):
    """Stocke les sommets originaux du mesh pour permettre un redimensionnement dynamique."""
    mesh.original_vertices = np.copy(mesh.vertices)

def main():
    pr.init_window(1000, 900, "Visionneuse 3D avec contrôle de rotation, de mise à l'échelle et de projection")
    pr.set_window_min_size(800, 600)
    camera = initialize_camera()
    pr.set_target_fps(60)
    movement_speed = 0.1

    # Chargement du mesh et initialisation des transformations
    ply_file_path = "cube.ply"
    mesh = load_ply_file(ply_file_path)
    initialize_mesh_for_transforming(mesh)

    # Contrôles d'interface pour les transformations et translations
    scale_factor_ptr = pr.ffi.new('float *', 1.0)
    angle_ptr = pr.ffi.new('float *', 0.0)
    axis_x_ptr = pr.ffi.new('float *', 1.0)
    axis_y_ptr = pr.ffi.new('float *', 0.0)
    axis_z_ptr = pr.ffi.new('float *', 0.0)
    translate_x_ptr = pr.ffi.new('float *', 0.0)
    translate_y_ptr = pr.ffi.new('float *', 0.0)
    translate_z_ptr = pr.ffi.new('float *', 0.0)
    
    d_ptr = pr.ffi.new('float *', 1.0)       # Paramètre de distance pour la projection en perspective
    projection_type_ptr = pr.ffi.new('float *', -1)  # Valeur par défaut (aucune projection)

    while not pr.window_should_close():
        update_camera_position(camera, movement_speed)
        
        pr.begin_drawing()
        pr.clear_background(pr.RAYWHITE)
        pr.begin_mode_3d(camera)
        
        axis = Vector3(axis_x_ptr[0], axis_y_ptr[0], axis_z_ptr[0])
        angle = angle_ptr[0]
        scale_factor = scale_factor_ptr[0]
        
        # Création des matrices de transformation
        rotation_mat = rotation_matrix_homogeneous(axis, np.radians(angle))
        scaling_mat = scaling_matrix_homogeneous(axis, scale_factor)
        
        # Choix de la projection
        projection_mat = np.eye(4)
        if projection_type_ptr[0] > -1 and projection_type_ptr[0] < 1:
            projection_mat = orthographic_projection_matrix_homogeneous(axis)
        elif projection_type_ptr[0] == 1:
            projection_mat = perspective_projection_matrix(d_ptr[0])
        
        # Dessin des axes et du mesh
        draw_coordinate_axes(Vector3(0, 0, 0), scale=3)
        draw_transformation_axis(Vector3(0, 0, 0), axis, scale=3)

        tx = translate_x_ptr[0]
        ty = translate_y_ptr[0]
        tz = translate_z_ptr[0]
        translation_mat = translation_matrix(tx, ty, tz)
        
        apply_transformations_homogeneous(mesh, translation_mat, rotation_mat, scaling_mat, projection_mat)
        
        draw_plane(axis, 10)
        draw_mesh(mesh)
        pr.end_mode_3d()

        # GUI de contrôle pour les transformations
        pr.draw_text("Échelle:", 750, 50, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(750, 80, 200, 20), "0.5", "10", scale_factor_ptr, 0.4, 10.0)
        pr.draw_text("Angle (degrés):", 750, 110, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(750, 140, 200, 20), "0", "360", angle_ptr, 0.0, 360.0)
        
        pr.draw_text("Axe de transformation X:", 750, 170, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(750, 200, 200, 20), "-1.0", "1.0", axis_x_ptr, -1.0, 1.0)
        pr.draw_text("Axe de transformation Y:", 750, 230, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(750, 260, 200, 20), "-1.0", "1.0", axis_y_ptr, -1.0, 1.0)
        pr.draw_text("Axe de transformation Z:", 750, 290, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(750, 320, 200, 20), "-1.0", "1.0", axis_z_ptr, -1.0, 1.0)

        # Contrôles de translation
        pr.draw_text("Translation X:", 750, 350, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(750, 380, 200, 20), "-5.0", "5.0", translate_x_ptr, -5.0, 5.0)
        pr.draw_text("Translation Y:", 750, 410, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(750, 440, 200, 20), "-5.0", "5.0", translate_y_ptr, -5.0, 5.0)
        pr.draw_text("Translation Z:", 750, 470, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(750, 500, 200, 20), "-5.0", "5.0", translate_z_ptr, -5.0, 5.0)

        # Ajout d'un espace avant les contrôles de projection
        pr.draw_text("Type de projection:", 750, 550, 20, pr.BLACK)
        pr.gui_slider_bar(pr.Rectangle(750, 580, 200, 20), "-1", "1", projection_type_ptr, -1.0, 1.0)

        # Contrôle de la distance de projection pour la perspective
        if projection_type_ptr[0] == 1:
            pr.draw_text("Distance de projection:", 750, 610, 20, pr.BLACK)
            pr.gui_slider_bar(pr.Rectangle(750, 640, 200, 20), "1.0", "8.0", d_ptr, 1.0, 8.0)

        pr.end_drawing()

    pr.close_window()

if __name__ == "__main__":
    main()