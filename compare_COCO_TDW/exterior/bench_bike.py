import cv2
from tdw.librarian import MaterialLibrarian
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.output_data import Bounds, Images, SegmentationColors, OutputData
import numpy as np
import pandas as pd


def get_COCO(val, my_dict):
    for key, value in my_dict.items():
        if val in value:
            return key


class ProcGenInteriorDesign(Controller):

    def run(self):
        self.start()
        init_setup_commands = [{"$type": "set_screen_size",
                                "width": 600,
                                "height": 480},
                               {"$type": "set_render_quality",
                                "render_quality": 5}]
        self.communicate(init_setup_commands)

        self.communicate(self.get_add_hdri_skybox("industrial_sunset_4k"))

        # Create an empty room.
        self.communicate(TDWUtils.create_empty_room(8, 8))
        # Disable physics.
        self.communicate({"$type": "set_gravity",
                          "value": False})

        # Add the avatar.
        self.communicate(TDWUtils.create_avatar(position={"x": 1, "y": 1.5, "z": 0.3},
                                                look_at=TDWUtils.array_to_vector3([2.5, 0.5, 0.5]),
                                                avatar_id="avatar"))

        lib = MaterialLibrarian(library="materials_med.json")
        record = lib.get_record("concrete_049")
        self.communicate({"$type": "add_material", "name": "concrete_049", "url": record.get_url()})
        self.communicate({"$type": "set_proc_gen_floor_material", "name": "concrete_049"})
        # self.communicate({"$type": "set_proc_gen_walls_material", "name": "concrete"})

        # self.communicate({"$type": "set_field_of_view",
        #                   "field_of_view": 68.0,
        #                   "avatar_id": "avatar"})

        bench = self.add_object(model_name="cgaxis_models_51_19_01",
                                position={"x": 2.5, "y": 0, "z": 0.5},
                                rotation={"x": 0, "y": 90, "z": 0},
                                library="models_full.json")

        bench_bounds = self.get_bounds_data(bench)
        top = bench_bounds.get_top(0)

        self.add_object(model_name="b05_cat_model_3dmax2012",
                        position={"x": 2.5, "y": top[1], "z": 0.2},
                        rotation={"x": 0, "y": 0, "z": 0},
                        library="models_full.json")

        self.add_object(model_name="azor",
                        position={"x": 3, "y": 0, "z": 0.5},
                        rotation={"x": 0, "y": 90, "z": 0},
                        library="models_full.json")

        """ Post-scene construction """

        # Enable image capture
        self.communicate({"$type": "set_pass_masks",
                          "avatar_id": "avatar",
                          "pass_masks": ["_id"]})

        scene_data = self.communicate({"$type": "look_at_position",
                                       "avatar_id": "avatar",
                                       "position": TDWUtils.array_to_vector3([3, 0.5, 0.5])})

        # images = Images(scene_data[0])
        im = cv2.imread("/Users/leonard/Desktop/TDWBase-1.5.0/Python/Leonard/"
                        "compare_COCO_TDW/replicated_images/exterior/id_bench_bike.png")
        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)

        # WRITE THIS TO JSON!
        segmentation_data = []
        COCO_to_TDW = pd.read_csv('/Users/leonard/Desktop/coco/COCO_to_TDW.csv', header=None, index_col=0, squeeze=True).to_dict()

        segmentation_colors = self.communicate({"$type": "send_segmentation_colors", "frequency": "once"})
        for r in segmentation_colors[:-1]:
            r_id = OutputData.get_data_type_id(r)
            if r_id == "segm":
                s = SegmentationColors(r)
                for i in range(s.get_num()):
                    name = s.get_object_name(i)
                    category = get_COCO(name, COCO_to_TDW)

                    color = s.get_object_color(i)
                    indices = np.where(im != 0)  # Segmentation pixels
                    print(color)
                    print(indices)
                    print(im[indices[0][0]])   # some random RGB val -- MUSt match one of the 3
                    segmentation_data.append([indices, category])

        # TDWUtils.save_images(images, "bench_bike",
        #                      output_directory="/Users/leonard/Desktop/TDWBase-1.5.0/Python/Leonard/compare_COCO_TDW/replicated_images/exterior")

        # Consider using zip() to clean up coordinates

        return segmentation_data

    def get_bounds_data(self, object_id):
        resp = self.communicate({"$type": "send_bounds",
                                 "frequency": "once",
                                 "ids": [object_id]})
        return Bounds(resp[0])


if __name__ == "__main__":
    segmentation_masks = ProcGenInteriorDesign().run()
    print(segmentation_masks)
