import frappe
from frappe.utils import get_datetime, time_diff


def minutes_diff(dt1, dt2):
	"""Calculate difference in minutes between two datetimes"""
	td = time_diff(str(dt1), str(dt2))
	return int(td.total_seconds() / 60)


def calculate_ot_hours(check_in, check_out, working_hours=8):
	"""
	حساب ساعات العمل الاضافي
	"""
	settings = frappe.get_single("Attendance Settings")
	multiplier = settings.ot_multiplier or 1.5

	if not check_out:
		return 0, 0

	actual_hours = minutes_diff(
		get_datetime(check_in),
		get_datetime(check_out)
	) / 60.0

	ot_hours = max(0, actual_hours - working_hours)
	payable_hours = ot_hours * multiplier

	return ot_hours, payable_hours


def calculate_pending_ot():
	"""
	حساب OT المعلق
	"""
	today = frappe.utils.today()

	attendances = frappe.get_all(
		"Attendance",
		filters={
			"attendance_date": today,
			"status": "Present",
			"docstatus": 1
		},
		fields=["name", "employee", "check_in", "check_out"]
	)

	for att in attendances:
		if att.check_in and att.check_out:
			ot_hours, payable_hours = calculate_ot_hours(
				att.check_in, att.check_out
			)

			if ot_hours > 0:
				frappe.db.set_value("Attendance", att.name, "custom_ot_hours", ot_hours)

	frappe.db.commit()
