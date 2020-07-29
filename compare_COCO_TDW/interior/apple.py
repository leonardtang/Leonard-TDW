import random
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.output_data import Bounds, Transforms, Images


class ProcGenInteriorDesign(Controller):

    DINING_TABLE = ["willisau_varion_w3_table"]

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
        self.communicate(TDWUtils.create_avatar(position={"x": 0.9, "y": 1.5, "z": 0.9},
                                                look_at=TDWUtils.array_to_vector3([0, 0.8, 0]),
                                                avatar_id="avatar"))

        # Create the dining table.
        self.dining_table()

    def get_transforms_data(self, object_ids):
        resp = self.communicate({"$type": "send_transforms",
                                 "frequency": "once",
                                 "ids": object_ids})

        transforms = Transforms(resp[0])
        return transforms

    def get_bounds_data(self, object_id):
        resp = self.communicate({"$type": "send_bounds",
                                 "frequency": "once",
                                 "ids": [object_id]})
        return Bounds(resp[0])

    def random_rotation(self, object_ids, max_angle=45):
        commands = []
        for object_id in object_ids:
            commands.append({"$type": "rotate_object_by",
                             "angle": random.uniform(-max_angle, max_angle),
                             "axis": "yaw",
                             "id": object_id,
                             "is_world": True})
        self.communicate(commands)

    def dining_table(self):
        """
        1. Create a dining table in the center of the room.
        2. Create four chairs, one on each side of the table.
        3. Create "table settings" in front of each chair on the table.
        4. Create a centerpiece on the table.
        """

        # Create a dining table in the center of the room.
        dining_table_id = self.add_object(random.choice(ProcGenInteriorDesign.DINING_TABLE))

        # Get the table bounds.
        dining_table_bounds = self.get_bounds_data(dining_table_id)

        top = dining_table_bounds.get_top(0)
        setting_ids = []

        # Add apple
        setting_id = self.add_object(model_name="apple07(8_vray)",
                                     position={"x": top[0], "y": top[1], "z": top[2]},
                                     library="models_full.json")
        setting_ids.append(setting_id)

        # Add vase 1
        position = [top[0] - 0.125, 0, top[2] + 0.134]
        position[1] = top[1]
        self.add_object(model_name="vase_03",
                        position=TDWUtils.array_to_vector3(position),
                        library="models_full.json")

        # Add vase 2
        position = [top[0] + 0.245, 0, top[2] + 0.234]
        position[1] = top[1]
        self.add_object(model_name="vase_06",
                        position=TDWUtils.array_to_vector3(position),
                        library="models_full.json")
        #
        # """ Destroying select objects for generating segmentations """
        # """ ---------------------------- """
        #
        # self.communicate([{"$type": "destroy_object",
        #                    "id": dining_table_id}])

        # Enable image capture
        self.communicate({"$type": "set_pass_masks",
                          "avatar_id": "avatar",
                          "pass_masks": ["_img"]})

        self.communicate({"$type": "send_images",
                          "frequency": "always"})

        scene_data = self.communicate({"$type": "look_at_position",
                                       "avatar_id": "avatar",
                                       "position": TDWUtils.array_to_vector3([0, 0.8, 0])})
        images = Images(scene_data[0])

        TDWUtils.save_images(images, "apple_seg_4", output_directory="../replicated_images/segmentation")


if __name__ == "__main__":
    ProcGenInteriorDesign().run()
