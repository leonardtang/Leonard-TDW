# while len(self.communicate([])) > 1:
#     obj_bytes = self.communicate([])
#     for b in obj_bytes[:-1]:
#         b_id = OutputData.get_data_type_id(b)
#         print(b_id)
#         # Return collision data
#         # For later: if objects in scene collide, remove obj_count and re-add
#         # if b_id == "coll":
#         print("collision data")
#
#         if b_id == "coll":
#             collision = Collision(b)
#             print("Collision between two objects:")
#             print("\tEvent: " + collision.get_state())
#             print("\tCollider: " + str(collision.get_collider_id()))
#             print("\tCollidee: " + str(collision.get_collidee_id()))
#             print("\tRelative velocity: " + str(collision.get_relative_velocity()))
#             print("\tContacts:")
#             for j in range(collision.get_num_contacts()):
#                 print(str(collision.get_contact_normal(j)) + "\t" + str(
#                     collision.get_contact_point(j)))
#         # There was a collision between an object and the environment.
#         elif b_id == "enco":
#             collision = EnvironmentCollision(b)
#             print("Collision between an object and the environment:")
#             print("\tEvent: " + collision.get_state())
#             print("\tCollider: " + str(collision.get_object_id()))
#             print("\tContacts:")
#             for j in range(collision.get_num_contacts()):
#                 print(str(collision.get_contact_normal(j)) + "\t" + str(
#                     collision.get_contact_point(j)))


# self.communicate({"$type": "set_object_collision_detection_mode",
#                   "mode": "continuous_speculative",
#                   "id": obj_count})
#
# self.communicate({"$type": "send_collisions",
#                   "enter": True,
#                   "stay": True,
#                   "exit": True,
#                   "collision_types": ["obj"]})

# Keep going until object hits floor (no more collisions)
# obj_bytes = self.communicate([])