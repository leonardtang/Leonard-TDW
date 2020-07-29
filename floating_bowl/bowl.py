from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import SceneLibrarian
from tdw.output_data import Images
import time
import os
import shutil


class MultipleObjects(Controller):
    def run(self):
        # Setting up image directory
        output_directory = "floating_bowl_images"
        parent_dir = '/Users/leonard/Desktop/TDWBase-1.5.0/Python/Leonard/floating_bowl'
        path = os.path.join(parent_dir, output_directory)
        print(path)
        if os.path.exists(path):
            shutil.rmtree(path)
            time.sleep(0.5)
            os.mkdir(path)

        # Initialize scene
        self.start()

        # Load in scene
        scene_lib = SceneLibrarian()
        scene_record = scene_lib.get_record("tdw_room_2018")
        self.communicate({"$type": "add_scene",
                          "name": scene_record.name,
                          "url": scene_record.get_url()})

        # Resize screen; note render_quality 5 is best
        self.communicate([{"$type": "set_screen_size",
                           "width": 1280,
                           "height": 962},
                          {"$type": "set_render_quality",
                           "render_quality": 2}])

        # Toggle physics
        physics_on = True
        self.communicate({"$type": "simulate_physics",
                          "value": physics_on})

        # Load in avatar
        self.communicate(TDWUtils.create_avatar(avatar_id="avatar",
                                                position={"x": 3, "y": 1.5, "z": 3},
                                                look_at={"x": 0, "y": 0.8, "z": 0}))

        # Necessary commands to avoid error in calling save_images()
        # Second command enables image capture
        self.communicate({"$type": "set_pass_masks",
                          "avatar_id": "avatar",
                          "pass_masks": ["_img", "_id"]})
        self.communicate({"$type": "send_images",
                          "frequency": "always"})

        # Capture images
        for i in range(20):
            bowl_id = self.add_object(model_name="b04_bowl_smooth",
                                      position={"x": 0, "y": i / 10, "z": 0},
                                      rotation={"x": i * 30 / 10, "y": i / 10, "z": 0},
                                      library="models_full.json")

            resp = self.communicate({"$type": "look_at_position",
                                     "avatar_id": "avatar",
                                     "position": {"x": 0, "y": 0.8, "z": 0}})
            images = Images(resp[0])
            TDWUtils.save_images(images, TDWUtils.zero_padding(i), output_directory=path)

            self.communicate({"$type": "destroy_object",
                              "id": bowl_id})


if __name__ == "__main__":
    MultipleObjects().run()
