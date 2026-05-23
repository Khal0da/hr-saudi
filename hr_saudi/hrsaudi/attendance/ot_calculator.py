import frappe
from frappe import _
from frappe.utils import get_datetime, time_diff, today


def calculate_dynamic_ot(employee, check_in, check_out):
	"""
	حساب العمل الإضافي الديناميكي بناءً على:
	- نوع اليوم (عادي، إجازة، عطلة أسبوعية)
	- وقت الشيفت (ليلي، نهاري)
	- درجة الموظف
	- نوع المشروع
	"""
	if not check_out:
		return 0, 0
		
	check_in_dt = get_datetime(check_in)
	check_out_dt = get_datetime(check_out)
	
	# Calculate total hours
	total_hours = time_diff(str(check_out_dt), str(check_in_dt)).total_seconds() / 3600
	
	# Get employee details
	emp = frappe.get_doc("Employee", employee)
	grade = emp.get("employee_grade") or ""
	project = emp.get("custom_project") or ""
	
	# Determine multiplier based on various factors
	multiplier = 1.5  # Default
	
	# Grade-based multiplier
	if "Executive" in grade or "Management" in grade:
		multiplier = 2.0
	elif "Professional" in grade:
		multiplier = 1.75
		
	# Time-based multiplier (Night shift)
	if check_in_dt.hour >= 22 or check_in_dt.hour <= 6:
		multiplier *= 1.25  # 25% extra for night shift
		
	# Day-based multiplier (Weekend/Holiday)
	day_of_week = check_in_dt.weekday()
	if day_of_week >= 5:  # Friday/Saturday (Saudi weekend)
		multiplier *= 1.5
	elif frappe.db.exists("Holiday", {"holiday_date": check_in_dt.date()}):
		multiplier *= 2.0  # Double time on holidays
		
	# Project-based multiplier (High risk projects)
	if project:
		project_type = frappe.db.get_value("Project", project, "custom_project_type")
		if project_type == "High Risk":
			multiplier *= 1.2
			
	ot_hours = max(0, total_hours - 8)  # Standard 8 hours
	payable_hours = ot_hours * multiplier
	
	return round(ot_hours, 2), round(payable_hours, 2)


@frappe.whitelist()
def calculate_ot_for_attendance(attendance_name):
	"""
	Calculate OT for a specific attendance record
	"""
	att = frappe.get_doc("Attendance", attendance_name)
	
	if not att.check_in or not att.check_out:
		return 0, 0
		
	ot_hours, payable_hours = calculate_dynamic_ot(
		att.employee,
		att.check_in,
		att.check_out
	)
	
	# Update attendance record
	att.db_set("custom_ot_hours", payable_hours)
	
	return ot_hours, payable_hours


def calculate_daily_ot():
	"""
	Scheduler job to calculate OT for all attendance records of the day
	"""
	today_date = today()
	
	attendances = frappe.get_all("Attendance",
		filters={
			"attendance_date": today_date,
			"status": "Present",
			"docstatus": 1,
			"custom_ot_hours": 0
		},
		fields=["name", "employee", "check_in", "check_out"]
	)
	
	for att in attendances:
		try:
			ot_hours, payable_hours = calculate_dynamic_ot(
				att.employee,
				att.check_in,
				att.check_out
			)
			
			if payable_hours > 0:
				frappe.db.set_value("Attendance", att.name, "custom_ot_hours", payable_hours)
				
		except Exception as e:
			frappe.log_error(f"OT Calculation Error: {str(e)}", "Dynamic OT Engine")
			
	frappe.db.commit()
