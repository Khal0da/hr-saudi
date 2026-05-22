import frappe
import math
from frappe import _


def haversine(lat1, lng1, lat2, lng2):
	"""
	حساب المسافة بين نقطتين بالامتار
	"""
	R = 6371000
	dlat = math.radians(lat2 - lat1)
	dlng = math.radians(lng2 - lng1)
	a = (
		math.sin(dlat / 2) ** 2
		+ math.cos(math.radians(lat1))
		* math.cos(math.radians(lat2))
		* math.sin(dlng / 2) ** 2
	)
	return R * 2 * math.asin(math.sqrt(a))


@frappe.whitelist()
def gps_checkin(employee_id, latitude, longitude, accuracy=None):
	"""
	تسجيل حضور عبر GPS مع Geo-Fencing
	"""
	employee = frappe.get_doc("Employee", employee_id)

	fences = frappe.get_all(
		"Geo Fence",
		filters={"is_active": 1},
		fields=["name", "latitude", "longitude", "radius_meters", "project"]
	)

	matched_fence = None
	for fence in fences:
		distance = haversine(
			float(latitude), float(longitude),
			float(fence.latitude), float(fence.longitude)
		)
		if distance <= fence.radius_meters:
			matched_fence = fence
			matched_fence["distance"] = distance
			break

	if not matched_fence:
		return {"error": "خارج نطاق أي موقع مسجل"}

	today = frappe.utils.today()
	existing = frappe.db.exists("Attendance Log", {
		"employee": employee_id,
		"timestamp": ["between", [f"{today} 00:00:00", f"{today} 23:59:59"]],
		"direction": "In"
	})

	if existing:
		return {"error": "تم تسجيل الحضور مسبقًا اليوم"}

	att_log = frappe.get_doc({
		"doctype": "Attendance Log",
		"employee": employee_id,
		"device": "Mobile GPS",
		"timestamp": frappe.utils.now(),
		"direction": "In",
		"status": "Synced",
		"sync_status": "Synced"
	})
	att_log.insert(ignore_permissions=True)
	frappe.db.commit()

	return {
		"success": True,
		"project": matched_fence["project"],
		"distance": round(matched_fence["distance"], 1)
	}


@frappe.whitelist()
def qr_checkin(employee_id, qr_data, latitude, longitude):
	"""
	تسجيل حضور عبر QR Code + GPS
	"""
	fence = frappe.db.get_value(
		"Geo Fence",
		{"qr_code": qr_data, "is_active": 1},
		["name", "latitude", "longitude", "radius_meters", "project"],
		as_dict=True
	)

	if not fence:
		return {"error": "QR Code غير صالح"}

	distance = haversine(
		float(latitude), float(longitude),
		float(fence.latitude), float(fence.longitude)
	)

	if distance > fence.radius_meters:
		return {"error": "أنت بعيد عن الموقع"}

	return gps_checkin(employee_id, latitude, longitude)


@frappe.whitelist()
def validate_geo_fence(employee_id, latitude, longitude):
	"""
	التحقق من وجود الموظف داخل نطاق موقع مسجل
	"""
	fences = frappe.get_all(
		"Geo Fence",
		filters={"is_active": 1},
		fields=["name", "latitude", "longitude", "radius_meters", "project"]
	)

	for fence in fences:
		distance = haversine(
			float(latitude), float(longitude),
			float(fence.latitude), float(fence.longitude)
		)
		if distance <= fence.radius_meters:
			return {
				"valid": True,
				"fence": fence["name"],
				"project": fence["project"],
				"distance": round(distance, 1)
			}

	return {"valid": False, "message": "خارج نطاق أي موقع"}
