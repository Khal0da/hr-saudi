frappe.ui.form.on('Geo Fence', {
	refresh: function(frm) {
		frm.add_custom_button(__('Get Current Location'), function() {
			if (navigator.geolocation) {
				navigator.geolocation.getCurrentPosition(function(pos) {
					frm.set_value('latitude', pos.coords.latitude);
					frm.set_value('longitude', pos.coords.longitude);
					frm.refresh_field('latitude');
					frm.refresh_field('longitude');
					frappe.show_alert({
						message: __('Location captured successfully'),
						indicator: 'green'
					});
				});
			} else {
				frappe.msgprint(__('Geolocation is not supported by this browser'));
			}
		});
	}
});
