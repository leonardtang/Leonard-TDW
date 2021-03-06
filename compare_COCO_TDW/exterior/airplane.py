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

        # Create an empty scene (no walls)
        self.communicate({"$type": "create_empty_environment",
                          "center": {"x": 0, "y": 0, "z": 0},
                          "bounds": {"x": 30, "y": 30, "z": 30}})

        self.communicate(self.get_add_hdri_skybox("pink_sunrise_4k"))

        cube = self.communicate({"$type": "load_primitive_from_resources",
                                 "primitive_type": "Cube",
                                 "id": 1,
                                 "position": {"x": 0, "y": 0, "z": 0},
                                 "orientation": {"x": 0, "y": 0, "z": 0}})
        self.communicate({"$type": "scale_object",
                          "scale_factor": {"x": 30, "y": 0.0001, "z": 30},
                          "id": 1})
        lib = MaterialLibrarian(library="materials_med.json")
        record = lib.get_record("concrete_chipped_cracked")
        self.communicate({"$type": "add_material", "name": "concrete_chipped_cracked", "url": record.get_url()})

        # self.communicate({"$type": "set_visual_material",
        #                   "material_index": 1,
        #                   "material_name": "concrete_chipped_cracked",
        #                   "object_name": "cube",
        #                   "id": 1})
        # Disable physics.
        self.communicate({"$type": "set_gravity",
                          "value": False})

        # Add the avatar.
        self.communicate(TDWUtils.create_avatar(position={"x": -13, "y": 1.5, "z": 0},
                                                look_at=TDWUtils.array_to_vector3([5, 1.5, 0]),
                                                avatar_id="avatar"))

        self.communicate({"$type": "set_field_of_view",
                          "field_of_view": 68.0,
                          "avatar_id": "avatar"})

        self.add_object(model_name="spitfire_2012",
                        position={"x": 0, "y": 0, "z": 2},
                        rotation={"x": 0, "y": 90, "z": 0},
                        library="models_full.json")

        self.add_object(model_name="b03_topkicktruck",
                        position={"x": -7, "y": 0, "z": -5},
                        rotation={"x": 0, "y": 0, "z": 0},
                        library="models_full.json")

        self.add_object(model_name="3dscan_man_012",
                        position={"x": -4, "y": 0, "z": 3},
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
                                       "position": TDWUtils.array_to_vector3([5, 1.5, 0])})

        images = Images(scene_data[0])
        TDWUtils.save_images(images, "airplane",
                             output_directory="/Users/leonard/Desktop/TDWBase-1.5.0/Python/Leonard/compare_COCO_TDW/replicated_images/exterior")

    def get_bounds_data(self, object_id):
        resp = self.communicate({"$type": "send_bounds",
                                 "frequency": "once",
                                 "ids": [object_id]})
        return Bounds(resp[0])


if __name__ == "__main__":
    ProcGenInteriorDesign().run()
