from Leonard.random_scenes.ObjectPosition import ObjectPosition
from scipy.spatial import distance
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import SceneLibrarian, ModelLibrarian
from tdw.output_data import Images, OutputData, Environments, Bounds
from typing import List, Dict, Tuple
import msCOCO_matrix
import TDW_relationships
import numpy as np
import time
import random
import os
import shutil
import csv
import math

TDW_COCO_models_list = "/Users/leonard/Desktop/TDWBase-1.5.0/Python/Leonard/objects_changing_positions/COCO_to_TDW.csv"
TDW_COCO_models = dict()
# materials_list = "/Users/leonard/Desktop/TDWBase-1.5.0/Python/Leonard/json_list/materials_list.csv"
# materials = []
scenes_list = "/Users/leonard/Desktop/TDWBase-1.5.0/Python/Leonard/json_list/scenes_list.csv"
scenes = []
path = ""


class GenerateScenes(Controller):

    @staticmethod
    def get_lists():
        with open(TDW_COCO_models_list) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                TDW_COCO_models[row[0]] = row[1]

        # with open(materials_list) as csvfile:
        #     reader = csv.reader(csvfile)
        #     for row in reader:
        #         materials.append(row)

        with open(scenes_list) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                scenes.append(row)

    @staticmethod
    def set_dir():
        # Setting up image directory
        output_directory = "objects_positions_images"
        parent_dir = '/Users/leonard/Desktop/TDWBase-1.5.0/Python/Leonard/objects_changing_positions'
        global path
        path = os.path.join(parent_dir, output_directory)
        if os.path.exists(path):
            shutil.rmtree(path)
            time.sleep(0.5)
            os.mkdir(path)

    # In case we don't want to use computationally intensive scenes
    # def create(self):
    #     c.start()
    #     c.communicate(TDWUtils.create_empty_room(20, 20))

    # Don't need this to investigate object positions only
    # def load_material(self, material):
    #
    #     return self.communicate({"$type": "add_material",
    #                              "name": material[0],
    #                              "url": material[2]})

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

        # Start with everything on ground
        # # Set height value
        # o_pos[1] = random.uniform(0, 0.9 * scene_dimensions[1][1] / 3)
        o_pos = TDWUtils.array_to_vector3(o_pos)
        # print("O_Pos:", o_pos)

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

                    # o_pos = TDWUtils.get_random_point_in_circle(center=np.array([
                    #                                                  random.uniform(-0.9 * scene_dimensions[1][0] / 2
                    #                                                                 , 0.9 * scene_dimensions[1][0] / 2),
                    #                                                  0,
                    #                                                  random.uniform(-0.9 * scene_dimensions[1][2] / 2
                    #                                                                 , 0.9 * scene_dimensions[1][2] / 2)]),
                    #                                             radius=location_radius)

                    o_pos = TDWUtils.get_random_point_in_circle(center=np.array([0, 0, 0]),
                                                                radius=location_radius)
                    # Scale circular point --> elliptic point for non-square rooms
                    # Width > Depth of scene
                    if scene_dimensions[1][0] > scene_dimensions[1][2]:
                        o_pos[0] = o_pos[0] * scene_dimensions[1][0] / scene_dimensions[1][2]
                    # Depth > Width of scene
                    else:
                        o_pos[2] = o_pos[2] * scene_dimensions[1][2] / scene_dimensions[1][0]

                    # Don't change height for now
                    # o_pos[1] = random.uniform(0, 0.9 * scene_dimensions[1][1])
                    o_pos = TDWUtils.array_to_vector3(o_pos)
                    print("O_Pos:", o_pos)
        return [ok, o_pos]

    # Quick wrapper function to get bounds data given object
    def get_bounds_data(self, object_id):
        resp = self.communicate({"$type": "send_bounds",
                                 "frequency": "once",
                                 "ids": [object_id]})
        return Bounds(resp[0])

    def run(self):
        """ Generate room using COCO_TDW dataset """
        objects_in_scene = 15
        object_ids = []
        # Get Category-Object mapping
        TDW_COCO_models = TDW_relationships.get_COCO_TDW_mapping()
        # print("TDWCOCO:", TDW_COCO_models)
        # print("KEYS:", TDW_COCO_models.keys())

        # Gets COCO categories co-occurring in a scene
        # +5 is for dealing with failed object insertion attempts
        COCO_configurations = msCOCO_matrix.get_max_co_occurrence(5, int(objects_in_scene + 5))
        configuration_1 = COCO_configurations[0]
        print("Config 1:", configuration_1)
        # TDW models/objects
        objects = []
        for COCO_object in configuration_1:
            print(COCO_object)
            print(COCO_object.split())
            if len(COCO_object.split()) > 1:
                COCO_object = COCO_object.split()[-1]
                print(COCO_object)
            # Check if COCO category is a key in the COCO-TDW mapping
            if COCO_object in TDW_COCO_models.keys():
                # Gets random TDW model (from COCO-to-TDW map) based on COCO category key
                print(TDW_COCO_models[COCO_object])
                model = TDW_COCO_models[COCO_object][random.randint(0, len(TDW_COCO_models[COCO_object]) - 1)]
                objects.append(model)

        print("COCO to TDW objects:", objects)
        # print(len(objects))

        # Stores object categories that other objects can be placed upon (e.g. table, chair, couch, bed)
        surface_properties_list = TDW_COCO_models['table'] + TDW_COCO_models['chair'] + \
                                  TDW_COCO_models['bed'] + TDW_COCO_models['couch'] + \
                                  TDW_COCO_models['bench'] + TDW_COCO_models['refrigerator']
        surface_categories = []
        for surface_properties in surface_properties_list:
            surface_categories.append(surface_properties[0])

        print("Surface Categories:", surface_categories)

        # Stores the actual surface object instances/ids alongside number of objects on the surface
        surface_object_ids = {}

        self.start()
        positions_list = []  # Stores current model locations and radii
        scene_dimensions = []  # Store scene/environment dimensions
        init_setup_commands = [{"$type": "set_screen_size",
                                "width": 640,
                                "height": 481},
                               {"$type": "set_render_quality",
                                "render_quality": 1}]
        self.communicate(init_setup_commands)

        scene_lib = SceneLibrarian()
        # Disable physics when adding in new objects (objects float)
        self.communicate({"$type": "simulate_physics",
                          "value": False})

        for scene in scenes[1:]:
            # Load in scene
            # print("Scene", scene[0])
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
                # print("Avatar Position:", avatar_position)
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

                # # Gets rid of header (Model: Category)
                # objects = TDW_COCO_models[1:]
                # random.shuffle(objects)
                obj_count = 0
                obj_overlaps = 0  # Number of failed attempts to place object due to over-dense objects area
                while obj_count < objects_in_scene and obj_overlaps < 5:
                    # Handles if object has been added to a flat surface
                    added_to_surface = False
                    print("Object COUNT:", obj_count)
                    # Need to have random position for Bounds Data to return meaningful info
                    valid_obj_pos = {"x": random.uniform(-1 * scene_dimensions[1][0] / 2,
                                                         0.5 * scene_dimensions[1][0] / 2),
                                     "y": scene_dimensions[1][1] / 4,
                                     "z": random.uniform(-0.9 * scene_dimensions[1][2] / 2,
                                                         0.9 * scene_dimensions[1][2] / 2)}
                    print("First random position")
                    # Add in the object at random position
                    # Object will later be removed or updated accordingly after performing collision calculations
                    record = ModelLibrarian(library="models_full.json").get_record(objects[obj_count][0])
                    print("Record gotten")
                    print(objects[obj_count][0])
                    o_id = self.communicate({"$type": "add_object",
                                             "name": objects[obj_count][0],
                                             "url": record.get_url(),
                                             "scale_factor": record.scale_factor,
                                             "position": valid_obj_pos,
                                             "rotation": TDWUtils.VECTOR3_ZERO,
                                             "category": record.wcategory,
                                             "id": obj_count})

                    print("Random first add")

                    # Returns bound data for added object
                    bounds_data = self.communicate({"$type": "send_bounds",
                                                    "frequency": "once"})

                    print("Bounds returned")

                    # Appends object, with information on position and obj_radius, to positions_list
                    # Length of buffer array should be 1
                    # print("Bounds Data:", bounds_data)
                    for b in bounds_data[:-1]:
                        # print("Buffer Loop:", b)
                        b_id = OutputData.get_data_type_id(b)
                        if b_id == "boun":
                            # print("BOUNDS")
                            o = Bounds(b)
                            # print("# of Objects:", o.get_num())
                            # print("# of Failed Attempts:", obj_overlaps)
                            # print("Buffer Array:", b)
                            # print("Bounds Object:", o)
                            for i in range(o.get_num()):
                                print("Object ID:", o.get_id(i))
                                print("obj_count:", obj_count)
                                print("Object:", objects[obj_count][0], "Category:", objects[obj_count][1])
                                # print("Object Center:", o.get_center(i))
                                # Only want to compute valid_position for object we are about to add
                                # Skip any computation if this is not the case
                                if o.get_id(i) != obj_count:
                                    continue
                                # Useful for detecting if object fits in environment
                                # print("Calculating if object fits in environment")
                                width = distance.euclidean(o.get_left(i), o.get_right(i))
                                depth = distance.euclidean(o.get_front(i), o.get_back(i))
                                height = distance.euclidean(o.get_top(i), o.get_bottom(i))
                                # print("Width:", width)
                                # print("Depth:", depth)
                                # ("Height:", height)

                                # Useful for avoiding object overlap
                                # print("Calculating Object Bounds")
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

                                # print("Obj_Radius:", obj_radius)

                                # Set sweeping radius, based on scene plane dimensions
                                l_radius = random.uniform(0, min(0.5 * scene_dimensions[1][0] / 2,
                                                                 0.5 * scene_dimensions[1][2] / 2))

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
                                    # Check if object fits on table, chair, couch, etc.
                                    # Add object if it fits, place it somewhere on top of the surface
                                    for surface_id in surface_object_ids.keys():
                                        print("Surface ID:", surface_id)
                                        # Skip placement feasibility if the object is already a surface-type object
                                        # Ex. no chair on top of a table
                                        if objects[obj_count][0] in surface_categories:
                                            print("Object: %s is already a surface object" % objects[obj_count][0])
                                            break

                                        # Check how many objects are on surface
                                        if surface_object_ids[surface_id] >= 3:
                                            print("Too many objects on surface")
                                            print("From surface objects dict:", surface_object_ids[surface_id])
                                            continue

                                        surface_bounds = self.get_bounds_data(surface_id)
                                        surface_area = distance.euclidean(surface_bounds.get_left(0),
                                                                          surface_bounds.get_right(0)) * \
                                                       distance.euclidean(surface_bounds.get_front(0),
                                                                          surface_bounds.get_back(0))
                                        obj_area = width * height
                                        if obj_area < surface_area:
                                            s_center_to_top = distance.euclidean(surface_bounds.get_center(0),
                                                                                 surface_bounds.get_top(0))
                                            s_center_to_bottom = distance.euclidean(surface_bounds.get_center(0),
                                                                                    surface_bounds.get_bottom(0))
                                            s_center_to_left = distance.euclidean(surface_bounds.get_center(0),
                                                                                  surface_bounds.get_left(0))
                                            s_center_to_right = distance.euclidean(surface_bounds.get_center(0),
                                                                                   surface_bounds.get_right(0))
                                            s_center_to_front = distance.euclidean(surface_bounds.get_center(0),
                                                                                   surface_bounds.get_front(0))
                                            s_center_to_back = distance.euclidean(surface_bounds.get_center(0),
                                                                                  surface_bounds.get_back(0))

                                            surface_radius = \
                                                max(math.sqrt(
                                                    s_center_to_top ** 2 + s_center_to_left ** 2 + s_center_to_front ** 2),
                                                    math.sqrt(
                                                        s_center_to_top ** 2 + s_center_to_right ** 2 + s_center_to_front ** 2),
                                                    math.sqrt(
                                                        s_center_to_top ** 2 + s_center_to_left ** 2 + s_center_to_back ** 2),
                                                    math.sqrt(
                                                        s_center_to_top ** 2 + s_center_to_right ** 2 + s_center_to_back ** 2),
                                                    math.sqrt(
                                                        s_center_to_bottom ** 2 + s_center_to_left ** 2 + s_center_to_front ** 2),
                                                    math.sqrt(
                                                        s_center_to_bottom ** 2 + s_center_to_right ** 2 + s_center_to_front ** 2),
                                                    math.sqrt(
                                                        s_center_to_bottom ** 2 + s_center_to_left ** 2 + s_center_to_back ** 2),
                                                    math.sqrt(
                                                        s_center_to_bottom ** 2 + s_center_to_right ** 2 + s_center_to_back ** 2))

                                            print("Surface-type object")
                                            self.communicate({"$type": "destroy_object",
                                                              "id": obj_count})

                                            # Adding the object to the top of the surface
                                            on_pos = surface_bounds.get_top(0)
                                            on_y = on_pos[1]
                                            on_pos = TDWUtils.get_random_point_in_circle(np.array(on_pos),
                                                                                         0.7 * surface_radius)
                                            on_pos[1] = on_y
                                            on_pos = TDWUtils.array_to_vector3(on_pos)
                                            on_rot = {"x": 0, "y": random.uniform(-45, 45), "z": 0}
                                            # Add the object.
                                            print("Model Name on Surface:", objects[obj_count][0])
                                            record = ModelLibrarian(library="models_full.json").get_record(
                                                objects[obj_count][0])
                                            on_id = self.communicate({"$type": "add_object",
                                                                      "name": objects[obj_count][0],
                                                                      "url": record.get_url(),
                                                                      "scale_factor": record.scale_factor,
                                                                      "position": on_pos,
                                                                      "rotation": on_rot,
                                                                      "category": record.wcategory,
                                                                      "id": obj_count})
                                            obj_count += 1
                                            surface_object_ids[surface_id] += 1
                                            object_ids.append(obj_count)
                                            print("Object added on top of surface")
                                            added_to_surface = True
                                            # Breaking out of surface objects loop
                                            break

                                    if added_to_surface:
                                        print("Breaking out of object loop")
                                        # Breaking out of object loop
                                        break

                                    print("Post-surface")

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
                                    added_object_id = self.communicate({"$type": "add_object",
                                                                        "name": objects[obj_count][0],
                                                                        "url": record.get_url(),
                                                                        "scale_factor": record.scale_factor,
                                                                        "position": valid_obj_pos,
                                                                        "rotation": {"x": 0, "y": 0, "z": 0},
                                                                        "category": record.wcategory,
                                                                        "id": obj_count})
                                    # print("Object ID:", added_object_id)
                                    print("Regular object add")
                                    object_ids.append(added_object_id)
                                    # If TDW model belongs to surface categories, store id_information
                                    if objects[obj_count][0] in surface_categories:
                                        surface_object_ids[obj_count] = 0
                                    # Rotate the object randomly
                                    print("Rotating object")
                                    self.communicate({"$type": "rotate_object_by",
                                                      "angle": random.uniform(-45, 45),
                                                      "axis": "yaw",
                                                      "id": obj_count,
                                                      "is_world": True})

                                     # Minimal rotating for position differences
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
                                     # Don't need this for just changing positions
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

                # for i in range(200):
                #     self.communicate({"$type": "simulate_physics",
                #                       "value": False})

                # Enable image capture
                self.communicate({"$type": "set_pass_masks",
                                  "avatar_id": "avatar",
                                  "pass_masks": ["_img", "_id"]})

                self.communicate({"$type": "send_images",
                                  "frequency": "always"})

                # Capture scene
                # NOTE: THESE SCENES GET REPLACED IN THE TARGET DIRECTORY
                scene_data = self.communicate({"$type": "look_at_position",
                                               "avatar_id": "avatar",
                                               "position": {"x": 0,
                                                            "y": scene_dimensions[0][1] / 2,
                                                            "z": 0}})
                images = Images(scene_data[0])
                TDWUtils.save_images(images, TDWUtils.zero_padding(i), output_directory=path)
                print("Object ids:", object_ids)

                # # Loop through each object ID in scene to alter positioning
                # for obj_num in obj_count:
                #     # Skip if object is a surface object
                #     if objects[obj_num] in surface_categories:
                #         continue
                #
                #     obj_bounds = self.get_bounds_data(obj_num)
                #     obj_height = obj_bounds.get_bottom()[1]
                #     obj_center = obj_bounds.get_bottom()
                #     obj_center[1] -= obj_height
                #     pos = TDWUtils.get_random_point_in_circle(obj_center, 0.125)
                #     pos[1] = pos[1] + obj_height + random.uniform(0, 0.5)
                #     pos = TDWUtils.array_to_vector3(pos)
                #
                #     # Remove object
                #     # self.communicate("$type":)
                #
                #     scene_data = self.communicate({"$type": "look_at_position",
                #                                    "avatar_id": "avatar",
                #                                    "position": {"x": 0,
                #                                                 "y": scene_dimensions[0][1] / 2,
                #                                                 "z": 0}})
                #     images = Images(scene_data[0])
                #     TDWUtils.save_images(images, TDWUtils.zero_padding(i), output_directory=path)


if __name__ == "__main__":
    animate = GenerateScenes()
    animate.get_lists()
    animate.set_dir()
    print("Run()")
    animate.run()
