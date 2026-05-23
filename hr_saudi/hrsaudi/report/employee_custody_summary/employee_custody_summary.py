import frappe
from frappe.utils import flt


def execute(filters=None):
	if not filters:
		filters = {}

	columns = get_columns()
	data = get_data(filters)

	return columns, data


def get_columns():
	return [
		{
			"label": "Custody ID",
			"fieldname": "custody_id",
			"fieldtype": "Link",
			"options": "Employee Custody",
			"width": 130
		},
		{
			"label": "Employee",
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 130
		},
		{
			"label": "Employee Name",
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "Department",
			"fieldname": "department",
			"fieldtype": "Link",
			"options": "Department",
			"width": 120
		},
		{
			"label": "Project",
			"fieldname": "project",
			"fieldtype": "Link",
			"options": "Project",
			"width": 130
		},
		{
			"label": "Custody Date",
			"fieldname": "custody_date",
			"fieldtype": "Date",
			"width": 110
		},
		{
			"label": "Status",
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "Item Code",
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 120
		},
		{
			"label": "Item Name",
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "Custody Type",
			"fieldname": "custody_type",
			"fieldtype": "Link",
			"options": "Custody Type",
			"width": 120
		},
		{
			"label": "Serial Number",
			"fieldname": "serial_number",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "Quantity",
			"fieldname": "quantity",
			"fieldtype": "Int",
			"width": 80
		},
		{
			"label": "Condition",
			"fieldname": "condition",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": "Estimated Value",
			"fieldname": "estimated_value",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": "Return Date",
			"fieldname": "return_date",
			"fieldtype": "Date",
			"width": 110
		},
		{
			"label": "Return Condition",
			"fieldname": "return_condition",
			"fieldtype": "Data",
			"width": 130
		}
	]


def get_data(filters):
	custody_filters = {"docstatus": 1}
	if filters.get("employee"):
		custody_filters["employee"] = filters.get("employee")
	if filters.get("department"):
		custody_filters["department"] = filters.get("department")
	if filters.get("status"):
		custody_filters["status"] = filters.get("status")
	if filters.get("project"):
		custody_filters["project"] = filters.get("project")

	custodies = frappe.get_all("Employee Custody",
		filters=custody_filters,
		fields=["name", "employee", "employee_name", "department", "project", "custody_date", "status"]
	)

	data = []
	for custody in custodies:
		custody_doc = frappe.get_doc("Employee Custody", custody.name)
		for item in custody_doc.items:
			if filters.get("custody_type") and item.custody_type != filters.get("custody_type"):
				continue

			data.append({
				"custody_id": custody.name,
				"employee": custody.employee,
				"employee_name": custody.employee_name,
				"department": custody.department,
				"project": custody.project,
				"custody_date": custody.custody_date,
				"status": custody.status,
				"item_code": item.item_code,
				"item_name": item.item_name,
				"custody_type": item.custody_type,
				"serial_number": item.serial_number,
				"quantity": item.quantity,
				"condition": item.condition,
				"estimated_value": item.estimated_value,
				"return_date": item.return_date,
				"return_condition": item.return_condition
			})

	return data
