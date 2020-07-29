from tdw.librarian import ModelLibrarian, MaterialLibrarian
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

        lib = MaterialLibrarian(library="materials_med.json")
        record = lib.get_record("laser_cut_white_norway_spruce")
        self.communicate({"$type": "add_material", "name": "laser_cut_white_norway_spruce", "url": record.get_url()})
        self.communicate({"$type": "set_proc_gen_floor_material", "name": "laser_cut_white_norway_spruce"})

        # Add the avatar.
        self.communicate(TDWUtils.create_avatar(position={"x": 1.5, "y": 1.6, "z": 0},
                                                look_at=TDWUtils.array_to_vector3([0, 0.5, 0]),
                                                avatar_id="avatar"))

        self.communicate({"$type": "set_field_of_view",
                          "field_of_view": 68.0,
                          "avatar_id": "avatar"})

        table = self.add_object(model_name="boconcept_lugo_dining_table_vray1.5",
                                position={"x": 0, "y": 0, "z": 0.0},
                                rotation={"x": 0, "y": -90, "z": 0},
                                library="models_full.json")

        table_bounds = self.get_bounds_data(table)

        top = table_bounds.get_top(0)
        self.add_object(model_name='macbook_001',
                        position={"x": 0, "y": top[1], "z": 0.1},
                        rotation={"x": 0, "y": 90, "z": 0},
                        library="models_full.json")

        self.add_object(model_name='spunlight_designermesh_lamp',
                        position={"x": -0.19, "y": top[1], "z": -0.4},
                        rotation={"x": 0, "y": 0, "z": 0},
                        library="models_full.json")

        self.add_object(model_name="apple_magic_mouse_2_(2015)_vray",
                        position={"x": 0, "y": top[1], "z": 0.32},
                        rotation={"x": 0, "y": 86, "z": 0},
                        library="models_full.json")

        self.add_object(model_name="f10_apple_iphone_4",
                        position={"x": 0.14, "y": top[1], "z": -0.3},
                        rotation={"x": 0, "y": 12, "z": 0},
                        library="models_full.json")

        # Enable image capture
        self.communicate({"$type": "set_pass_masks",
                          "avatar_id": "avatar",
                          "pass_masks": ["_img", "_id"]})

        self.communicate({"$type": "send_images",
                          "frequency": "always"})

        scene_data = self.communicate({"$type": "look_at_position",
                                       "avatar_id": "avatar",
                                       "position": TDWUtils.array_to_vector3([0, 0.5, 0])})

        images = Images(scene_data[0])
        TDWUtils.save_images(images, "phone", output_directory="/Users/leonard/Desktop/TDWBase-1.5.0/Python/Leonard/compare_COCO_TDW/replicated_images/interior")

    def get_bounds_data(self, object_id):
        resp = self.communicate({"$type": "send_bounds",
                                 "frequency": "once",
                                 "ids": [object_id]})
        return Bounds(resp[0])


if __name__ == "__main__":
    ProcGenInteriorDesign().run()
