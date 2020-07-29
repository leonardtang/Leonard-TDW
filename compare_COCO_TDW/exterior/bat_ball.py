from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.output_data import Bounds, Images


class ProcGenInteriorDesign(Controller):

    def run(self):
        self.start()
        init_setup_commands = [{"$type": "set_screen_size",
                                "width": 600,
                                "height": 480},
                               {"$type": "set_render_quality",
                                "render_quality": 5}]
        self.communicate(init_setup_commands)

        # Create an empty room.
        self.communicate(TDWUtils.create_empty_room(8, 8))
        # Disable physics.
        self.communicate({"$type": "set_gravity",
                          "value": False})

        # Add the avatar.
        self.communicate(TDWUtils.create_avatar(position={"x": 0, "y": 0.5, "z": 1.3},
                                                look_at=TDWUtils.array_to_vector3([0.1, 0.2, 2.5]),
                                                avatar_id="avatar"))

        # self.communicate({"$type": "set_field_of_view",
        #                   "field_of_view": 68.0,
        #                   "avatar_id": "avatar"})

        self.add_object(model_name="b06_cat_1",
                        position={"x": -0.2, "y": 0, "z": 3.0},
                        rotation={"x": 0, "y": 159, "z": 0},
                        library="models_full.json")

        self.add_object(model_name="labrador_retriever_puppy",
                        position={"x": 0.25, "y": 0, "z": 2.8},
                        rotation={"x": 0, "y": 30, "z": 0},
                        library="models_full.json")

        self.add_object(model_name="baseball2014",
                        position={"x": 0.17, "y": 0, "z": 2.5},
                        rotation={"x": 0, "y": 0, "z": 0},
                        library="models_full.json")

        self.add_object(model_name="baseballs",
                        position={"x": -0.14, "y": 0, "z": 2.6},
                        rotation={"x": 0, "y": 23, "z": 0},
                        library="models_full.json")


        # Enable image capture
        self.communicate({"$type": "set_pass_masks",
                          "avatar_id": "avatar",
                          "pass_masks": ["_img", "_id"]})

        self.communicate({"$type": "send_images",
                          "frequency": "always"})

        scene_data = self.communicate({"$type": "look_at_position",
                                       "avatar_id": "avatar",
                                       "position": TDWUtils.array_to_vector3([0.1, 0.2, 2.5])})

        images = Images(scene_data[0])
        TDWUtils.save_images(images, "dog_cat", output_directory="/Users/leonard/Desktop/TDWBase-1.5.0/Python/Leonard/compare_COCO_TDW/replicated_images/interior")

    def get_bounds_data(self, object_id):
        resp = self.communicate({"$type": "send_bounds",
                                 "frequency": "once",
                                 "ids": [object_id]})
        return Bounds(resp[0])


if __name__ == "__main__":
    ProcGenInteriorDesign().run()
