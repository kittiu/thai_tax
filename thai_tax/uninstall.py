import frappe
from thai_tax.constants import HRMS_CUSTOM_FIELDS


def before_app_uninstall(app_name):
	if app_name == "hrms":
		delete_custom_fields(HRMS_CUSTOM_FIELDS)


def delete_custom_fields(custom_fields):
    """ Helper function to delete custom fields """
    for doctypes, fields in custom_fields.items():
        if isinstance(fields, dict):
            fields = [fields]
        if isinstance(doctypes, str):
            doctypes = (doctypes,)
        for doctype in doctypes:
            frappe.db.delete(
                "Custom Field",
                {
                    "fieldname": ("in", [field["fieldname"] for field in fields]),
                    "dt": doctype,
                },
            )
            frappe.clear_cache(doctype=doctype)
