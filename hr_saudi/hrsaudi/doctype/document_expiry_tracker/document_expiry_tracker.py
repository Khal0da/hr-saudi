import frappe
from frappe import _
from frappe.utils import today, date_diff


def validate_expiry_dates(doc, method=None):
	"""
	التحقق من تاريخ انتهاء الوثائق عند حفظ الموظف
	"""
	documents = [
		{"field": "national_id_expiry", "label": "National ID/Iqama"},
		{"field": "passport_expiry", "label": "Passport"},
		{"field": "work_permit_expiry", "label": "Work Permit"},
		{"field": "health_certificate_expiry", "label": "Health Certificate"},
	]

	for doc_item in documents:
		if doc.get(doc_item["field"]):
			expiry_date = doc.get(doc_item["field"])
			days_left = date_diff(expiry_date, today())

			if days_left < 0:
				frappe.msgprint(
					_("Warning: {0} has expired ({1} days ago)").format(
						doc_item["label"], abs(days_left)
					),
					alert=True
				)
			elif days_left <= 30:
				frappe.msgprint(
					_("Warning: {0} expires in {1} days").format(
						doc_item["label"], days_left
					),
					alert=True
				)
