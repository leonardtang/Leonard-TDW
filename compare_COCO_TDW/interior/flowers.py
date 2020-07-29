from tdw.librarian import ModelLibrarian
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.output_data import Bounds, Images


class ProcGenInteriorDesign(Controller):

    def run(self):
        self.start()
        init_setup_commands = [{"$type": "set_screen_size",
                                "width": 1280,
                                "height": 962},
                               {"$type": "set_render_quality",
                                "render_quality": 5}]
        self.communicate(init_setup_commands)

        # Create an empty room.
        self.load_streamed_scene(scene="tdw_room_2018")

        # Disable physics.
        self.communicate({"$type": "set_gravity",
                          "value": False})

        # Add the avatar.
        self.communicate(TDWUtils.create_avatar(position={"x": 0, "y": 1, "z": 0},
                                                look_at=TDWUtils.array_to_vector3([2, 0.8, -1.5]),
                                                avatar_id="avatar"))

        # self.communicate({"$type": "set_field_of_view",
        #                   "field_of_view": 68.0,
        #                   "avatar_id": "avatar"})

        table_id = self.add_object(model_name="glass_table",
                                   position={"x": 2, "y": 0, "z": -1.5},
                                   library="models_full.json")

        table_bounds = self.get_bounds_data(table_id)
        top = table_bounds.get_top(0)

        self.add_object(model_name="flower_vase_set_2",
                        position={"x": 1.6, "y": top[1], "z": -1.5},
                        library="models_full.json")

        self.add_object(model_name="flower_vase_set_2",
                        position={"x": 2, "y": top[1], "z": -1.5},
                        library="models_full.json")

        self.add_object(model_name="flower_vase_set_2",
                        position={"x": 2.4, "y": top[1], "z": -1.5},
                        library="models_full.json")

        # Enable image capture
        self.communicate({"$type": "set_pass_masks",
                          "avatar_id": "avatar",
                          "pass_masks": ["_img", "_id"]})

        self.communicate({"$type": "send_images",
                          "frequency": "always"})

        scene_data = self.communicate({"$type": "look_at_position",
                                       "avatar_id": "avatar",
                                       "position": TDWUtils.array_to_vector3([2, 0.8, -1.5])})

        images = Images(scene_data[0])
        TDWUtils.save_images(images, "flowers_row", output_directory="replicated_images")

    def get_bounds_data(self, object_id):
        resp = self.communicate({"$type": "send_bounds",
                                 "frequency": "once",
                                 "ids": [object_id]})
        return Bounds(resp[0])


if __name__ == "__main__":
    ProcGenInteriorDesign().run()
