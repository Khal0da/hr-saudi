import frappe


def execute():
	"""Add HR Saudi custom cards to the HR workspace"""
	
	workspace_name = "HR"
	
	try:
		workspace = frappe.get_doc("Workspace", workspace_name)
	except frappe.DoesNotExistError:
		frappe.log_error(f"Workspace {workspace_name} not found")
		return
	
	saudi_cards = [
		{
			"label": "Saudi Operations",
			"link_count": 5,
			"type": "Card Break",
			"hidden": 0,
			"is_query_report": 0,
			"onboard": 0,
		},
		{
			"label": "Biometric User Mapping",
			"link_to": "Biometric User Mapping",
			"link_type": "DocType",
			"type": "Link",
			"hidden": 0,
			"is_query_report": 0,
			"onboard": 0,
		},
		{
			"label": "Attendance Settings",
			"link_to": "Attendance Settings",
			"link_type": "DocType",
			"type": "Link",
			"hidden": 0,
			"is_query_report": 0,
			"onboard": 0,
		},
		{
			"label": "Geo Fence",
			"link_to": "Geo Fence",
			"link_type": "DocType",
			"type": "Link",
			"hidden": 0,
			"is_query_report": 0,
			"onboard": 0,
		},
		{
			"label": "Crew",
			"link_to": "Crew",
			"link_type": "DocType",
			"type": "Link",
			"hidden": 0,
			"is_query_report": 0,
			"onboard": 0,
		},
		{
			"label": "Site Deployment",
			"link_to": "Site Deployment",
			"link_type": "DocType",
			"type": "Link",
			"hidden": 0,
			"is_query_report": 0,
			"onboard": 0,
		},
		{
			"label": "Saudization",
			"link_count": 2,
			"type": "Card Break",
			"hidden": 0,
			"is_query_report": 0,
			"onboard": 0,
		},
		{
			"label": "Job Requisition",
			"link_to": "Job Requisition",
			"link_type": "DocType",
			"type": "Link",
			"hidden": 0,
			"is_query_report": 0,
			"onboard": 0,
		},
		{
			"label": "Saudization Settings",
			"link_to": "Saudization Settings",
			"link_type": "DocType",
			"type": "Link",
			"hidden": 0,
			"is_query_report": 0,
			"onboard": 0,
		},
	]
	
	existing_labels = [link.label for link in workspace.links if link.type == "Card Break"]
	
	for card in saudi_cards:
		if card["label"] not in existing_labels:
			workspace.append("links", card)
	
	workspace.save()
	frappe.db.commit()
	
	frappe.msgprint("Added HR Saudi cards to HR workspace")
