from tdw.librarian import MaterialLibrarian
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

        lib = MaterialLibrarian(library="materials_med.json")
        record = lib.get_record("parquet_wood_mahogany")
        self.communicate({"$type": "add_material", "name": "parquet_wood_mahogany", "url": record.get_url()})
        self.communicate({"$type": "set_proc_gen_floor_material", "name": "parquet_wood_mahogany"})

        # Add the avatar.
        self.communicate(TDWUtils.create_avatar(position={"x": -1, "y": 1.4, "z": -1},
                                                look_at=TDWUtils.array_to_vector3([-0.1, 0.7, -0.1]),
                                                avatar_id="avatar"))

        self.communicate({"$type": "set_field_of_view",
                          "field_of_view": 68.0,
                          "avatar_id": "avatar"})

        table_id = self.add_object(model_name="b03_restoration_hardware_pedestal_salvaged_round_tables",
                                   position={"x": 0, "y": 0, "z": 0},
                                   library="models_full.json")

        table_bounds = self.get_bounds_data(table_id)
        top = table_bounds.get_top(0)

        self.add_object(model_name="club_sandwich",
                        position={"x": 0.45, "y": top[1], "z": 0.25},
                        rotation={"x": 0, "y": 30, "z": 0},
                        library="models_full.json")

        self.add_object(model_name="coffeemug",
                        position={"x": 0.03, "y": top[1], "z": 0.03},
                        library="models_full.json")

        self.add_object(model_name="knife3",
                        position={"x": -0.17, "y": top[1], "z": 0.15},
                        rotation={"x": 0, "y": 24, "z": 90},
                        library="models_full.json")

        self.add_object(model_name="notes_02",
                        position={"x": 0.17, "y": top[1], "z": -0.12},
                        rotation={"x": 0, "y": 24, "z": 0},
                        library="models_full.json")


        # Enable image capture
        self.communicate({"$type": "set_pass_masks",
                          "avatar_id": "avatar",
                          "pass_masks": ["_img", "_id"]})

        self.communicate({"$type": "send_images",
                          "frequency": "always"})

        scene_data = self.communicate({"$type": "look_at_position",
                                       "avatar_id": "avatar",
                                       "position": TDWUtils.array_to_vector3([-0.1, 0.7, -0.1])})

        images = Images(scene_data[0])
        TDWUtils.save_images(images, "sadnwich2", output_directory="/Users/leonard/Desktop/TDWBase-1.5.0/Python/Leonard/compare_COCO_TDW/replicated_images/interior")

    def get_bounds_data(self, object_id):
        resp = self.communicate({"$type": "send_bounds",
                                 "frequency": "once",
                                 "ids": [object_id]})
        return Bounds(resp[0])


if __name__ == "__main__":
    ProcGenInteriorDesign().run()
