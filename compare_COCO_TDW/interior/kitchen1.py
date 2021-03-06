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
        self.communicate(TDWUtils.create_avatar(position={"x": -3.75, "y": 1.7, "z": -5.5},
                                                look_at=TDWUtils.array_to_vector3([-3.75, 1.5, -10]),
                                                avatar_id="avatar"))

        self.communicate({"$type": "set_field_of_view",
                          "field_of_view": 78.0,
                          "avatar_id": "avatar"})

        self.add_object(model_name="b03_ka90ivi20r_2013__vray",
                        position={"x": -5.5, "y": 0, "z": -9},
                        rotation={"x": 0, "y": 90, "z": 0},
                        library="models_full.json")

        table_id = self.add_object(model_name="quatre_dining_table",
                                   position={"x": -3, "y": 0, "z": -9},
                                   rotation={"x": 0, "y": 90, "z": 0},
                                   library="models_full.json")

        table_bounds = self.get_bounds_data(table_id)
        top = table_bounds.get_top(0)

        self.add_object(model_name="stua_onda_stool_max2012",
                        position={"x": -3, "y": 0, "z": -10},
                        library="models_full.json")

        self.add_object(model_name="stua_onda_stool_max2012",
                        position={"x": -3, "y": 0, "z": -8},
                        rotation={"x": 0, "y": 180, "z": 0},
                        library="models_full.json")

        # Enable image capture
        self.communicate({"$type": "set_pass_masks",
                          "avatar_id": "avatar",
                          "pass_masks": ["_img", "_id"]})

        self.communicate({"$type": "send_images",
                          "frequency": "always"})

        scene_data = self.communicate({"$type": "look_at_position",
                                       "avatar_id": "avatar",
                                       "position": TDWUtils.array_to_vector3([-3.75, 1.5, -10])})

        images = Images(scene_data[0])
        TDWUtils.save_images(images, "kitchen1", output_directory="replicated_images")

    def get_bounds_data(self, object_id):
        resp = self.communicate({"$type": "send_bounds",
                                 "frequency": "once",
                                 "ids": [object_id]})
        return Bounds(resp[0])


if __name__ == "__main__":
    ProcGenInteriorDesign().run()
