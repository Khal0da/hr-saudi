import frappe
from frappe import _
from frappe.utils import getdate, date_diff


def execute(filters=None):
	if not filters:
		filters = {}

	columns = get_columns()
	data = get_data(filters)

	return columns, data


def get_columns():
	return [
		{
			"label": _("Crew"),
			"fieldname": "crew",
			"fieldtype": "Link",
			"options": "Crew",
			"width": 150
		},
		{
			"label": _("Crew Type"),
			"fieldname": "crew_type",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Supervisor"),
			"fieldname": "supervisor",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 150
		},
		{
			"label": _("Total Members"),
			"fieldname": "total_members",
			"fieldtype": "Int",
			"width": 100
		},
		{
			"label": _("Deployed Members"),
			"fieldname": "deployed_members",
			"fieldtype": "Int",
			"width": 120
		},
		{
			"label": _("Available Members"),
			"fieldname": "available_members",
			"fieldtype": "Int",
			"width": 120
		},
		{
			"label": _("Utilization %"),
			"fieldname": "utilization_percentage",
			"fieldtype": "Percent",
			"width": 120
		},
		{
			"label": _("Current Project"),
			"fieldname": "current_project",
			"fieldtype": "Link",
			"options": "Project",
			"width": 150
		},
		{
			"label": _("Current Site"),
			"fieldname": "current_site",
			"fieldtype": "Data",
			"width": 150
		}
	]


def get_data(filters):
	conditions = get_conditions(filters)
	
	crews = frappe.get_all("Crew",
		filters={"status": "Active"},
		fields=["name", "crew_type", "supervisor", "project", "site"]
	)

	data = []
	
	for crew in crews:
		members = frappe.get_all("Crew Member",
			filters={"parent": crew.name, "status": "Active"},
			fields=["name"]
		)
		total_members = len(members)
		
		# Check deployments
		deployments = frappe.get_all("Site Deployment",
			filters={
				"crew": crew.name,
				"status": "Active",
				"deployment_date": ["<=", filters.get("to_date") or getdate()],
			},
			fields=["project", "site"]
		)
		
		deployed_members = 0
		current_project = None
		current_site = None
		
		if deployments:
			# Assume all members are deployed if crew is deployed
			deployed_members = total_members
			current_project = deployments[0].project
			current_site = deployments[0].site
			
		available_members = total_members - deployed_members
		utilization = (deployed_members / total_members * 100) if total_members > 0 else 0
		
		data.append({
			"crew": crew.name,
			"crew_type": crew.crew_type,
			"supervisor": crew.supervisor,
			"total_members": total_members,
			"deployed_members": deployed_members,
			"available_members": available_members,
			"utilization_percentage": utilization,
			"current_project": current_project,
			"current_site": current_site
		})
		
	return data


def get_conditions(filters):
	conditions = ""
	if filters.get("crew_type"):
		conditions += " AND crew_type = %(crew_type)s"
	if filters.get("project"):
		conditions += " AND project = %(project)s"
	return conditions
