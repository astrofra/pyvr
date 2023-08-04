import harfang as hg

def InitVRControllers(vr_controller=None, vr_controller_idx=None):

	if vr_controller is None or vr_controller_idx is None:
		vr_controller = [hg.VRController(), hg.VRController()]
		vr_controller_idx = [0, 0]

	name_template = "openvr_controller_"

	left_hand_connected = vr_controller[0].IsConnected()
	right_hand_connected = vr_controller[1].IsConnected()

	if not left_hand_connected:
		for i in range(16):
			if not right_hand_connected or vr_controller_idx[1] != i:
				if hg.ReadVRController(name_template + str(i)).IsConnected():
					vr_controller[0] = hg.VRController(name_template + str(i))
					vr_controller_idx[0] = i
					left_hand_connected = True
					print("Using controller %1 for left hand" + str(i))
					break

	if not right_hand_connected:
		for i in range(16):
			if not left_hand_connected or vr_controller_idx[0] != i:
				if hg.ReadVRController(name_template + str(i)).IsConnected():
					vr_controller[1] = hg.VRController(name_template + str(i))
					vr_controller_idx[1] = i
					right_hand_connected = True
					print("Using controller %1 for right hand" + str(i))
					break

	return vr_controller, vr_controller_idx


def UpdateVRControllers(vr_controller, vr_controller_idx):
	vr_controller, vr_controller_idx = InitVRControllers(vr_controller, vr_controller_idx)

	for i in range(2):
		vr_controller[i].Update()

	return vr_controller, vr_controller_idx