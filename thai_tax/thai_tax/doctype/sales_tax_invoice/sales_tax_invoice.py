# Copyright (c) 2023, Kitti U. and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.utils import add_months

class SalesTaxInvoice(Document):

	def on_update_after_submit(self):
		if self.get_doc_before_save():  # Some change is made
			# Compute Report Date
			if int(self.months_delayed) == 0:
				self.report_date = self.date
			else:
				self.report_date = add_months(self.date, int(self.months_delayed))