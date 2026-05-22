import frappe
from frappe import _


@frappe.whitelist()
def bulk_push(logs):
	"""
	يستقبل بصمات من Biometric Bridge
	"""
	if isinstance(logs, str):
		import json
		logs = json.loads(logs)

	results = {"success": 0, "failed": 0, "duplicates": 0}

	for log in logs:
		try:
			existing = frappe.db.exists("Attendance Log", {
				"employee": log["employee_id"],
				"timestamp": log["timestamp"],
				"device": log["device_name"]
			})

			if existing:
				results["duplicates"] += 1
				continue

			employee = frappe.get_value("Employee", log["employee_id"], ["employee_name", "branch"], as_dict=True)

			att_log = frappe.get_doc({
				"doctype": "Attendance Log",
				"employee": log["employee_id"],
				"employee_name": employee.employee_name if employee else "",
				"device": log["device_name"],
				"timestamp": log["timestamp"],
				"direction": log.get("direction", "Unknown"),
				"status": "Synced",
				"sync_status": "Synced"
			})
			att_log.insert(ignore_permissions=True)
			results["success"] += 1

		except Exception as e:
			frappe.log_error(f"Bulk Push Error: {str(e)}", "Biometric Bridge")
			results["failed"] += 1

	frappe.db.commit()
	return results


@frappe.whitelist()
def get_biometric_mapping():
	"""
	يجلب جدول الربط بين أجهزة البصمة والموظفين
	"""
	mappings = frappe.get_all(
		"Biometric User Mapping",
		filters={"is_active": 1},
		fields=["employee", "device_user_id", "biometric_device"]
	)
	return mappings
