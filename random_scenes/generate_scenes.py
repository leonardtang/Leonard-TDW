from ObjectPosition import ObjectPosition
from scipy.spatial import distance
import sys
from sys import platform
if platform == "linux":
    sys.path.append("/home/leonard/Desktop/Kreiman-Lab/Python/tdw")
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import SceneLibrarian, ModelLibrarian
from tdw.output_data import Images, OutputData, Environments, Bounds
from typing import List, Dict, Tuple
import numpy as np
import time
import random
import os
import shutil
import csv
import math


models_list = "/Users/leonard/Desktop/TDWBase-1.5.0/Python/Leonard/json_list/models_list.csv"
models = []
materials_list = "/Users/leonard/Desktop/TDWBase-1.5.0/Python/Leonard/json_list/materials_list.csv"
materials = []
scenes_list = "/Users/leonard/Desktop/TDWBase-1.5.0/Python/Leonard/json_list/scenes_list.csv"
scenes = []
path = ""


class GenerateScenes(Controller):

    @staticmethod
    def get_lists():
        with open(models_list) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                models.append(row)

        with open(materials_list) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                materials.append(row)

        with open(scenes_list) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                scenes.append(row)

    @staticmethod
    def set_dir():
        # Setting up image directory
        output_directory = "random_scene_images"
        parent_dir = '/Users/leonard/Desktop/TDWBase-1.5.0/Python/Leonard/random_scenes'
        global path
        path = os.path.join(parent_dir, output_directory)
        print(path)
        if os.path.exists(path):
            shutil.rmtree(path)
            time.sleep(0.5)
            os.mkdir(path)

    # In case we don't want to use computationally intensive scenes
    # def create(self):
    #     c.start()
    #     c.communicate(TDWUtils.create_empty_room(20, 20))

    def load_material(self, material):

        return self.communicate({"$type": "add_material",
                                 "name": material[0],
                                 "url": material[2]})

    @staticmethod
    def _get_object_position(scene_dimensions: List[Tuple], object_positions: List[ObjectPosition],
                             object_to_add_radius: float, max_tries: int = 1000, location_radius: float = 2) -> \
            Dict[str, float]:
        """
        Try to get a valid random position that doesn't interpenetrate with other objects.
        :param object_positions: The positions and radii of all objects so far that will be added to the scene.
        :param max_tries: Try this many times to get a valid position before giving up.
        :param location_radius: The radius to pick a position in.
        :return: A valid position that doesn't interpenetrate with other objects.
        """

        o_pos = TDWUtils.get_random_point_in_circle(center=np.array([random.uniform(-0.9 * scene_dimensions[1][0] / 2,
                                                                                    0.9 * scene_dimensions[1][0] / 2),
                                                                     0,
                                                                     random.uniform(-0.9 * scene_dimensions[1][2] / 2,
                                                                                    0.9 * scene_dimensions[1][2] / 2)]),
                                                    radius=location_radius)
        # Scale circular point --> elliptic point for non-square rooms
        # Width > Depth of scene
        if scene_dimensions[1][0] > scene_dimensions[1][2]:
            o_pos[0] = o_pos[0] * scene_dimensions[1][0] / scene_dimensions[1][2]
        # Depth > Width of scene
        else:
            o_pos[2] = o_pos[2] * scene_dimensions[1][2] / scene_dimensions[1][0]

        # Set height value
        o_pos[1] = random.uniform(0, 0.9 * scene_dimensions[1][1] / 3)
        o_pos = TDWUtils.array_to_vector3(o_pos)
        print("O_Pos:", o_pos)

        # Pick a position away from other objects.
        ok = False
        count = 0
        while not ok and count < max_tries:
            count += 1
            ok = True
            for o in object_positions:
                # If the object is too close to another object, try another position.
                # Also check that object bounds are generated within reasonable viewing window
                # Check Radius of old objects as well
                if (TDWUtils.get_distance(o.position, o_pos) <= 1.1 * o.obj_radius or
                        TDWUtils.get_distance(o.position, o_pos) <= 1.1 * object_to_add_radius or
                        o_pos["x"] < -0.9 * scene_dimensions[1][0] / 2 or
                        o_pos["x"] > 0.8 * scene_dimensions[1][0] / 2 or
                        o_pos["y"] < 0 or
                        o_pos["y"] > scene_dimensions[1][1] / 2 or
                        o_pos["z"] < -0.8 * scene_dimensions[1][2] / 2 or
                        o_pos["z"] > 0.8 * scene_dimensions[1][2] / 2):
                    ok = False
                    o_pos = TDWUtils.get_random_point_in_circle(center=np.array([
                                                                     random.uniform(-0.9 * scene_dimensions[1][0] / 2
                                                                                    , 0.9 * scene_dimensions[1][0] / 2),
                                                                     0,
                                                                     random.uniform(-0.9 * scene_dimensions[1][2] / 2
                                                                                    , 0.9 * scene_dimensions[1][2] / 2)]),
                                                                radius=location_radius)
                    # Scale circular point --> elliptic point for non-square rooms
                    # Width > Depth of scene
                    if scene_dimensions[1][0] > scene_dimensions[1][2]:
                        o_pos[0] = o_pos[0] * scene_dimensions[1][0] / scene_dimensions[1][2]
                    # Depth > Width of scene
                    else:
                        o_pos[2] = o_pos[2] * scene_dimensions[1][2] / scene_dimensions[1][0]

                    o_pos[1] = random.uniform(0, 0.9 * scene_dimensions[1][1])
                    o_pos = TDWUtils.array_to_vector3(o_pos)
                    print("O_Pos:", o_pos)
        return [ok, o_pos]

    def run(self):
        self.start()
        positions_list = []  # Stores current model locations and radii
        scene_dimensions = []  # Store scene/environment dimensions
        init_setup_commands = [{"$type": "set_screen_size",
                                "width": 1280,
                                "height": 962},
                               {"$type": "set_render_quality",
                                "render_quality": 5}]
        self.communicate(init_setup_commands)

        scene_lib = SceneLibrarian()
        # Disable physics when adding in new objects (objects float)
        self.communicate({"$type": "simulate_physics",
                          "value": False})

        for scene in scenes[1:]:
            # Load in scene
            print("Scene", scene[0])
            if scene[3] == "interior" and scene[0] == "box_room_2018":
                self.start()
                scene_record = scene_lib.get_record(scene[0])
                self.communicate({"$type": "add_scene",
                                  "name": scene_record.name,
                                  "url": scene_record.get_url()})

                # Gets dimensions of environments (e.g. inside, outside) in the scene
                # This command returns environment data in the form of a list of serialized byte arrays
                scene_bytes = self.communicate({"$type": "send_environments",
                                                "frequency": "once"})

                # Iterating through data and parsing byte array
                # Ignoring the last element (the frame count)
                for b in scene_bytes[:-1]:
                    e = Environments(b)
                    for i in range(e.get_num()):
                        center = e.get_center(i)
                        bounds = e.get_bounds(i)
                        env_id = e.get_id(i)
                    scene_dimensions = [center, bounds, env_id]  # Center, bounds are tuples

                # Must come before set_pass_masks
                avatar_position = TDWUtils.array_to_vector3([0.9 * scene_dimensions[1][0] / 2,
                                                             scene_dimensions[1][1] / 2,
                                                             0])
                print("Avatar Position:", avatar_position)
                self.communicate(TDWUtils.create_avatar(avatar_id="avatar",
                                                        position=avatar_position,
                                                        look_at={"x": 0,
                                                                 "y": scene_dimensions[0][1] / 2,
                                                                 "z": 0}))
                # Set collision mode
                self.communicate({"$type": "set_avatar_collision_detection_mode",
                                  "mode": "continuous_speculative",
                                  "avatar_id": "avatar"})

                # Alter FOV
                self.communicate({"$type": "set_field_of_view",
                                  "field_of_view": 80,
                                  "avatar_id": "avatar"})

                # Gets rid of header (Model: Category)
                objects = models[1:]
                random.shuffle(objects)
                obj_count = 0
                obj_overlaps = 0  # Number of failed attempts to place object due to over-dense objects area
                while obj_count < 30 and obj_overlaps < 5:
                    # Need to have random position for Bounds Data to return meaningful info
                    valid_obj_pos = {"x": random.uniform(-1 * scene_dimensions[1][0] / 2,
                                                         0.5 * scene_dimensions[1][0] / 2),
                                     "y": scene_dimensions[1][1] / 4,
                                     "z": random.uniform(-0.9 * scene_dimensions[1][2] / 2,
                                                         0.9 * scene_dimensions[1][2] / 2)}

                    # Add in the object at random position
                    # Object will later be removed or updated accordingly after performing collision calculations
                    record = ModelLibrarian(library="models_full.json").get_record(objects[obj_count][0])
                    self.communicate({"$type": "add_object",
                                      "name": objects[obj_count][0],
                                      "url": record.get_url(),
                                      "scale_factor": record.scale_factor,
                                      "position": valid_obj_pos,
                                      "rotation": {"x": 0, "y": 0, "z": 0},
                                      "category": record.wcategory,
                                      "id": obj_count})

                    # Returns bound data for added object
                    bounds_data = self.communicate({"$type": "send_bounds",
                                                    "frequency": "once"})

                    # Appends object, with information on position and obj_radius, to positions_list
                    # Length of buffer array should be 1
                    print("Bounds Data:", bounds_data)
                    for b in bounds_data[:-1]:
                        print("Buffer Loop:", b)
                        b_id = OutputData.get_data_type_id(b)
                        if b_id == "boun":
                            print("BOUNDS")
                            o = Bounds(b)
                            print("# of Objects:", o.get_num())
                            print("# of Failed Attempts:", obj_overlaps)
                            print("Buffer Array:", b)
                            print("Bounds Object:", o)
                            for i in range(o.get_num()):
                                print("Object ID:", o.get_id(i))
                                print("obj_count:", obj_count)
                                print("Object:", objects[obj_count][0], "Category:", objects[obj_count][1])
                                print("Object Center:", o.get_center(i))
                                # Only want to compute valid_position for object we are about to add
                                # Skip any computation if this is not the case
                                if o.get_id(i) != obj_count:
                                    continue
                                # Useful for detecting if object fits in environment
                                print("Calculating if object fits in environment")
                                width = distance.euclidean(o.get_left(i), o.get_right(i))
                                depth = distance.euclidean(o.get_front(i), o.get_back(i))
                                height = distance.euclidean(o.get_top(i), o.get_bottom(i))
                                print("Width:", width)
                                print("Depth:", depth)
                                print("Height:", height)

                                # Useful for avoiding object overlap
                                print("Calculating Object Bounds")
                                center_to_top = distance.euclidean(o.get_center(i), o.get_top(i))
                                center_to_bottom = distance.euclidean(o.get_center(i), o.get_bottom(i))
                                center_to_left = distance.euclidean(o.get_center(i), o.get_left(i))
                                center_to_right = distance.euclidean(o.get_center(i), o.get_right(i))
                                center_to_front = distance.euclidean(o.get_center(i), o.get_front(i))
                                center_to_back = distance.euclidean(o.get_center(i), o.get_back(i))
                                # Max object radius (center to diagonal of bounding box)
                                obj_radius = \
                                    max(math.sqrt(center_to_top ** 2 + center_to_left ** 2 + center_to_front ** 2),
                                        math.sqrt(center_to_top ** 2 + center_to_right ** 2 + center_to_front ** 2),
                                        math.sqrt(center_to_top ** 2 + center_to_left ** 2 + center_to_back ** 2),
                                        math.sqrt(center_to_top ** 2 + center_to_right ** 2 + center_to_back ** 2),
                                        math.sqrt(center_to_bottom ** 2 + center_to_left ** 2 + center_to_front ** 2),
                                        math.sqrt(center_to_bottom ** 2 + center_to_right ** 2 + center_to_front ** 2),
                                        math.sqrt(center_to_bottom ** 2 + center_to_left ** 2 + center_to_back ** 2),
                                        math.sqrt(center_to_bottom ** 2 + center_to_right ** 2 + center_to_back ** 2))

                                print("Obj_Radius:", obj_radius)

                                # Set sweeping radius, based on scene plane dimensions
                                l_radius = random.uniform(0, min(0.9 * scene_dimensions[1][0] / 2,
                                                                 0.9 * scene_dimensions[1][2] / 2))

                                # Checking that object fits in scene viewing
                                if (width > min(0.7 * scene_dimensions[1][0], 0.7 * scene_dimensions[1][2]) or
                                        depth > min(0.7 * scene_dimensions[1][0], 0.7 * scene_dimensions[1][2]) or
                                        height > 0.7 * scene_dimensions[1][1]):

                                    print("Object does not fit in scene")
                                    self.communicate([{"$type": "send_images",
                                                       "frequency": "never"},
                                                      {"$type": "destroy_object",
                                                       "id": obj_count}])
                                    # Ensures next attempt to load in item is not the same item as before
                                    random.shuffle(objects)
                                    break

                                # Not possible to find valid object position -- too many overlapping objects
                                elif (not self._get_object_position(scene_dimensions=scene_dimensions,
                                                                    object_positions=positions_list,
                                                                    object_to_add_radius=obj_radius,
                                                                    max_tries=20,
                                                                    location_radius=l_radius)[0]):
                                    print("Could not calculate valid object location")
                                    self.communicate([{"$type": "send_images",
                                                       "frequency": "never"},
                                                      {"$type": "destroy_object",
                                                       "id": obj_count}])
                                    obj_overlaps += 1
                                    # Ensures next attempt to load in item is not the same item as before
                                    random.shuffle(objects)
                                    break

                                # Find appropriate, non-overlapping object position
                                # Reset object position to the valid position
                                else:
                                    print("Object fits in scene")
                                    valid_obj_pos = self._get_object_position(scene_dimensions=scene_dimensions,
                                                                              object_positions=positions_list,
                                                                              object_to_add_radius=obj_radius,
                                                                              max_tries=20,
                                                                              location_radius=l_radius)[1]
                                    print("Position calculated")
                                    positions_list.append(ObjectPosition(valid_obj_pos, obj_radius))
                                    self.communicate([{"$type": "send_images",
                                                       "frequency": "never"},
                                                      {"$type": "destroy_object",
                                                       "id": obj_count}])
                                    print("Object ready to reset")
                                    self.communicate([{"$type": "send_images",
                                                       "frequency": "never"},
                                                      {"$type": "add_object",
                                                       "name": objects[obj_count][0],
                                                       "url": record.get_url(),
                                                       "scale_factor": record.scale_factor,
                                                       "position": valid_obj_pos,
                                                       "rotation": {"x": 0, "y": 0, "z": 0},
                                                       "category": record.wcategory,
                                                       "id": obj_count}])
                                    print("Object reset")

                                    # Rotate the object randomly
                                    print("Rotating object")
                                    self.communicate({"$type": "rotate_object_by",
                                                      "angle": random.uniform(-45, 45),
                                                      "axis": "yaw",
                                                      "id": obj_count,
                                                      "is_world": True})

                                    # Don't rotate the object if doing so will result in overlap into scene
                                    if not (o.get_bottom(i)[1] < 0 or o.get_top(i)[1] > 0.9 * scene_dimensions[1][1]):
                                        pitch_angle = random.uniform(-45, 45)
                                        self.communicate({"$type": "rotate_object_by",
                                                          "angle": pitch_angle,
                                                          "axis": "pitch",
                                                          "id": obj_count,
                                                          "is_world": True})
                                        roll_angle = random.uniform(-45, 45)
                                        self.communicate({"$type": "rotate_object_by",
                                                          "angle": roll_angle,
                                                          "axis": "roll",
                                                          "id": obj_count,
                                                          "is_world": True})

                                    # Setting random materials/textures
                                    # Looping through sub-objects and materials
                                    sub_count = 0
                                    for sub_object in record.substructure:
                                        # Loop through materials in sub-objects
                                        for j in range(len(sub_object)):
                                            # Get random material and load in
                                            material = random.choice(materials[1:])
                                            self.load_material(material)
                                            print("Material loaded")

                                            # Set random material on material of sub-object
                                            self.communicate({"$type": "set_visual_material",
                                                              "material_index": j,
                                                              "material_name": material[0],
                                                              "object_name": sub_object['name'],
                                                              "id": obj_count})
                                            print("Material set")
                                            sub_count += 1
                                            if sub_count > 10:
                                                break
                                        break

                                    print("Updating count")
                                    obj_count += 1
                                    print("Breaking out of object_id loop")
                                    break

                            # Break out of buffer loop
                            print("Breaking out of buffer loop")
                            break

                    # Move onto next iteration of while loop (next object to load in)
                    print("Object added - next while loop iteration")
                    continue

                # Enable image capture
                self.communicate({"$type": "set_pass_masks",
                                  "avatar_id": "avatar",
                                  "pass_masks": ["_img", "_id"]})

                self.communicate({"$type": "send_images",
                                  "frequency": "always"})

                # Capture scene
                scene_data = self.communicate({"$type": "look_at_position",
                                               "avatar_id": "avatar",
                                               "position": {"x": 0,
                                                            "y": scene_dimensions[0][1] / 2,
                                                            "z": 0}})
                images = Images(scene_data[0])
                TDWUtils.save_images(images, TDWUtils.zero_padding(i), output_directory=path)


if __name__ == "__main__":
    animate = GenerateScenes()
    animate.get_lists()
    animate.set_dir()
    print("Run()")
    animate.run()
