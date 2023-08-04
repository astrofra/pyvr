# Display a scene in VR

import harfang as hg
import sys
import math
from teleporter import UpdateTeleporterNode, GetHeadPos, DrawTeleporterSpline
from controllers import InitVRControllers, UpdateVRControllers

def main():
	hg.InputInit()
	hg.WindowSystemInit()

	res_x, res_y = 1280, 720
	win = hg.RenderInit("Harfang - OpenVR Scene", res_x, res_y, hg.RF_VSync | hg.RF_MSAA4X)

	hg.AddAssetsFolder("assets_compiled")

	pipeline = hg.CreateForwardPipeline()
	res = hg.PipelineResources()

	render_data = hg.SceneForwardPipelineRenderData()  # this object is used by the low-level scene rendering API to share view-independent data with both eyes

	# OpenVR initialization
	if not hg.OpenVRInit():
		sys.exit()

	vr_left_fb = hg.OpenVRCreateEyeFrameBuffer(hg.OVRAA_MSAA4x)
	vr_right_fb = hg.OpenVRCreateEyeFrameBuffer(hg.OVRAA_MSAA4x)

	# Create models
	vtx_layout = hg.VertexLayoutPosFloatNormUInt8()

	cube_mdl = hg.CreateCubeModel(vtx_layout, 0.1, 0.1, 0.1)
	cube_ref = res.AddModel('cube', cube_mdl)
	ground_mdl = hg.CreateCubeModel(vtx_layout, 50, 0.01, 50)
	ground_ref = res.AddModel('ground', ground_mdl)

	# Teleporter spline
	line_shader = hg.LoadProgramFromAssets('shaders/pos_rgb')
	vtx_layout_spline = hg.VertexLayout()
	vtx_layout_spline.Begin()
	vtx_layout_spline.Add(hg.A_Position, 3, hg.AT_Float)
	vtx_layout_spline.Add(hg.A_Color0, 3, hg.AT_Float)
	vtx_layout_spline.End()

	# Load shader
	prg_ref = hg.LoadPipelineProgramRefFromAssets('core/shader/pbr.hps', res, hg.GetForwardPipelineInfo())

	# Create scene
	scene = hg.Scene()

	hg.LoadSceneFromAssets("playground/playground.scn", scene, res, hg.GetForwardPipelineInfo())

	# Setup 2D rendering to display eyes textures
	quad_layout = hg.VertexLayout()
	quad_layout.Begin().Add(hg.A_Position, 3, hg.AT_Float).Add(hg.A_TexCoord0, 3, hg.AT_Float).End()

	quad_model = hg.CreatePlaneModel(quad_layout, 1, 1, 1, 1)
	quad_render_state = hg.ComputeRenderState(hg.BM_Alpha, hg.DT_Disabled, hg.FC_Disabled)

	eye_t_size = res_x / 2.5
	eye_t_x = (res_x - 2 * eye_t_size) / 6 + eye_t_size / 2
	quad_matrix = hg.TransformationMat4(hg.Vec3(0, 0, 0), hg.Vec3(hg.Deg(90), hg.Deg(0), hg.Deg(0)), hg.Vec3(eye_t_size, 1, eye_t_size))

	tex0_program = hg.LoadProgramFromAssets("shaders/sprite")

	quad_uniform_set_value_list = hg.UniformSetValueList()
	quad_uniform_set_value_list.clear()
	quad_uniform_set_value_list.push_back(hg.MakeUniformSetValue("color", hg.Vec4(1, 1, 1, 1)))

	quad_uniform_set_texture_list = hg.UniformSetTextureList()

	# Teleporter
	teleporter_node = hg.CreateInstanceFromAssets(scene, hg.Mat4.Identity, 'teleporter/teleporter.scn', res, hg.GetForwardPipelineInfo())[0]

	hand_left = hg.CreateInstanceFromAssets(scene, hg.Mat4.Identity, 'vr_controller/vr_controller.scn', res, hg.GetForwardPipelineInfo())[0]
	hand_left.SetName("hand_left")
	hand_right = hg.CreateInstanceFromAssets(scene, hg.Mat4.Identity, 'vr_controller/vr_controller.scn', res, hg.GetForwardPipelineInfo())[0]
	hand_right.SetName("hand_right")

	actor_pos = hg.Vec3(-1.3, 0, -2)
	head_pos = hg.Vec3()
	playground = [hg.Vec3(-3, 0, -3), hg.Vec3(3, 0, 3)]

	vr_controller, vr_controller_idx = InitVRControllers()

	# Main loop
	while not hg.ReadKeyboard().Key(hg.K_Escape):
		dt = hg.TickClock()

		# Teleporter and VR controller update
		vr_controller, vr_controller_idx = UpdateVRControllers(vr_controller, vr_controller_idx)
		hand_left.GetTransform().SetWorld(vr_controller[0].World())
		hand_right.GetTransform().SetWorld(vr_controller[1].World())

		controller = vr_controller[0]
		actor_pos = UpdateTeleporterNode(controller, actor_pos, head_pos, teleporter_node)

		scene.Update(dt)

		vr_state = hg.OpenVRGetState(hg.TranslationMat4(actor_pos), 0.1, 200)

		head_pos = GetHeadPos(vr_state, actor_pos)

		left, right = hg.OpenVRStateToViewState(vr_state)

		vid = 0  # keep track of the next free view id
		passId = hg.SceneForwardPipelinePassViewId()

		# Prepare view-independent render data once
		vid, passId = hg.PrepareSceneForwardPipelineCommonRenderData(vid, scene, render_data, pipeline, res, passId)
		vr_eye_rect = hg.IntRect(0, 0, vr_state.width, vr_state.height)

		# Prepare the left eye render data then draw to its framebuffer
		vid, passId = hg.PrepareSceneForwardPipelineViewDependentRenderData(vid, left, scene, render_data, pipeline, res, passId)
		vid, passId = hg.SubmitSceneToForwardPipeline(vid, scene, vr_eye_rect, left, pipeline, render_data, res, vr_left_fb.GetHandle())

		# Prepare the right eye render data then draw to its framebuffer
		vid, passId = hg.PrepareSceneForwardPipelineViewDependentRenderData(vid, right, scene, render_data, pipeline, res, passId)
		vid, passId = hg.SubmitSceneToForwardPipeline(vid, scene, vr_eye_rect, right, pipeline, render_data, res, vr_right_fb.GetHandle())

		# Display teleporter spline:
		hg.SetViewFrameBuffer(vid, vr_left_fb.GetHandle())
		hg.SetViewRect(vid, 0, 0, vr_state.width, vr_state.height)
		hg.SetViewClear(vid, 0, 0, 1.0, 0)
		hg.SetViewTransform(vid, left.view, left.proj)
		DrawTeleporterSpline(controller.World(), teleporter_node.GetTransform().GetPos(), vid, vtx_layout_spline, line_shader)

		vid += 1

		hg.SetViewFrameBuffer(vid, vr_right_fb.GetHandle())
		hg.SetViewRect(vid, 0, 0, vr_state.width, vr_state.height)
		hg.SetViewClear(vid, 0, 0, 1.0, 0)
		hg.SetViewTransform(vid, right.view, right.proj)
		DrawTeleporterSpline(controller.World(), teleporter_node.GetTransform().GetPos(), vid, vtx_layout_spline, line_shader)

		vid += 1

		# Display the VR eyes texture to the backbuffer
		hg.SetViewRect(vid, 0, 0, res_x, res_y)
		vs = hg.ComputeOrthographicViewState(hg.TranslationMat4(hg.Vec3(0, 0, 0)), res_y, 0.1, 100, hg.ComputeAspectRatioX(res_x, res_y))
		hg.SetViewTransform(vid, vs.view, vs.proj)

		quad_uniform_set_texture_list.clear()
		quad_uniform_set_texture_list.push_back(hg.MakeUniformSetTexture("s_tex", hg.OpenVRGetColorTexture(vr_left_fb), 0))
		hg.SetT(quad_matrix, hg.Vec3(eye_t_x, 0, 1))
		hg.DrawModel(vid, quad_model, tex0_program, quad_uniform_set_value_list, quad_uniform_set_texture_list, quad_matrix, quad_render_state)

		quad_uniform_set_texture_list.clear()
		quad_uniform_set_texture_list.push_back(hg.MakeUniformSetTexture("s_tex", hg.OpenVRGetColorTexture(vr_right_fb), 0))
		hg.SetT(quad_matrix, hg.Vec3(-eye_t_x, 0, 1))
		hg.DrawModel(vid, quad_model, tex0_program, quad_uniform_set_value_list, quad_uniform_set_texture_list, quad_matrix, quad_render_state)

		hg.Frame()
		hg.OpenVRSubmitFrame(vr_left_fb, vr_right_fb)

		hg.UpdateWindow(win)

	hg.DestroyForwardPipeline(pipeline)
	hg.RenderShutdown()
	hg.DestroyWindow(win)


main()