import frappe
from frappe.utils import flt
from erpnext.accounts.utils import get_account_currency
from erpnext.accounts.general_ledger import make_gl_entries, process_gl_map
from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry


class PaymentEntryOverrides(PaymentEntry):

	def add_tax_gl_entries(self, gl_entries):
		for d in self.get("taxes"):
			account_currency = get_account_currency(d.account_head)
			if account_currency != self.company_currency:
				frappe.throw(_("Currency for {0} must be {1}").format(d.account_head, self.company_currency))

			if self.payment_type in ("Pay", "Internal Transfer"):
				dr_or_cr = "debit" if d.add_deduct_tax == "Add" else "credit"
				rev_dr_or_cr = "credit" if dr_or_cr == "debit" else "debit"
				against = self.party or self.paid_from
			elif self.payment_type == "Receive":
				dr_or_cr = "credit" if d.add_deduct_tax == "Add" else "debit"
				rev_dr_or_cr = "credit" if dr_or_cr == "debit" else "debit"
				against = self.party or self.paid_to

			payment_account = self.get_party_account_for_taxes()
			tax_amount = d.tax_amount
			base_tax_amount = d.base_tax_amount

			gl_entries.append(
				self.get_gl_dict(
					{
						"account": d.account_head,
						"against": against,
						dr_or_cr: tax_amount,
						dr_or_cr + "_in_account_currency": base_tax_amount
						if account_currency == self.company_currency
						else d.tax_amount,
						"cost_center": d.cost_center,
						"post_net_value": True,
						# Add clear tax entry
						"against_gl_entry": d.against_gl_entry,
						# --
					},
					account_currency,
					item=d,
				)
			)

			if not d.included_in_paid_amount:
				if get_account_currency(payment_account) != self.company_currency:
					if self.payment_type == "Receive":
						exchange_rate = self.target_exchange_rate
					elif self.payment_type in ["Pay", "Internal Transfer"]:
						exchange_rate = self.source_exchange_rate
					base_tax_amount = flt((tax_amount / exchange_rate), self.precision("paid_amount"))

				gl_entries.append(
					self.get_gl_dict(
						{
							"account": payment_account,
							"against": against,
							rev_dr_or_cr: tax_amount,
							rev_dr_or_cr + "_in_account_currency": base_tax_amount
							if account_currency == self.company_currency
							else d.tax_amount,
							"cost_center": self.cost_center,
							"post_net_value": True,
							# Add clear tax entry
							"against_gl_entry": d.against_gl_entry,
							# --
						},
						account_currency,
						item=d,
					)
				)
