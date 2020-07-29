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
                          "bounds": {"x": 15, "y": 15, "z": 15}})

        # Disable physics.
        self.communicate({"$type": "set_gravity",
                          "value": False})

        # Add the avatar.
        self.communicate(TDWUtils.create_avatar(position={"x": -1.5, "y": 1.4, "z": 0.6},
                                                look_at=TDWUtils.array_to_vector3([3, 0.5, 0.5]),
                                                avatar_id="avatar"))

        self.communicate(self.get_add_hdri_skybox("table_mountain_1_4k"))

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

        self.add_object(model_name="b03_horse",
                        position={"x": 3, "y": 0.0001, "z": 0.5},
                        rotation={"x": 0, "y": 0, "z": 0},
                        library="models_full.json")

        bird = self.add_object(model_name="polysurface63",
                               position={"x": 1.2, "y": 0.0001, "z": 1},
                               rotation={"x": 0, "y": 0, "z": 0},
                               library="models_full.json")

        self.communicate({"$type": "scale_object",
                          "scale_factor": {"x": 2, "y": 2, "z": 2},
                          "id": bird})

        bird = self.add_object(model_name="b03_realistic_pigeon_max",
                               position={"x": 1.8, "y": 0.0001, "z": 0.45},
                               rotation={"x": 0, "y": -95, "z": 0},
                               library="models_full.json")

        self.communicate({"$type": "scale_object",
                          "scale_factor": {"x": 2, "y": 2, "z": 2},
                          "id": bird})

        bird = self.add_object(model_name="rockdove_polysurface77",
                               position={"x": 1, "y": 0.0001, "z": 0.7},
                               rotation={"x": 0, "y": -80, "z": 0},
                               library="models_full.json")

        self.communicate({"$type": "scale_object",
                          "scale_factor": {"x": 2, "y": 2, "z": 2},
                          "id": bird})

        # Enable image capture
        self.communicate({"$type": "set_pass_masks",
                          "avatar_id": "avatar",
                          "pass_masks": ["_img", "_id"]})

        self.communicate({"$type": "send_images",
                          "frequency": "always"})

        scene_data = self.communicate({"$type": "look_at_position",
                                       "avatar_id": "avatar",
                                       "position": TDWUtils.array_to_vector3([3, 0.5, 0])})

        images = Images(scene_data[0])
        TDWUtils.save_images(images, "bird2",
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
