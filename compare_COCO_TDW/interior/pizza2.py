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

        self.communicate(TDWUtils.create_empty_room(8, 8))

        # Disable physics.
        self.communicate({"$type": "set_gravity",
                          "value": False})

        # Add the avatar.
        self.communicate(TDWUtils.create_avatar(position={"x": 0, "y": 1.4, "z": 3},
                                                look_at=TDWUtils.array_to_vector3([0, 0.5, 0]),
                                                avatar_id="avatar"))

        self.communicate({"$type": "set_field_of_view",
                          "field_of_view": 68.0,
                          "avatar_id": "avatar"})

        table_record = ModelLibrarian(library="models_full.json").get_record("restoration_hardware_salvaged_tables")
        table = self.add_object(model_name="restoration_hardware_salvaged_tables",
                                position={"x": 0, "y": 0, "z": 0},
                                rotation={"x": 0, "y": -90, "z": 0},
                                library="models_full.json")

        table_bounds = self.get_bounds_data(table)
        left = table_bounds.get_left(0)
        self.add_object(model_name="3dscan_man_002",
                        position={"x": 1.6, "y": 0, "z": left[2]},
                        rotation={"x": 0, "y": 124, "z": 0},
                        library="models_full.json")

        top = table_bounds.get_top(0)
        cup_record = ModelLibrarian(library="models_full.json").get_record("cup")
        self.communicate({"$type": "add_object",
                          "name": "cup",
                          "url": cup_record.get_url(),
                          "scale_factor": cup_record.scale_factor,
                          "position": {"x": 0, "y": top[1], "z": -0.07},
                          "rotation": {"x": 0, "y": -90, "z": 0},
                          "category": cup_record.wcategory,
                          "id": 1})

        # record = MaterialLibrarian(library='materials_high.json').get_record("polystyrene_foam")
        self.communicate({"$type": "add_material",
                          "name": "polystyrene_foam",
                          "url": "http://s3.amazonaws.com/tdw_test_dev/materials/osx/high/polystyrene_foam"})

        for sub_object in cup_record.substructure:
            for j in range(len(sub_object)):
                self.communicate({"$type": "set_visual_material",
                                  "material_index": j,
                                  "material_name": "polystyrene_foam",
                                  "object_name": sub_object["name"],
                                  "id": 1})

        self.communicate({"$type": "add_object",
                          "name": "cup",
                          "url": cup_record.get_url(),
                          "scale_factor": cup_record.scale_factor,
                          "position": {"x": -0.3, "y": top[1], "z": 0.1},
                          "rotation": {"x": 0, "y": -90, "z": 0},
                          "category": cup_record.wcategory,
                          "id": 2})

        for sub_object in cup_record.substructure:
            for j in range(len(sub_object)):
                self.communicate({"$type": "set_visual_material",
                                  "material_index": j,
                                  "material_name": "polystyrene_foam",
                                  "object_name": sub_object["name"],
                                  "id": 2})

        self.add_object(model_name='neopolitan_pizza',
                        position={"x": 0.7, "y": top[1], "z": 0},
                        rotation={"x": 0, "y": -22, "z": 0},
                        library="models_full.json")

        self.add_object(model_name='stua_onda_stool_max2012',
                        position={"x": -1.4, "y": 0, "z": 0},
                        rotation={"x": 0, "y": 90, "z": 0},
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
        TDWUtils.save_images(images, "pizza2",
                             output_directory="/Users/leonard/Desktop/TDWBase-1.5.0/Python/Leonard/compare_COCO_TDW/replicated_images/interior")

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
