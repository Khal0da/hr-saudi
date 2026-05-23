import frappe


def execute():
	"""Add HR Saudi custom cards to the HR workspace"""
	
	workspace_name = "HR"
	
	try:
		workspace = frappe.get_doc("Workspace", workspace_name)
	except frappe.DoesNotExistError:
		frappe.log_error(f"Workspace {workspace_name} not found")
		return
	
	saudi_links = [
		{
			"label": "Saudi Operations",
			"type": "Card Break",
			"links": [
				"Biometric User Mapping",
				"Attendance Settings",
				"Geo Fence",
				"Crew",
				"Site Deployment",
				"Document Expiry Tracker",
			]
		},
		{
			"label": "Saudization",
			"type": "Card Break",
			"links": [
				"Job Requisition",
				"Saudization Settings",
			]
		},
		{
			"label": "Subcontractor Management",
			"type": "Card Break",
			"links": [
				"Subcontractor Worker",
				"Subcontractor Attendance",
				"Subcontractor Payroll",
			]
		},
		{
			"label": "Subcontractor Reports",
			"type": "Card Break",
			"links": [
				"Subcontractor Utilization",
			]
		},
	]
	
	existing_labels = [link.label for link in workspace.links if link.type == "Card Break"]
	
	for card in saudi_links:
		if card["label"] not in existing_labels:
			valid_links = [l for l in card["links"] if frappe.db.exists("DocType", l)]
			
			if valid_links:
				workspace.append("links", {
					"label": card["label"],
					"link_count": len(valid_links),
					"type": "Card Break",
					"hidden": 0,
					"is_query_report": 0,
					"onboard": 0,
				})
				
				for link_name in valid_links:
					workspace.append("links", {
						"label": link_name,
						"link_to": link_name,
						"link_type": "DocType",
						"type": "Link",
						"hidden": 0,
						"is_query_report": 0,
						"onboard": 0,
					})
		
		# Add reports as query reports
		if card["label"] == "Subcontractor Reports":
			report_name = "Subcontractor Utilization"
			if frappe.db.exists("Report", report_name):
				workspace.append("links", {
					"label": report_name,
					"link_to": report_name,
					"link_type": "Report",
					"type": "Link",
					"hidden": 0,
					"is_query_report": 1,
					"onboard": 0,
				})
	
	workspace.save()
	frappe.db.commit()
	
	frappe.msgprint("Added HR Saudi cards to HR workspace")
