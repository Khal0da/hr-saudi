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
			"label": _("Employee"),
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 150
		},
		{
			"label": _("Employee Name"),
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Branch"),
			"fieldname": "branch",
			"fieldtype": "Link",
			"options": "Branch",
			"width": 120
		},
		{
			"label": _("Department"),
			"fieldname": "department",
			"fieldtype": "Link",
			"options": "Department",
			"width": 120
		},
		{
			"label": _("Project"),
			"fieldname": "custom_project",
			"fieldtype": "Link",
			"options": "Project",
			"width": 150
		},
		{
			"label": _("Crew"),
			"fieldname": "crew",
			"fieldtype": "Link",
			"options": "Crew",
			"width": 120
		},
		{
			"label": _("Present Days"),
			"fieldname": "present_days",
			"fieldtype": "Int",
			"width": 100
		},
		{
			"label": _("Absent Days"),
			"fieldname": "absent_days",
			"fieldtype": "Int",
			"width": 100
		},
		{
			"label": _("Late Days"),
			"fieldname": "late_days",
			"fieldtype": "Int",
			"width": 100
		},
		{
			"label": _("Half Days"),
			"fieldname": "half_days",
			"fieldtype": "Int",
			"width": 100
		},
		{
			"label": _("OT Hours"),
			"fieldname": "total_ot_hours",
			"fieldtype": "Float",
			"width": 100
		},
		{
			"label": _("Attendance %"),
			"fieldname": "attendance_percentage",
			"fieldtype": "Percent",
			"width": 120
		}
	]


def get_data(filters):
	conditions = get_conditions(filters)
	
	employees = frappe.get_all("Employee",
		filters={"status": "Active"},
		fields=["name", "employee_name", "branch", "department", "labor_camp"]
	)

	data = []
	total_days = date_diff(filters.get("to_date"), filters.get("from_date")) + 1

	for emp in employees:
		attendance = frappe.get_all("Attendance",
			filters={
				"employee": emp.name,
				"attendance_date": ["between", [filters.get("from_date"), filters.get("to_date")]],
				"docstatus": 1
			},
			fields=["status", "custom_late_minutes", "custom_ot_hours", "custom_project"]
		)

		present_days = sum(1 for a in attendance if a.status == "Present")
		absent_days = sum(1 for a in attendance if a.status == "Absent")
		half_days = sum(1 for a in attendance if a.status == "Half Day")
		late_days = sum(1 for a in attendance if a.custom_late_minutes and a.custom_late_minutes > 0)
		total_ot_hours = sum(a.custom_ot_hours or 0 for a in attendance)

		# Get crew assignment
		crew = frappe.db.get_value("Crew Member", {"employee": emp.name, "status": "Active"}, "parent")

		attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0

		data.append({
			"employee": emp.name,
			"employee_name": emp.employee_name,
			"branch": emp.branch,
			"department": emp.department,
			"custom_project": attendance[0].custom_project if attendance else None,
			"crew": crew,
			"present_days": present_days,
			"absent_days": absent_days,
			"late_days": late_days,
			"half_days": half_days,
			"total_ot_hours": total_ot_hours,
			"attendance_percentage": attendance_percentage
		})

	return data


def get_conditions(filters):
	conditions = ""
	if filters.get("branch"):
		conditions += " AND e.branch = %(branch)s"
	if filters.get("department"):
		conditions += " AND e.department = %(department)s"
	if filters.get("project"):
		conditions += " AND a.custom_project = %(project)s"
	if filters.get("crew"):
		conditions += " AND cm.parent = %(crew)s"
	return conditions
