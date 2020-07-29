from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import SceneLibrarian
from tdw.output_data import Images
import time
import os
import shutil

# Quaternions, Euler angles, directional vectors
# Pitch (x), yaw (y), roll (z); possible that x and z are swapped


class RotatingBowl(Controller):
    def run(self):
        # Setting up image directory
        output_directory = "rotating_guitar_images"
        parent_dir = '/Users/leonard/Desktop/TDWBase-1.5.0/Python/Leonard/rotating_guitar'
        path = os.path.join(parent_dir, output_directory)
        print(path)
        if os.path.exists(path):
            shutil.rmtree(path)
            time.sleep(0.5)
            os.mkdir(path)

        # Initialize scene
        self.start()

        init_setup_commands = [{"$type": "set_screen_size",
                                "width": 1280,
                                "height": 962},
                               {"$type": "set_render_quality",
                                "render_quality": 5}]
        self.communicate(init_setup_commands)

        scene_lib = SceneLibrarian()
        scene_record = scene_lib.get_record("tdw_room_2018")
        self.communicate({"$type": "add_scene",
                          "name": scene_record.name,
                          "url": scene_record.get_url()})

        self.communicate({"$type": "set_gravity",
                          "value": True})
        self.communicate({"$type": "simulate_physics",
                          "value": True})

        self.communicate(TDWUtils.create_avatar(
            avatar_id="avatar",
            position={"x": 3, "y": 1.5, "z": 3},
            look_at={"x": 0, "y": 0.8, "z": 0}))

        guitar_id = self.add_object(model_name="b01_shovel",
                                    position={"x": 0, "y": 1, "z": 0},
                                    rotation={"x": 0, "y": 0, "z": 0},
                                    library="models_full.json")

        self.communicate({"$type": "rotate_object_by",
                          "angle": -15.0,
                          "id": guitar_id,
                          "axis": "roll",
                          "is_world": True})

        self.communicate({"$type": "set_pass_masks",
                          "avatar_id": "avatar",
                          "pass_masks": ["_img", "_id"]})
        self.communicate({"$type": "send_images",
                          "frequency": "always"})

        for i in range(50):
            resp = self.communicate({"$type": "look_at_position",
                                     "avatar_id": "avatar",
                                     "position": {"x": 0, "y": 0.8, "z": 0}})
            images = Images(resp[0])
            TDWUtils.save_images(images, TDWUtils.zero_padding(i), output_directory=path)


if __name__ == "__main__":
    RotatingBowl().run()




