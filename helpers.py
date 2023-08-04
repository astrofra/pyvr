import harfang as hg


# Create materials
def create_material(ubc, orm, prg_ref):
	mat = hg.Material()
	hg.SetMaterialProgram(mat, prg_ref)
	hg.SetMaterialValue(mat, "uBaseOpacityColor", ubc)
	hg.SetMaterialValue(mat, "uOcclusionRoughnessMetalnessColor", orm)
	return mat


def DrawSpline(p1, p2, p3, p4, vid, vtx_layout_spline, line_shader):
	step = 10
	prev_value = [p1.x, p1.y, p1.z]
	vtx = hg.Vertices(vtx_layout_spline, step * 2)
	spline_color = hg.Color.Blue + hg.Color.Green
	for i in range(step+1):
		step_range = (1 / step) * i
		val_x = hg.CubicInterpolate(p2.x, p1.x, p4.x, p3.x, step_range)
		val_y = hg.CubicInterpolate(min(p2.y, 0), p1.y, p4.y, p3.y, step_range)
		val_z = hg.CubicInterpolate(p2.z, p1.z, p4.z, p3.z, step_range)
		val = [val_x, val_y, val_z]
		vtx.Begin(2 * i).SetPos(hg.Vec3(prev_value[0], prev_value[1], prev_value[2])).SetColor0(spline_color).End()
		vtx.Begin(2 * i + 1).SetPos(hg.Vec3(val[0], val[1], val[2])).SetColor0(spline_color).End()
		prev_value = val

	hg.DrawLines(vid, vtx, line_shader)  # submit all lines in a single call