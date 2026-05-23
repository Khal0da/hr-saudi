import frappe
from frappe.utils import today, add_days, date_diff


def check_expiring_documents():
	"""
	فحص الوثائق المنتهية وإرسال تنبيهات
	"""
	today_date = today()
	documents = [
		{"field": "national_id_expiry", "label": "National ID/Iqama", "days": [60, 30, 7]},
		{"field": "passport_expiry", "label": "Passport", "days": [90, 60, 30]},
		{"field": "work_permit_expiry", "label": "Work Permit", "days": [60, 30, 7]},
		{"field": "health_certificate_expiry", "label": "Health Certificate", "days": [30, 15, 7]},
	]

	for doc in documents:
		for days_before in doc["days"]:
			expiry_date = add_days(today_date, days_before)

			employees = frappe.get_all(
				"Employee",
				filters={
					"status": "Active",
					doc["field"]: ["between", [today_date, expiry_date]]
				},
				fields=["name", "employee_name", doc["field"], "company_email"]
			)

			for emp in employees:
				days_left = date_diff(expiry_date, today_date)
				send_expiry_notification(emp, doc["label"], days_left)


def send_expiry_notification(employee, doc_label, days_left):
	"""إرسال تنبيه انتهاء وثيقة"""
	try:
		frappe.get_doc({
			"doctype": "Notification Log",
			"subject": f"تنبيه: انتهاء {doc_label} خلال {days_left} يوم",
			"email_content": f"""
				السيد/ {employee.employee_name}<br>
				{doc_label} سينتهي خلال {days_left} يوم.<br>
				يرجى التجديد في أقرب وقت.
			""",
			"for_user": employee.company_email or employee.name,
			"type": "Alert",
		}).insert(ignore_permissions=True)
		frappe.db.commit()
	except Exception:
		pass
