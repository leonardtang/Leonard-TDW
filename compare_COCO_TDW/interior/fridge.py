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
        self.communicate(TDWUtils.create_avatar(position={"x": 2, "y": 1.5, "z": 0},
                                                look_at=TDWUtils.array_to_vector3([2, 0.8, -4]),
                                                avatar_id="avatar"))

        self.communicate({"$type": "set_field_of_view",
                          "field_of_view": 68.0,
                          "avatar_id": "avatar"})

        self.add_object(model_name="kenmore_refr_74049",
                        position={"x": 3, "y": 0, "z": -4},
                        rotation={"x": 0, "y": 90, "z": 0},
                        library="models_full.json")

        record = ModelLibrarian(library='models_full.json').get_record("b03_bosch_cbg675bs1b_2013__vray_composite")
        self.communicate({"$type": "add_object",
                          "name": "b03_bosch_cbg675bs1b_2013__vray_composite",
                          "url": record.get_url(),
                          "scale_factor": 1.5,
                          "position": {"x": 2, "y": 0, "z": -4},
                          "category": record.wcategory,
                          "id": self.get_unique_id()})

        table_id = self.add_object(model_name="b03_restoration_hardware_pedestal_salvaged_round_tables",
                                   position={"x": 1, "y": 0, "z": -4},
                                   library="models_full.json")

        table_bounds = self.get_bounds_data(table_id)
        top = table_bounds.get_top(0)

        self.add_object(model_name="cgaxis_models_65_06_vray",
                        position={"x": 1.2, "y": top[1], "z": -4.2},
                        library="models_full.json")

        self.add_object(model_name="b04_heineken_beer_vray",
                        position={"x": 0.77, "y": top[1], "z": -3.9},
                        library="models_full.json")

        self.add_object(model_name="b03_backpack",
                        position={"x": 1.3, "y": 0, "z": -3.7},
                        rotation={"x": 0, "y": 20, "z": 0},
                        library="models_full.json")

        # Enable image capture
        self.communicate({"$type": "set_pass_masks",
                          "avatar_id": "avatar",
                          "pass_masks": ["_img", "_id"]})

        self.communicate({"$type": "send_images",
                          "frequency": "always"})

        scene_data = self.communicate({"$type": "look_at_position",
                                       "avatar_id": "avatar",
                                       "position": TDWUtils.array_to_vector3([2, 0.8, -4])})

        images = Images(scene_data[0])

        TDWUtils.save_images(images, "fridge", output_directory="replicated_images")

    def get_bounds_data(self, object_id):
        resp = self.communicate({"$type": "send_bounds",
                                 "frequency": "once",
                                 "ids": [object_id]})
        return Bounds(resp[0])


if __name__ == "__main__":
    ProcGenInteriorDesign().run()
