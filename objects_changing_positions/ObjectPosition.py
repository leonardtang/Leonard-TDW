from typing import Dict, List


class ObjectPosition:
    """
    Defines the initial position of an object.
    """
    def __init__(self, position: Dict[str, float], obj_radius: float):
        """
        :param position: The position of the object.
        :param obj_radius: The maximum radius swept by the object's bounds.
        """
        self.position = position
        self.obj_radius = obj_radius
