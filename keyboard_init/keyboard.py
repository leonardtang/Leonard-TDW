from getch import getch
from tdw.output_data import Transforms
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
c.start()
c.communicate(TDWUtils.create_empty_room(20, 20))
c.communicate([{"$type": "set_screen_size",
                "width": 1280,
                "height": 962},
               {"$type": "set_render_quality",
                "render_quality": 2}])
c.communicate(TDWUtils.create_avatar(avatar_id="avatar",
                                     position={"x": 3, "y": 1.5, "z": 3},
                                     look_at={"x": 0, "y": 0, "z": 0}))
o_id = c.add_object(model_name="iron_box",
                    position={"x": 0, "y": 0, "z": 0},
                    rotation={"x": 0, "y": 0, "z": 0},
                    library="models_full.json")
c.communicate({"$type": "send_transforms",
               "frequency": "always"})

char = getch()

if char == b'w':
    resp = c.communicate({"$type": "teleport_object",
                          "position": {"x": 1, "y": 0, "z": 0},
                          "id": o_id})
    transform = Transforms(resp[0])

    # Get the position and rotation of the iron_box object.
    position = transform.get_position(0)
    rotation = transform.get_rotation(0)

    print("Position: " + position)
    print("Rotation: " + rotation)
