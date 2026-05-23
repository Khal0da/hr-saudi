import frappe
from frappe.utils import today, get_datetime, time_diff


def minutes_diff(dt1, dt2):
	"""Calculate difference in minutes between two datetimes"""
	td = time_diff(str(dt1), str(dt2))
	return int(td.total_seconds() / 60)


def generate_daily_attendance(date=None):
	"""
	يولد سجلات الحضور اليومية من البصمات
	"""
	if not date:
		date = today()

	logs = frappe.get_all(
		"Attendance Log",
		filters={
			"timestamp": ["between", [f"{date} 00:00:00", f"{date} 23:59:59"]],
			"status": "Synced"
		},
		fields=["employee", "timestamp", "direction"],
		order_by="timestamp"
	)

	employee_logs = {}
	for log in logs:
		if log.employee not in employee_logs:
			employee_logs[log.employee] = []
		employee_logs[log.employee].append(log)

	settings = frappe.get_single("Attendance Settings")
	late_threshold = settings.late_threshold or 15

	for emp, emp_logs in employee_logs.items():
		if frappe.db.exists("Attendance", {
			"employee": emp,
			"attendance_date": date
		}):
			continue

		in_logs = [l for l in emp_logs if l["direction"] == "In"]
		out_logs = [l for l in emp_logs if l["direction"] == "Out"]

		if not in_logs:
			continue

		first_in = min(get_datetime(l["timestamp"]) for l in in_logs)
		last_out = max(get_datetime(l["timestamp"]) for l in out_logs) if out_logs else None

		late_minutes = 0
		expected_start = get_datetime(f"{date} 09:00:00")
		if first_in > expected_start:
			late_minutes = minutes_diff(first_in, expected_start)

		status = "Present"
		if late_minutes > (settings.half_day_threshold or 60):
			status = "Half Day"

		employee_branch = frappe.db.get_value("Employee", emp, "branch")

		attendance = frappe.get_doc({
			"doctype": "Attendance",
			"employee": emp,
			"attendance_date": date,
			"status": status,
			"check_in": first_in,
			"check_out": last_out,
		})
		attendance.insert(ignore_permissions=True)

		if late_minutes > late_threshold:
			attendance.custom_late_minutes = late_minutes
			attendance.save()

	frappe.db.commit()


def generate_end_of_day_attendance():
	"""
	يولد الحضور لنهاية اليوم - يتحقق من الغياب
	"""
	today_date = today()

	all_employees = frappe.get_all(
		"Employee",
		filters={"status": "Active"},
		fields=["name", "branch", "company"]
	)

	for emp in all_employees:
		if frappe.db.exists("Attendance", {
			"employee": emp.name,
			"attendance_date": today_date
		}):
			continue

		attendance = frappe.get_doc({
			"doctype": "Attendance",
			"employee": emp.name,
			"attendance_date": today_date,
			"status": "Absent",
		})
		attendance.insert(ignore_permissions=True)

	frappe.db.commit()
