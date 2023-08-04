import harfang as hg
import math
from helpers import DrawSpline


def UpdateTeleporterPos(controller, actor_pos, head_pos, teleporter_pos, playground=None):
	if controller.IsConnected():
		world = controller.World()
		T = hg.GetT(world)
		Z = hg.GetZ(world)

		min_Vy = -0.1

		if Z.y < min_Vy:
			if playground is not None:
				teleport_I = T + Z * (playground[0].y - T.y) / Z.y
				teleport_I = hg.Clamp(teleport_I, playground[0], playground[1])
			else:
				teleport_I = T + Z * (0 - T.y) / Z.y

			# detect trigger
			if controller.Pressed(hg.VRCB_Axis1):
				new_actor_pos = teleport_I + (actor_pos - head_pos)
				actor_diff = new_actor_pos - actor_pos
				teleporter_pos = teleport_I + actor_diff
				actor_pos = new_actor_pos
			else:
				teleporter_pos = teleport_I

	return actor_pos, teleporter_pos


def UpdateTeleporterNode(controller, actor_pos, head_pos, teleporter_node, playground=None):
	if controller.IsConnected():
		world = controller.World()
		T = hg.GetT(world)
		Z = hg.GetZ(world)

		min_Vy = -0.1

		if Z.y < min_Vy:
			if playground is not None:
				teleport_I = T + Z * (playground[0].y - T.y) / Z.y
				teleport_I = hg.Clamp(teleport_I, playground[0], playground[1])
			else:
				teleport_I = T + Z * (0 - T.y) / Z.y

			# detect trigger
			if controller.Pressed(hg.VRCB_Axis1):
				new_actor_pos = teleport_I + (actor_pos - head_pos)
				actor_diff = new_actor_pos - actor_pos
				teleporter_pos = teleport_I + actor_diff
				actor_pos = new_actor_pos
			else:
				teleporter_pos = teleport_I

			teleporter_node.GetTransform().SetPos(teleporter_pos)
			teleporter_node.Enable()
		else:
			teleporter_node.Disable()

	return actor_pos


def GetHeadPos(vr_state, actor_pos):
	headT = hg.GetT(vr_state.head)
	return hg.Vec3(headT.x, actor_pos.y, headT.z)


def DrawTeleporterSpline(controller_mtx, ground_mtx, vid, vtx_layout_spline, line_shader):
	dir_teleporter = hg.GetZ(controller_mtx)
	pos_start = hg.GetT(controller_mtx)
	cos_angle = hg.Dot(dir_teleporter, hg.Normalize(hg.Vec3(dir_teleporter.x, 0, dir_teleporter.z)))
	cos_angle = min(1.0, max(cos_angle, -1))
	angle = math.acos(cos_angle)
	strength_force = pow((math.sin(angle) + 1) / 2, 2) * 2

	DrawSpline(pos_start, pos_start + dir_teleporter * strength_force, ground_mtx + hg.Vec3(0, -strength_force, 0), ground_mtx, vid, vtx_layout_spline, line_shader)