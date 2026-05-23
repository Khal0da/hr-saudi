import frappe
from frappe.utils import get_first_day, get_last_day, flt


def execute(filters=None):
	if not filters:
		filters = {}

	columns = get_columns()
	data = get_data(filters)

	return columns, data


def get_columns():
	return [
		{
			"label": "Subcontractor",
			"fieldname": "subcontractor",
			"fieldtype": "Link",
			"options": "Supplier",
			"width": 150
		},
		{
			"label": "Worker",
			"fieldname": "worker",
			"fieldtype": "Link",
			"options": "Subcontractor Worker",
			"width": 150
		},
		{
			"label": "Worker Name",
			"fieldname": "worker_name",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "Trade",
			"fieldname": "trade",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": "Project",
			"fieldname": "project",
			"fieldtype": "Link",
			"options": "Project",
			"width": 150
		},
		{
			"label": "Present Days",
			"fieldname": "present_days",
			"fieldtype": "Int",
			"width": 100
		},
		{
			"label": "Absent Days",
			"fieldname": "absent_days",
			"fieldtype": "Int",
			"width": 100
		},
		{
			"label": "Total Hours",
			"fieldname": "total_hours",
			"fieldtype": "Float",
			"width": 100
		},
		{
			"label": "Overtime Hours",
			"fieldname": "overtime_hours",
			"fieldtype": "Float",
			"width": 120
		},
		{
			"label": "Daily Rate",
			"fieldname": "daily_rate",
			"fieldtype": "Currency",
			"width": 100
		},
		{
			"label": "Regular Amount",
			"fieldname": "regular_amount",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": "Overtime Amount",
			"fieldname": "overtime_amount",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": "Total Amount",
			"fieldname": "total_amount",
			"fieldtype": "Currency",
			"width": 120
		}
	]


def get_data(filters):
	from_date = get_first_day(f"{filters.get('year')}-{filters.get('month')}-01")
	to_date = get_last_day(f"{filters.get('year')}-{filters.get('month')}-01")

	attendance_filters = {
		"attendance_date": ["between", [from_date, to_date]],
		"docstatus": 1
	}

	if filters.get("subcontractor"):
		attendance_filters["subcontractor"] = filters.get("subcontractor")
	if filters.get("project"):
		attendance_filters["project"] = filters.get("project")

	attendance = frappe.get_all(
		"Subcontractor Attendance",
		filters=attendance_filters,
		fields=["worker", "worker_name", "subcontractor", "project", "trade", "status", "working_hours", "overtime_hours"]
	)

	# Group by worker
	worker_data = {}
	for record in attendance:
		if record.worker not in worker_data:
			worker_data[record.worker] = {
				"subcontractor": record.subcontractor,
				"worker_name": record.worker_name,
				"trade": record.trade,
				"project": record.project,
				"present_days": 0,
				"absent_days": 0,
				"total_hours": 0.0,
				"overtime_hours": 0.0
			}

		if record.status == "Present":
			worker_data[record.worker]["present_days"] += 1
		elif record.status == "Absent":
			worker_data[record.worker]["absent_days"] += 1

		worker_data[record.worker]["total_hours"] += flt(record.working_hours)
		worker_data[record.worker]["overtime_hours"] += flt(record.overtime_hours)

	# Fetch worker rates
	data = []
	for worker_id, w_data in worker_data.items():
		worker_doc = frappe.get_doc("Subcontractor Worker", worker_id)
		regular_amount = w_data["present_days"] * worker_doc.daily_rate
		overtime_amount = w_data["overtime_hours"] * worker_doc.overtime_rate
		total_amount = regular_amount + overtime_amount

		data.append({
			"subcontractor": w_data["subcontractor"],
			"worker": worker_id,
			"worker_name": w_data["worker_name"],
			"trade": w_data["trade"],
			"project": w_data["project"],
			"present_days": w_data["present_days"],
			"absent_days": w_data["absent_days"],
			"total_hours": w_data["total_hours"],
			"overtime_hours": w_data["overtime_hours"],
			"daily_rate": worker_doc.daily_rate,
			"regular_amount": regular_amount,
			"overtime_amount": overtime_amount,
			"total_amount": total_amount
		})

	return data
