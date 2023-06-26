# Copyright (c) 2023, Kitti U. and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.utils import add_months


class SalesTaxInvoice(Document):
	def validate(self):
		self.compute_report_date()

	def on_update_after_submit(self):
		if self.get_doc_before_save():  # Some change is made
			self.compute_report_date()

	def compute_report_date(self):
		if int(self.months_delayed) == 0:
			self.db_set("report_date", self.date)
		else:
			self.db_set("report_date", add_months(self.date, int(self.months_delayed)))
