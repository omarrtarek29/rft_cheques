// Copyright (c) 2026, omar and contributors
// For license information, please see license.txt

frappe.ui.form.on("Payment Entry", {
	setup: function (frm) {
		frm.set_query("endorsed_party_type", function () {
			return {
				filters: {
					name: ["in", ["Supplier", "Customer", "Employee"]],
				},
			};
		});

		frm.set_query("endorsed_party_account", function () {
			return {
				filters: {
					account_type: ["in", ["Payable", "Receivable"]],
				},
			};
		});
	},

	cheque_number: function (frm) {
		if (frm.doc.cheque_number) {
			frm.set_value("reference_no", frm.doc.cheque_number);
		}
	},

	maturity_date: function (frm) {
		if (frm.doc.maturity_date) {
			frm.set_value("reference_date", frm.doc.maturity_date);
		}
	},

	cheque_restriction: function (frm) {
		if (frm.doc.mode_of_payment_type !== "Cheque") {
			return;
		}

		if (frm.doc.cheque_restriction === "First Beneficiary") {
			frm.set_df_property("endorsed_party_type", "read_only", 1);
			frm.set_df_property("endorsed_party_name", "read_only", 1);
			frm.set_df_property("endorsed_party_account", "read_only", 1);
			frappe.msgprint(__("First Beneficiary cheques cannot be endorsed."));
		} else {
			frm.set_df_property("endorsed_party_type", "read_only", 0);
			frm.set_df_property("endorsed_party_name", "read_only", 0);
			frm.set_df_property("endorsed_party_account", "read_only", 0);
		}
	},

	cheque_type: function (frm) {
		if (frm.doc.cheque_type === "Crossed") {
			frappe.msgprint(
				__("Crossed cheques must be deposited to bank account, cannot be cashed."),
			);
		}
	},

	cheque_action: function (frm) {
		// Validate action requirements
		if (frm.doc.cheque_action === "Endorse Cheque") {
			if (!frm.doc.endorsed_party_name || !frm.doc.endorsed_party_account) {
				frappe.msgprint(__("Please specify endorsed party and account"));
				frm.set_value("cheque_action", "");
				return;
			}
		}
	},
});
