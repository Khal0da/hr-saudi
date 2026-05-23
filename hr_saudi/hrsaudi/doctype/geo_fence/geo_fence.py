import frappe
from frappe.model.document import Document


class GeoFence(Document):
	def validate(self):
		self.validate_coordinates()

	def validate_coordinates(self):
		if self.latitude < -90 or self.latitude > 90:
			frappe.throw("Latitude must be between -90 and 90")
		if self.longitude < -180 or self.longitude > 180:
			frappe.throw("Longitude must be between -180 and 180")
		if self.radius_meters and self.radius_meters < 10:
			frappe.throw("Radius must be at least 10 meters")
