from pyray import Vector3
import math

def cross_product(A, B):
    """Calcule le produit croisé entre deux vecteurs A et B."""
    return Vector3(
        A.y*B.z - A.z*B.y, 
        A.z*B.x - A.x*B.z, 
        A.x*B.y - A.y*B.x 
    )

def vector_length(vector):
    """Calcule la longueur d'un vecteur."""
    return math.sqrt(dot_product(vector, vector))

def vector_normalize(vector):
    """Normalise un vecteur pour obtenir un vecteur de longueur 1."""
    length = vector_length(vector)
    if length==0: 
        return vector
    return Vector3(vector.x/length,vector.y/length,vector.z/length)


def dot_product(A, B):
    """Calcule le produit scalaire entre deux vecteurs A et B."""
    return A.x*B.x + A.y*B.y + A.z*B.z
