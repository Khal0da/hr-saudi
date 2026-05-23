import frappe
from frappe import _
from frappe.utils import get_time, time_diff_in_minutes, today


def validate_attendance(doc, method=None):
	"""
	التحقق من سجل الحضور
	"""
	if doc.employee and doc.attendance_date:
		existing = frappe.db.get_value(
			"Attendance",
			{
				"employee": doc.employee,
				"attendance_date": doc.attendance_date,
				"name": ["!=", doc.name]
			},
			"name"
		)

		if existing:
			frappe.throw(
				_("Attendance already exists for employee {0} on {1}").format(
					doc.employee, doc.attendance_date
				)
			)

	if doc.employee:
		branch = frappe.db.get_value("Employee", doc.employee, "branch")
		if branch:
			doc.branch = branch
	
	# Calculate late minutes and apply grace period
	if doc.employee and doc.in_time and doc.attendance_date:
		settings = frappe.get_single("Attendance Settings")
		expected_time = settings.expected_start_time or "09:00:00"
		grace_period = settings.grace_period or 10
		late_threshold = settings.late_threshold or 15
		
		in_time = get_time(doc.in_time)
		expected = get_time(expected_time)
		
		# Calculate total late minutes (after grace period)
		total_late = time_diff_in_minutes(in_time, expected)
		
		if total_late > 0:
			# Apply grace period
			effective_late = max(0, total_late - grace_period)
			
			if effective_late > late_threshold:
				doc.status = "Late"
				doc.custom_late_minutes = int(effective_late)
				
				# Check for late deduction
				if settings.late_deduction_enabled and effective_late > settings.late_deduction_after_minutes:
					doc.custom_late_deduction = settings.late_deduction_amount
				
				# Send late notification
				if settings.send_late_notification:
					send_late_notification(doc, effective_late)


def send_late_notification(attendance_doc, late_minutes):
	"""Send email notification for late attendance"""
	try:
		settings = frappe.get_single("Attendance Settings")
		employee = frappe.get_doc("Employee", attendance_doc.employee)
		
		subject = f"Late Attendance Alert - {employee.employee_name}"
		message = f"""
		<p>Employee: {employee.employee_name}</p>
		<p>Employee ID: {attendance_doc.employee}</p>
		<p>Date: {attendance_doc.attendance_date}</p>
		<p>Late by: {late_minutes} minutes</p>
		<p>In Time: {attendance_doc.in_time}</p>
		"""
		
		if settings.late_deduction_enabled and late_minutes > settings.late_deduction_after_minutes:
			message += f"<p><strong>Late Deduction Applied: SAR {settings.late_deduction_amount}</strong></p>"
		
		frappe.sendmail(
			recipients=[settings.late_notification_email or "hr@company.com"],
			subject=subject,
			message=message,
			delayed=False
		)
	except Exception as e:
		frappe.log_error(f"Failed to send late notification: {str(e)}")
