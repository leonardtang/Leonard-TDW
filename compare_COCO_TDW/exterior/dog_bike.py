import numpy as np
import random
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.output_data import Bounds, Transforms, Images

"""
Procedurally furnish a room with basic relational semantic rules.
"""


class ProcGenInteriorDesign(Controller):

    def run(self):
        self.start()
        init_setup_commands = [{"$type": "set_screen_size",
                                "width": 600,
                                "height": 480},
                               {"$type": "set_render_quality",
                                "render_quality": 5}]
        self.communicate(init_setup_commands)

        width = 8
        length = 8

        # Create an empty room.
        self.load_streamed_scene("box_room_2018")

        # Disable physics.
        self.communicate({"$type": "set_gravity",
                          "value": False})

        # Add the avatar.
        self.communicate(TDWUtils.create_avatar(position={"x": 0, "y": 1.7, "z": 0},
                                                look_at={"x": 0.3, "y": 0.8, "z": 2.2},
                                                avatar_id="avatar"))

        self.communicate({"$type": "set_field_of_view",
                          "field_of_view": 68.0,
                          "avatar_id": "avatar"})

        self.add_object(model_name="b06_bikenew",
                        position={"x": 0.3, "y": 0, "z": 2.2},
                        rotation={"x": 0, "y": 180, "z": 0},
                        library="models_full.json")

        self.add_object(model_name="animal_dog_rtsit_1280",
                        position={"x": 0.35, "y": 0, "z": 1.8},
                        library="models_full.json")

        # Enable image capture
        self.communicate({"$type": "set_pass_masks",
                          "avatar_id": "avatar",
                          "pass_masks": ["_img", "_id"]})

        self.communicate({"$type": "send_images",
                          "frequency": "always"})

        scene_data = self.communicate({"$type": "look_at_position",
                                       "avatar_id": "avatar",
                                       "position": {"x": 0.3, "y": 0.8, "z": 2.2}})

        images = Images(scene_data[0])
        TDWUtils.save_images(images, "dog_bike", output_directory="replicated_images/interior")

    def get_bounds_data(self, object_id):
        resp = self.communicate({"$type": "send_bounds",
                                 "frequency": "once",
                                 "ids": [object_id]})
        return Bounds(resp[0])


if __name__ == "__main__":
    ProcGenInteriorDesign().run()
