from tdw.librarian import ModelLibrarian
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
        self.load_streamed_scene(scene="tdw_room_2018")

        # Disable physics.
        self.communicate({"$type": "set_gravity",
                          "value": False})

        # Add the avatar.
        self.communicate(TDWUtils.create_avatar(position={"x": -0.8, "y": 1.6, "z": 0.6},
                                                look_at=TDWUtils.array_to_vector3([0, 0.4, 0]),
                                                avatar_id="avatar"))

        # self.communicate({"$type": "set_field_of_view",
        #                   "field_of_view": 68.0,
        #                   "avatar_id": "avatar"})

        table_id = self.add_object(model_name="glass_table_round",
                                   position={"x": 0, "y": 0, "z": 0},
                                   library="models_full.json")

        table_bounds = self.get_bounds_data(table_id)
        top = table_bounds.get_top(0)

        self.add_object(model_name="b03_orange",
                        position={"x": 0, "y": top[1], "z": 0},
                        library="models_full.json")

        position = TDWUtils.get_random_point_in_circle([0, 0, 0], 0.17)
        position[1] = top[1]
        self.add_object(model_name="b03_orange",
                        position={"x": 0, "y": top[1], "z": 0},
                        library="models_full.json")

        position = TDWUtils.get_random_point_in_circle([0, 0, 0], 0.4)
        position[1] = top[1]
        self.add_object(model_name="b04_banana",
                        position=TDWUtils.array_to_vector3(position),
                        rotation={"x": 0, "y": 40, "z": 0},
                        library="models_full.json")

        position = TDWUtils.get_random_point_in_circle([0, 0, 0], 0.4)
        position[1] = top[1]
        self.add_object(model_name="b04_banana",
                        position=TDWUtils.array_to_vector3(position),
                        library="models_full.json")

        position = TDWUtils.get_random_point_in_circle([0, 0, 0], 0.5)
        position[1] = top[1]
        self.add_object(model_name="red_apple",
                        position=TDWUtils.array_to_vector3(position),
                        library="models_full.json")

        position = TDWUtils.get_random_point_in_circle([0, 0, 0], 0.6)
        position[1] = top[1]
        self.add_object(model_name="vk0076_fruitfork",
                        position=TDWUtils.array_to_vector3(position),
                        library="models_full.json")

        # Enable image capture
        self.communicate({"$type": "set_pass_masks",
                          "avatar_id": "avatar",
                          "pass_masks": ["_img", "_id"]})

        self.communicate({"$type": "send_images",
                          "frequency": "always"})

        scene_data = self.communicate({"$type": "look_at_position",
                                       "avatar_id": "avatar",
                                       "position": TDWUtils.array_to_vector3([0, 0.4, 0])})

        images = Images(scene_data[0])
        TDWUtils.save_images(images, "fruit_table", output_directory="/Users/leonard/Desktop/TDWBase-1.5.0/Python/Leonard/compare_COCO_TDW/replicated_images/interior")

    def get_bounds_data(self, object_id):
        resp = self.communicate({"$type": "send_bounds",
                                 "frequency": "once",
                                 "ids": [object_id]})
        return Bounds(resp[0])


if __name__ == "__main__":
    ProcGenInteriorDesign().run()
