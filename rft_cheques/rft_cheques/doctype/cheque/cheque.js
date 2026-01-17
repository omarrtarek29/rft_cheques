// Copyright (c) 2026, omar and contributors
// For license information, please see license.txt

frappe.ui.form.on("Cheque", {
	refresh: function (frm) {
		frm.disable();
		// if (frm.doc.restriction === "First Beneficiary") {
		// 	frm.set_df_property("endorsed_to", "read_only", 1);
		// }
		// frm.trigger("change_status_options");
	},
});
// 	category: function (frm) {
// 		if (frm.doc.category === "Incoming") {
// 			frm.set_value("current_status", "In Hand");
// 		} else if (frm.doc.category === "Outgoing") {
// 			frm.set_value("current_status", "Issued");
// 		}
// 		frm.trigger("change_status_options");
// 	},

// 	type: function (frm) {
// 		if (frm.doc.type === "Crossed" && frm.doc.current_status === "Cleared") {
// 			frappe.msgprint(__("Crossed cheques cannot be cashed at teller."));
// 		}
// 		frm.trigger("change_status_options");
// 	},

// 	restriction: function (frm) {
// 		if (frm.doc.restriction === "First Beneficiary") {
// 			frm.set_value("endorsed_to", "");
// 			frm.set_df_property("endorsed_to", "read_only", 1);
// 			frappe.msgprint(__("First Beneficiary cheques cannot be endorsed."));
// 		} else {
// 			frm.set_df_property("endorsed_to", "read_only", 0);
// 		}
// 	},

// 	current_status: function (frm) {
// 		if (frm.doc.current_status === "Endorsed" && !frm.doc.endorsed_to) {
// 			frappe.msgprint(__("Please specify the supplier to whom the cheque is endorsed."));
// 		}

// 		if (frm.doc.current_status === "Under Collection") {
// 			frm.set_value("physical_location", "At Bank");
// 		} else if (frm.doc.current_status === "In Hand") {
// 			frm.set_value("physical_location", "Main Safe");
// 		}
// 	},
// 	change_status_options: function (frm) {
// 		if (frm.doc.type === "Crossed") {
// 			frm.set_df_property(
// 				"current_status",
// 				"options",
// 				"Draft\nIn Hand\nUnder Collection\nCleared\nBounced\nCancelled\nIssued\nSettled\nRejected",
// 			);
// 		}
// 		if (frm.doc.category === "Incoming" && frm.doc.type === "Opened") {
// 			frm.set_df_property(
// 				"current_status",
// 				"options",
// 				"Draft\nIn Hand\nUnder Collection\nCleared\nBounced\nEndorsed\nCancelled",
// 			);
// 		}
// 		frm.refresh_fields("current_status");
// 	},
// });
