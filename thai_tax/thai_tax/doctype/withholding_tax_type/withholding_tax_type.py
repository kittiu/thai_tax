# Copyright (c) 2023, Kitti U. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, cstr


class WithholdingTaxType(Document):
	def on_trash(self):
		if (
			self.name == "Auto"
			and not cint(getattr(frappe.local.conf, "developer_mode", 0))
			and not (frappe.flags.in_migrate or frappe.flags.in_patch)
		):
			frappe.throw(_("You are not allowed to delete Auto"))
