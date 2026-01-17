# Copyright (c) 2026, omar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def create_cheque_from_payment_entry(doc, method):
	"""Create Cheque doctype record when Payment Entry is submitted with cheque fields filled"""
	validate_cheque_fields(doc)
	cheque = frappe.new_doc("Cheque")
	cheque.cheque_number = doc.cheque_number
	cheque.category = "Incoming" if doc.payment_type == "Receive" else "Outgoing"
	cheque.type = doc.cheque_type or "Opened"
	cheque.restriction = doc.cheque_restriction or "None"
	cheque.currency = (
		doc.paid_to_account_currency
		or doc.company_currency
		or frappe.get_cached_value("Company", doc.company, "default_currency")
	)
	cheque.amount = flt(doc.paid_amount)
	cheque.issue_date = doc.posting_date
	cheque.maturity_date = doc.maturity_date or doc.posting_date
	cheque.current_status = doc.current_status

	if doc.payment_type == "Receive":
		cheque.issuer_name = doc.party or ""
		cheque.beneficiary_name = doc.company or ""
	else:
		cheque.issuer_name = doc.company or ""
		cheque.beneficiary_name = doc.party or ""

	cheque.issuer_bank = doc.issuer_bank
	cheque.issuer_branch = doc.issuer_branch or ""

	cheque.bank_account_no = doc.custom_bank_account_no or ""

	cheque.related_transaction_type = "Payment Entry"
	cheque.related_transaction = doc.name

	cheque.insert()

	frappe.db.set_value("Payment Entry", doc.name, "linked_cheque", cheque.name)
	frappe.msgprint(
		_(
			f"Cheque <a href='/app/cheque/{cheque.name}'>{cheque.name}</a> created successfully from Payment Entry"
		)
	)


def validate_cheque_fields(doc):
	if doc.mode_of_payment_type != "Cheque" or doc.linked_cheque:
		return

	if not doc.cheque_number:
		frappe.throw(_("Cheque Number is required when creating a new cheque"))

	if not doc.cheque_type:
		frappe.throw(_("Cheque Type is required when creating a new cheque"))

	if not doc.issuer_bank:
		frappe.throw(_("Issuer Bank is required when creating a new cheque"))

	if not doc.current_status:
		frappe.throw(_("Current Status is required when creating a new cheque"))

	if not doc.maturity_date:
		frappe.throw(_("Maturity Date is required when creating a new cheque"))
