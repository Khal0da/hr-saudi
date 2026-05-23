from frappe import _


def get_data():
	return [
		{
			"label": _("HR Saudi"),
			"icon": "octicon octicon-organization",
			"items": [
				{
					"type": "doctype",
					"name": "Employee",
					"label": _("Employee"),
					"description": _("Employee master data"),
				},
				{
					"type": "doctype",
					"name": "Biometric User Mapping",
					"label": _("Biometric User Mapping"),
					"description": _("Map device user IDs to employees"),
				},
				{
					"type": "doctype",
					"name": "Attendance Settings",
					"label": _("Attendance Settings"),
					"description": _("Configure attendance rules"),
				},
				{
					"type": "doctype",
					"name": "Geo Fence",
					"label": _("Geo Fence"),
					"description": _("Define site boundaries for GPS attendance"),
				},
				{
					"type": "page",
					"name": "attendance",
					"label": _("Mobile Attendance"),
					"description": _("GPS & QR attendance for sites without devices"),
				},
			],
		},
	]
