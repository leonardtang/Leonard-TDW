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
        self.communicate(TDWUtils.create_empty_room(32, 32))
        # Disable physics.
        self.communicate({"$type": "set_gravity",
                          "value": False})

        # Add the avatar.
        self.communicate(TDWUtils.create_avatar(position={"x": -1.5, "y": 1.5, "z": -15},
                                                look_at=TDWUtils.array_to_vector3([-1.7, 0.7, -2.3]),
                                                avatar_id="avatar"))

        lib = MaterialLibrarian(library="materials_med.json")
        record = lib.get_record("concrete_chipped_cracked")
        self.communicate({"$type": "add_material", "name": "concrete_chipped_cracked", "url": record.get_url()})
        self.communicate({"$type": "set_proc_gen_floor_material", "name": "concrete_chipped_cracked"})
        # self.communicate({"$type": "set_proc_gen_walls_material", "name": "concrete"})

        self.communicate({"$type": "set_field_of_view",
                          "field_of_view": 68.0,
                          "avatar_id": "avatar"})

        bus = self.add_object(model_name="b06_bus_new",
                              position={"x": -2, "y": 0, "z": 0},
                              rotation={"x": 0, "y": -70, "z": 0},
                              library="models_full.json")

        bus_bounds = self.get_bounds_data(bus)
        bus_front = bus_bounds.get_front(0)
        print(bus_front)

        self.add_object(model_name="3dscan_man_004",
                        position={"x": -3.7, "y": 0, "z": -7.3},
                        rotation={"x": 0, "y": 0, "z": 0},
                        library="models_full.json")

        # Enable image capture
        self.communicate({"$type": "set_pass_masks",
                          "avatar_id": "avatar",
                          "pass_masks": ["_img", "_id"]})

        self.communicate({"$type": "send_images",
                          "frequency": "always"})

        scene_data = self.communicate({"$type": "look_at_position",
                                       "avatar_id": "avatar",
                                       "position": TDWUtils.array_to_vector3([-1.7, 0.7, -2.3])})

        images = Images(scene_data[0])
        TDWUtils.save_images(images, "bus",
                             output_directory="/Users/leonard/Desktop/TDWBase-1.5.0/Python/Leonard/compare_COCO_TDW/replicated_images/exterior")

    def get_bounds_data(self, object_id):
        resp = self.communicate({"$type": "send_bounds",
                                 "frequency": "once",
                                 "ids": [object_id]})
        return Bounds(resp[0])


if __name__ == "__main__":
    ProcGenInteriorDesign().run()
