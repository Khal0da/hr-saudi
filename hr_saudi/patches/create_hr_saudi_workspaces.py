import frappe


def execute():
	"""Create HR Saudi workspaces with proper content and links"""
	
	workspaces = [
		{
			"name": "Saudi Operations",
			"title": "Saudi Operations",
			"label": "Saudi Operations",
			"module": "HRSaudi",
			"parent_page": "HR",
			"public": 1,
			"icon": "setting-gear",
			"indicator_color": "green",
			"is_editable": 1,
			"content": '[{"id":"1","type":"header","data":{"text":"<span class=\\"h4\\">Saudi Operations</span>","col":12}},{"id":"2","type":"card","data":{"card_name":"Biometric & Attendance","col":4}},{"id":"3","type":"card","data":{"card_name":"Crew Management","col":4}},{"id":"4","type":"card","data":{"card_name":"Compliance & Documents","col":4}},{"id":"5","type":"card","data":{"card_name":"Reports","col":4}}]',
			"links": [
				{"label": "Biometric & Attendance", "link_count": 3, "type": "Card Break", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Biometric User Mapping", "link_to": "Biometric User Mapping", "link_type": "DocType", "type": "Link", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Attendance Settings", "link_to": "Attendance Settings", "link_type": "DocType", "type": "Link", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Geo Fence", "link_to": "Geo Fence", "link_type": "DocType", "type": "Link", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Crew Management", "link_count": 3, "type": "Card Break", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Crew", "link_to": "Crew", "link_type": "DocType", "type": "Link", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Site Deployment", "link_to": "Site Deployment", "link_type": "DocType", "type": "Link", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Labor Camp", "link_to": "Labor Camp", "link_type": "DocType", "type": "Link", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Compliance & Documents", "link_count": 2, "type": "Card Break", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Incident", "link_to": "Incident", "link_type": "DocType", "type": "Link", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Permit to Work", "link_to": "Permit to Work", "link_type": "DocType", "type": "Link", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Reports", "link_count": 1, "type": "Card Break", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Attendance Summary", "link_to": "Attendance Summary", "link_type": "Report", "type": "Link", "hidden": 0, "is_query_report": 1, "onboard": 0}
			],
			"roles": [{"role": "HR Manager"}, {"role": "HR User"}, {"role": "System Manager"}]
		},
		{
			"name": "Saudization",
			"title": "Saudization",
			"label": "Saudization",
			"module": "HRSaudi",
			"parent_page": "HR",
			"public": 1,
			"icon": "education",
			"indicator_color": "purple",
			"is_editable": 1,
			"content": '[{"id":"1","type":"header","data":{"text":"<span class=\\"h4\\">Saudization</span>","col":12}},{"id":"2","type":"card","data":{"card_name":"Recruitment","col":4}},{"id":"3","type":"card","data":{"card_name":"Reports","col":4}}]',
			"links": [
				{"label": "Recruitment", "link_count": 2, "type": "Card Break", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Job Requisition", "link_to": "Job Requisition", "link_type": "DocType", "type": "Link", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Saudization Settings", "link_to": "Saudization Settings", "link_type": "DocType", "type": "Link", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Reports", "link_count": 2, "type": "Card Break", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Saudization Status", "link_to": "Saudization Status", "link_type": "Report", "type": "Link", "hidden": 0, "is_query_report": 1, "onboard": 0},
				{"label": "Crew Utilization", "link_to": "Crew Utilization", "link_type": "Report", "type": "Link", "hidden": 0, "is_query_report": 1, "onboard": 0}
			],
			"roles": [{"role": "HR Manager"}, {"role": "HR User"}, {"role": "System Manager"}]
		},
		{
			"name": "Subcontractor Management",
			"title": "Subcontractor Management",
			"label": "Subcontractor Management",
			"module": "HRSaudi",
			"parent_page": "HR",
			"public": 1,
			"icon": "users",
			"indicator_color": "orange",
			"is_editable": 1,
			"content": '[{"id":"1","type":"header","data":{"text":"<span class=\\"h4\\">Subcontractor Management</span>","col":12}},{"id":"2","type":"card","data":{"card_name":"Workers","col":4}},{"id":"3","type":"card","data":{"card_name":"Attendance","col":4}},{"id":"4","type":"card","data":{"card_name":"Payroll","col":4}},{"id":"5","type":"card","data":{"card_name":"Reports","col":4}}]',
			"links": [
				{"label": "Workers", "link_count": 1, "type": "Card Break", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Subcontractor Worker", "link_to": "Subcontractor Worker", "link_type": "DocType", "type": "Link", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Attendance", "link_count": 1, "type": "Card Break", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Subcontractor Attendance", "link_to": "Subcontractor Attendance", "link_type": "DocType", "type": "Link", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Payroll", "link_count": 1, "type": "Card Break", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Subcontractor Payroll", "link_to": "Subcontractor Payroll", "link_type": "DocType", "type": "Link", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Reports", "link_count": 1, "type": "Card Break", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Subcontractor Utilization", "link_to": "Subcontractor Utilization", "link_type": "Report", "type": "Link", "hidden": 0, "is_query_report": 1, "onboard": 0}
			],
			"roles": [{"role": "HR Manager"}, {"role": "HR User"}, {"role": "System Manager"}]
		},
		{
			"name": "Payroll Distribution",
			"title": "Payroll Distribution",
			"label": "Payroll Distribution",
			"module": "HRSaudi",
			"parent_page": "HR",
			"public": 1,
			"icon": "money-coins",
			"indicator_color": "blue",
			"is_editable": 1,
			"content": '[{"id":"1","type":"header","data":{"text":"<span class=\\"h4\\">Payroll Distribution</span>","col":12}},{"id":"2","type":"card","data":{"card_name":"Cost Distribution","col":4}}]',
			"links": [
				{"label": "Cost Distribution", "link_count": 1, "type": "Card Break", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Payroll Cost Distribution", "link_to": "Payroll Cost Distribution", "link_type": "DocType", "type": "Link", "hidden": 0, "is_query_report": 0, "onboard": 0}
			],
			"roles": [{"role": "HR Manager"}, {"role": "Accounts Manager"}, {"role": "System Manager"}]
		},
		{
			"name": "Internal Transfers",
			"title": "Internal Transfers",
			"label": "Internal Transfers",
			"module": "HRSaudi",
			"parent_page": "HR",
			"public": 1,
			"icon": "change",
			"indicator_color": "gray",
			"is_editable": 1,
			"content": '[{"id":"1","type":"header","data":{"text":"<span class=\\"h4\\">Internal Transfers</span>","col":12}},{"id":"2","type":"card","data":{"card_name":"Transfers","col":4}}]',
			"links": [
				{"label": "Transfers", "link_count": 1, "type": "Card Break", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Internal Transfer", "link_to": "Internal Transfer", "link_type": "DocType", "type": "Link", "hidden": 0, "is_query_report": 0, "onboard": 0}
			],
			"roles": [{"role": "HR Manager"}, {"role": "HR User"}, {"role": "System Manager"}]
		},
		{
			"name": "Employee Custody",
			"title": "Employee Custody",
			"label": "Employee Custody",
			"module": "HRSaudi",
			"parent_page": "HR",
			"public": 1,
			"icon": "box",
			"indicator_color": "yellow",
			"is_editable": 1,
			"content": '[{"id":"1","type":"header","data":{"text":"<span class=\\"h4\\">Employee Custody</span>","col":12}},{"id":"2","type":"card","data":{"card_name":"Custody Management","col":4}},{"id":"3","type":"card","data":{"card_name":"Reports","col":4}}]',
			"links": [
				{"label": "Custody Management", "link_count": 2, "type": "Card Break", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Employee Custody", "link_to": "Employee Custody", "link_type": "DocType", "type": "Link", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Custody Type", "link_to": "Custody Type", "link_type": "DocType", "type": "Link", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Reports", "link_count": 1, "type": "Card Break", "hidden": 0, "is_query_report": 0, "onboard": 0},
				{"label": "Employee Custody Summary", "link_to": "Employee Custody Summary", "link_type": "Report", "type": "Link", "hidden": 0, "is_query_report": 1, "onboard": 0}
			],
			"roles": [{"role": "HR Manager"}, {"role": "HR User"}, {"role": "Store Manager"}, {"role": "System Manager"}]
		}
	]

	for ws_data in workspaces:
		ws_name = ws_data.pop("name")
		
		try:
			ws = frappe.get_doc("Workspace", ws_name)
			print(f"Updating existing workspace: {ws_name}")
		except frappe.DoesNotExistError:
			ws = frappe.new_doc("Workspace")
			ws.name = ws_name
			print(f"Creating new workspace: {ws_name}")

		for key, value in ws_data.items():
			if key == "links":
				ws.set("links", [])
				for link in value:
					ws.append("links", link)
			elif key == "roles":
				ws.set("roles", [])
				for role in value:
					ws.append("roles", role)
			else:
				ws.set(key, value)

		ws.save()
		frappe.db.commit()
		print(f"Successfully saved workspace: {ws_name}")
