frappe.ui.form.on("Withholding Tax Cert", {
	refresh(frm) {
		frm.set_query("company_address", function (doc) {
			return {
				query: "frappe.contacts.doctype.address.address.address_query",
				filters: {
					link_doctype: "Company",
					link_name: doc.company,
				},
			};
		});
		frm.set_query("voucher_type", function () {
			return {
				filters: {
					name: ["in", ["Payment Entry", "Journal Entry"]],
				},
			};
		});
	},
});

frappe.ui.form.on("Withholding Tax Items", {
	// Helper to calculate tax amount from given rate
	tax_rate: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "tax_amount", (row.tax_base * row.tax_rate) / 100);
	},
	// Auto assign income type description
	type_of_income: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		var vals = {
			1: "เงินเดือน ค่าจ้าง ฯลฯ 40(1)",
			2: "ค่าธรรมเนียม ค่านายหน้า ฯลฯ 40(2)",
			3: "ค่าแห่งลิขสิทธิ์ ฯลฯ 40(3)",
			4: "ดอกเบี้ย ฯลฯ 40(4)ก",
			"4.1.1":
				"เงินปันผล เงินส่วนแบ่งกำไร ฯลฯ 40(4)ข (1.1) กิจการที่ต้องเสียภาษีเงินได้นิติบุคคลร้อยละ 30 ของกำไรสุทธิ",
			"4.1.2":
				"เงินปันผล เงินส่วนแบ่งกำไร ฯลฯ 40(4)ข (1.2) กิจการที่ต้องเสียภาษีเงินได้นิติบุคคลร้อยละ 25 ของกำไรสุทธิ",
			"4.1.3":
				"เงินปันผล เงินส่วนแบ่งกำไร ฯลฯ 40(4)ข (1.3) กิจการที่ต้องเสียภาษีเงินได้นิติบุคคลร้อยละ 20 ของกำไรสุทธิ",
			"4.1.4":
				"เงินปันผล เงินส่วนแบ่งกำไร ฯลฯ 40(4)ข (1.4) กิจการที่ต้องเสียภาษีเงินได้นิติบุคคลร้อยละ อื่นๆ (ระบุ) ของกำไรสุทธิ",
			"4.2.1":
				"เงินปันผล เงินส่วนแบ่งกำไร ฯลฯ 40(4)ข (2.1) กำไรสุทธิกิจการที่ได้รับยกเว้นภาษีเงินได้นิติบุคคล",
			"4.2.2":
				"เงินปันผล เงินส่วนแบ่งกำไร ฯลฯ 40(4)ข (2.2) ได้รับยกเว้นไม่ต้องนำมารวมคำนวณเป็นรายได้",
			"4.2.3":
				"เงินปันผล เงินส่วนแบ่งกำไร ฯลฯ 40(4)ข (2.3) กำไรสุทธิส่วนที่หักผลขาดทุนสุทธิยกมาไม่เกิน 5 ปี",
			"4.2.4":
				"เงินปันผล เงินส่วนแบ่งกำไร ฯลฯ 40(4)ข (2.4) กำไรที่รับรู้ทางบัญชีโดยวิธีส่วนได้เสีย",
			"4.2.5": "เงินปันผล เงินส่วนแบ่งกำไร ฯลฯ 40(4)ข (2.5) อื่นๆ (ระบุ)",
			5: "ค่าจ้างทำของ ค่าบริการ ค่าเช่า ค่าขนส่ง ฯลฯ 3 เตรส",
			6: "อื่นๆ (ระบุ)",
		};
		frappe.model.set_value(cdt, cdn, "description", vals[row.type_of_income]);
	},
});
