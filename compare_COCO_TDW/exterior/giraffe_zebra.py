from tdw.librarian import ModelLibrarian
from tdw.librarian import MaterialLibrarian
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

        self.communicate({"$type": "create_empty_environment",
                          "center": {"x": 0, "y": 0, "z": 0},
                          "bounds": {"x": 30, "y": 30, "z": 30}})

        # Disable physics.
        self.communicate({"$type": "set_gravity",
                          "value": False})

        # Add the avatar.
        self.communicate(TDWUtils.create_avatar(position={"x": -8, "y": 1.7, "z": 0},
                                                look_at=TDWUtils.array_to_vector3([0, 1, 0]),
                                                avatar_id="avatar"))

        self.communicate(self.get_add_hdri_skybox("table_mountain_1_4k"))
        self.communicate({"$type": "rotate_hdri_skybox_by", "angle": 90})

        self.communicate({"$type": "set_field_of_view",
                          "field_of_view": 68.0,
                          "avatar_id": "avatar"})

        cube_record = ModelLibrarian("models_special.json").get_record("prim_cube")
        self.communicate({"$type": "add_object",
                          "name": "prim_cube",
                          "url": cube_record.get_url(),
                          "scale_factor": cube_record.scale_factor,
                          "position": {"x": 0, "y": 0, "z": 0},
                          "rotation": {"x": 0, "y": 0, "z": 0},
                          "category": cube_record.wcategory,
                          "id": 1})

        self.communicate({"$type": "scale_object",
                          "scale_factor": {"x": 30, "y": 0.0001, "z": 30},
                          "id": 1})

        grass_record = MaterialLibrarian("materials_high.json").get_record("grass_countryside")
        self.communicate({"$type": "add_material", "name": "grass_countryside", "url": grass_record.get_url()})
        self.communicate(TDWUtils.set_visual_material(c=self, substructure=cube_record.substructure, object_id=1,
                                                      material="grass_countryside"))

        self.add_object(model_name="b03_giraffe",
                        position={"x": 1.2, "y": 0.0001, "z": 2.4},
                        rotation={"x": 0, "y": 193, "z": 0},
                        library="models_full.json")

        self.add_object(model_name="b03_zebra",
                        position={"x": -3.3, "y": 0.0001, "z": -1.6},
                        rotation={"x": 0, "y": 13, "z": 0},
                        library="models_full.json")

        self.add_object(model_name="b03_zebra",
                        position={"x": 0, "y": 0.001, "z": 0.7},
                        rotation={"x": 0, "y": -190, "z": 0},
                        library="models_full.json")

        # Enable image capture
        self.communicate({"$type": "set_pass_masks",
                          "avatar_id": "avatar",
                          "pass_masks": ["_img", "_id"]})

        self.communicate({"$type": "send_images",
                          "frequency": "always"})

        scene_data = self.communicate({"$type": "look_at_position",
                                       "avatar_id": "avatar",
                                       "position": TDWUtils.array_to_vector3([0, 1, 0])})

        images = Images(scene_data[0])
        TDWUtils.save_images(images, "giraffe_zebra",
                             output_directory="/Users/leonard/Desktop/TDWBase-1.5.0/Python/Leonard/compare_COCO_TDW/replicated_images/exterior")

    def load_material(self, material):
        return self.communicate({"$type": "add_material",
                                 "name": material[0],
                                 "url": material[2]})

    def get_bounds_data(self, object_id):
        resp = self.communicate({"$type": "send_bounds",
                                 "frequency": "once",
                                 "ids": [object_id]})
        return Bounds(resp[0])


if __name__ == "__main__":
    ProcGenInteriorDesign().run()
