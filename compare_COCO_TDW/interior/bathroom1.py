from tdw.librarian import ModelLibrarian
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.output_data import Bounds, Images


class ProcGenInteriorDesign(Controller):

    def run(self):
        self.start()
        init_setup_commands = [{"$type": "set_screen_size",
                                "width": 640,
                                "height": 480},
                               {"$type": "set_render_quality",
                                "render_quality": 5}]
        self.communicate(init_setup_commands)

        self.communicate(TDWUtils.create_empty_room(8, 8))

        # Disable physics.
        self.communicate({"$type": "set_gravity",
                          "value": False})

        # Add the avatar.
        self.communicate(TDWUtils.create_avatar(position={"x": 0.75, "y": 1, "z": 0},
                                                look_at=TDWUtils.array_to_vector3([3, 0.7, 0]),
                                                avatar_id="avatar"))

        # self.communicate({"$type": "set_field_of_view",
        #                   "field_of_view": 68.0,
        #                   "avatar_id": "avatar"})

        self.add_object(model_name="12_01_001",
                        position={"x": 3, "y": 0, "z": -0.35},
                        rotation={"x": 0, "y": 90, "z": 0},
                        library="models_full.json")

        sink = self.add_object(model_name="cgaxis_models_22_33_vray",
                               position={"x": 3, "y": 0, "z": 0.35},
                               rotation={"x": 0, "y": -90, "z": 0},
                               library="models_full.json")

        record = ModelLibrarian(library='models_full.json').get_record("b03_simpsons_london_-_round_hudson_mirror")
        self.communicate({"$type": "add_object",
                          "name": "b05_tv1970",
                          "url": record.get_url(),
                          "scale_factor": 0.5,
                          "position": {"x": 3, "y": 0.6, "z": 0.35},
                          "rotation": {"x": 0, "y": -90, "z": 0},
                          "category": record.wcategory,
                          "id": self.get_unique_id()})

        sink_bounds = self.get_bounds_data(sink)

        top = sink_bounds.get_top(0)
        self.add_object(model_name="808409_toothbrush",
                        position={"x": 3, "y": top[1] - 0.217, "z": 0.7},
                        rotation={"x": -20, "y": -40, "z": 90},
                        library="models_full.json")

        # Enable image capture
        self.communicate({"$type": "set_pass_masks",
                          "avatar_id": "avatar",
                          "pass_masks": ["_img", "_id"]})

        self.communicate({"$type": "send_images",
                          "frequency": "always"})

        scene_data = self.communicate({"$type": "look_at_position",
                                       "avatar_id": "avatar",
                                       "position": TDWUtils.array_to_vector3([3, 0.7, 0])})

        images = Images(scene_data[0])

        TDWUtils.save_images(images, "bathroom1", output_directory="replicated_images")

    def get_bounds_data(self, object_id):
        resp = self.communicate({"$type": "send_bounds",
                                 "frequency": "once",
                                 "ids": [object_id]})
        return Bounds(resp[0])


if __name__ == "__main__":
    ProcGenInteriorDesign().run()
