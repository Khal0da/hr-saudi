import frappe
from frappe.utils import flt, getdate


@frappe.whitelist(allow_guest=True)
def push_attendance():
	"""
	Endpoint for biometric bridge to push subcontractor attendance
	Expects: device_id, worker_id, timestamp, event_type (IN/OUT)
	"""
	data = frappe.request.get_json()
	if not data:
		return {"status": "error", "message": "No data provided"}

	results = []
	for record in data:
		try:
			worker_id = record.get("worker_id")
			timestamp = record.get("timestamp")
			event_type = record.get("event_type", "IN")

			# Find worker by biometric ID mapping
			mapping = frappe.db.get_value("Biometric User Mapping",
				{"biometric_user_id": worker_id},
				["subcontractor_worker", "subcontractor"],
				as_dict=True
			)

			if not mapping or not mapping.subcontractor_worker:
				results.append({
					"worker_id": worker_id,
					"status": "error",
					"message": "Worker not mapped"
				})
				continue

			# Create or update attendance
			attendance_date = getdate(timestamp)
			existing = frappe.db.exists("Subcontractor Attendance", {
				"worker": mapping.subcontractor_worker,
				"attendance_date": attendance_date,
				"docstatus": 0
			})

			if existing:
				doc = frappe.get_doc("Subcontractor Attendance", existing)
				if event_type == "IN" and not doc.check_in:
					doc.check_in = timestamp
				elif event_type == "OUT" and not doc.check_out:
					doc.check_out = timestamp
				doc.save()
			else:
				doc = frappe.get_doc({
					"doctype": "Subcontractor Attendance",
					"worker": mapping.subcontractor_worker,
					"subcontractor": mapping.subcontractor,
					"attendance_date": attendance_date,
					"check_in": timestamp if event_type == "IN" else None,
					"check_out": timestamp if event_type == "OUT" else None,
					"source": "Biometric"
				})
				doc.insert()

			results.append({
				"worker_id": worker_id,
				"status": "success",
				"attendance": doc.name
			})

		except Exception as e:
			results.append({
				"worker_id": worker_id,
				"status": "error",
				"message": str(e)
			})

	return {"status": "success", "results": results}


@frappe.whitelist()
def get_subcontractor_dashboard(subcontractor, month=None, year=None):
	"""
	Get dashboard data for a subcontractor
	"""
	from frappe.utils import get_first_day, get_last_day, today

	if not month:
		month = getdate(today()).month
	if not year:
		year = getdate(today()).year

	first_day = get_first_day(f"{year}-{month}-01")
	last_day = get_last_day(f"{year}-{month}-01")

	# Active workers
	active_workers = frappe.db.count("Subcontractor Worker", {
		"subcontractor": subcontractor,
		"status": "Active"
	})

	# Attendance stats
	attendance = frappe.get_all("Subcontractor Attendance",
		filters={
			"subcontractor": subcontractor,
			"attendance_date": ["between", [first_day, last_day]],
			"docstatus": 1
		},
		fields=["status", "count(*) as count"],
		group_by="status"
	)

	stats = {"present": 0, "absent": 0, "half_day": 0}
	for row in attendance:
		status = row.status.lower().replace(" ", "_")
		if status in stats:
			stats[status] = row.count

	# Payroll summary
	payroll = frappe.db.get_value("Subcontractor Payroll",
		{
			"subcontractor": subcontractor,
			"month": str(month).zfill(2),
			"year": year,
			"docstatus": 1
		},
		["grand_total", "total_workers"],
		as_dict=True
	)

	return {
		"active_workers": active_workers,
		"attendance_stats": stats,
		"payroll": {
			"grand_total": payroll.grand_total if payroll else 0,
			"total_workers": payroll.total_workers if payroll else 0
		}
	}
