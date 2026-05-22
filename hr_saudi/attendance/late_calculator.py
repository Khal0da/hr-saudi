import frappe
from frappe.utils import time_diff_in_minutes, get_datetime


def calculate_late_minutes(check_in_time, expected_start="09:00:00"):
	"""
	حساب دقائق التأخير
	"""
	settings = frappe.get_single("Attendance Settings")
	threshold = settings.late_threshold or 15

	check_in = get_datetime(check_in_time)
	expected = get_datetime(f"{check_in.date()} {expected_start}")

	if check_in <= expected:
		return 0

	late = time_diff_in_minutes(check_in, expected)

	if late <= threshold:
		return 0

	return late


def calculate_ot_hours(check_in, check_out, working_hours=8):
	"""
	حساب ساعات العمل الاضافي
	"""
	if not check_out:
		return 0

	actual_hours = time_diff_in_minutes(
		get_datetime(check_in),
		get_datetime(check_out)
	) / 60.0

	ot = actual_hours - working_hours
	return max(0, ot)
