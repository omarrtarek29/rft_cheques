# Copyright (c) 2026, omar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class Cheque(Document):
	def validate(self):
		self.validate_restrictions()
		self.validate_status_transitions()
		self.validate_dates()
		self.validate_amounts()

	def validate_restrictions(self):
		if self.restriction == "First Beneficiary" and self.current_status == "Endorsed":
			frappe.throw(_("First Beneficiary cheques cannot be endorsed."))

		if self.type == "Crossed" and self.current_status == "Cleared":
			if "Cash" in str(self.physical_location) or "Safe" in str(self.physical_location):
				frappe.throw(_("Crossed cheques cannot be cashed at teller. They must be deposited."))

	def validate_status_transitions(self):
		valid_transitions = {
			"Draft": ["In Hand", "Issued", "Cancelled"],
			"In Hand": ["Under Collection", "Endorsed", "Cleared", "Cancelled"],
			"Under Collection": ["Cleared", "Bounced", "Cancelled"],
			"Cleared": ["Cancelled"],
			"Bounced": ["Under Collection", "Cancelled"],
			"Endorsed": ["Under Collection", "Cleared", "Cancelled"],
			"Issued": ["Settled", "Rejected", "Cancelled"],
			"Settled": ["Cancelled"],
			"Rejected": ["Issued", "Cancelled"],
			"Cancelled": [],
		}

		if self.is_new():
			return

		old_status = self.get_doc_before_save().current_status if self.get_doc_before_save() else None
		if old_status and old_status != self.current_status:
			if self.current_status not in valid_transitions.get(old_status, []):
				frappe.throw(
					_("Invalid status transition from {0} to {1}").format(old_status, self.current_status)
				)

	def validate_dates(self):
		if self.issue_date and self.maturity_date:
			if self.maturity_date < self.issue_date:
				frappe.throw(_("Maturity Date cannot be before Issue Date"))

	def validate_amounts(self):
		if flt(self.amount) <= 0:
			frappe.throw(_("Amount must be greater than zero"))

		if flt(self.collection_fees) < 0:
			frappe.throw(_("Collection Fees cannot be negative"))

	def on_update(self):
		if self.current_status == "Endorsed" and not self.endorsed_to:
			frappe.throw(_("Please specify the supplier to whom the cheque is endorsed."))

	def create_accounting_entries(self):
		if not self.accounting_entries:
			self.generate_accounting_entries()
			self.save()

	def generate_accounting_entries(self):
		self.accounting_entries = []

		if self.category == "Incoming":
			self._handle_incoming_cheque_entries()
		elif self.category == "Outgoing":
			self._handle_outgoing_cheque_entries()

	def _handle_incoming_cheque_entries(self):
		if self.current_status == "In Hand":
			self._add_entry("Notes Under Hand", self.amount, 0)
			self._add_entry("Customer Account", 0, self.amount, party_type="Customer")

		elif self.current_status == "Endorsed":
			self._add_entry("Supplier Account", self.amount, 0, party_type="Supplier", party=self.endorsed_to)
			self._add_entry("Notes Under Hand", 0, self.amount)

		elif self.current_status == "Cleared" and self.type == "Opened":
			if "Cash" in str(self.physical_location):
				self._add_entry("Cash/Safe Account", self.amount, 0)
				self._add_entry("Notes Under Hand", 0, self.amount)
			else:
				self._add_entry("Bank Account", self.amount, 0)
				if flt(self.collection_fees) > 0:
					self._add_entry("Bank Fees Account", self.collection_fees, 0)
					self._add_entry("Notes Under Collection", 0, self.amount + flt(self.collection_fees))
				else:
					self._add_entry("Notes Under Collection", 0, self.amount)

		elif self.current_status == "Under Collection":
			self._add_entry("Notes Under Collection", self.amount, 0)
			self._add_entry("Notes Under Hand", 0, self.amount)

		elif self.current_status == "Cleared" and self.type == "Crossed":
			self._add_entry("Bank Account", self.amount, 0)
			if flt(self.collection_fees) > 0:
				self._add_entry("Bank Fees Account", self.collection_fees, 0)
				self._add_entry("Notes Under Collection", 0, self.amount + flt(self.collection_fees))
			else:
				self._add_entry("Notes Under Collection", 0, self.amount)

	def _handle_outgoing_cheque_entries(self):
		if self.current_status == "Issued":
			self._add_entry("Supplier Account", 0, self.amount, party_type="Supplier")
			self._add_entry("Notes Payable", self.amount, 0)

		elif self.current_status == "Settled":
			self._add_entry("Notes Payable", 0, self.amount)
			self._add_entry("Bank Account", self.amount, 0)

		elif self.current_status == "Rejected":
			self._add_entry("Notes Payable", 0, self.amount)
			self._add_entry("Supplier Account", self.amount, 0, party_type="Supplier")

	def _add_entry(self, account, debit, credit, party_type=None, party=None):
		entry = {
			"account": account,
			"debit": flt(debit),
			"credit": flt(credit),
			"party_type": party_type,
			"party": party,
			"reference_doctype": "Cheque",
			"reference_name": self.name,
			"remarks": f"Cheque {self.cheque_number} - {self.current_status}",
		}
		self.append("accounting_entries", entry)
