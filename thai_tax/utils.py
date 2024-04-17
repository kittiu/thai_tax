import frappe
import zeep
from frappe import _
from num2words import num2words
from requests import Session
from zeep import Client
from zeep.transports import Transport


def amount_in_bahttext(amount):
	return num2words(amount, to="currency", lang="th")


@frappe.whitelist()
def get_address_by_tax_id(tax_id=False, branch=False):
	if not (tax_id and branch):
		frappe.throw(_("Please provide Tax ID and Branch"))
	session = Session()
	session.verify = False
	transport = Transport(session=session)
	client = Client(
		"https://rdws.rd.go.th/serviceRD3/vatserviceRD3.asmx?wsdl", transport=transport
	)
	result = client.service.Service(
		username="anonymous",
		password="anonymous",
		TIN=tax_id,
		ProvinceCode=0,
		BranchNumber=int(branch.isnumeric() and branch or "0"),
		AmphurCode=0,
	)
	result = zeep.helpers.serialize_object(result)
	data = {}
	for k in result.keys():
		if k == "vmsgerr" and result[k] is not None:
			frappe.throw(result[k].get("anyType", None)[0])
		if result[k] is not None:
			v = result[k].get("anyType", None)[0]
			data.update({k: v})
	return finalize_address_dict(data)


def finalize_address_dict(data):
	def get_part(data, key, value):
		return data.get(key, "-") != "-" and value % (map[key], data.get(key)) or ""

	map = {
		"vBuildingName": "อาคาร",
		"vFloorNumber": "ชั้น",
		"vVillageName": "หมู่บ้าน",
		"vRoomNumber": "ห้อง",
		# "vHouseNumber": "เลขที่",
		"vMooNumber": "หมู่ที่",
		"vSoiName": "ซอย",
		"vStreetName": "ถนน",
		"vThambol": "ต.",
		"vAmphur": "อ.",
		"vProvince": "จ.",
	}
	name = "{} {}".format(data.get("vtitleName"), data.get("vName"))
	if data.get("vSurname", "-") != "-":
		name = "{} {}".format(name, data["vSurname"])
	house = data.get("vHouseNumber", "")
	village = get_part(data, "vVillageName", "%s %s")
	soi = get_part(data, "vSoiName", "%s %s")
	moo = get_part(data, "vMooNumber", "%s %s")
	building = get_part(data, "vBuildingName", "%s %s")
	floor = get_part(data, "vFloorNumber", "%s %s")
	room = get_part(data, "vRoomNumber", "%s %s")
	street = get_part(data, "vStreetName", "%s%s")
	thambon = get_part(data, "vThambol", "%s%s")
	amphur = get_part(data, "vAmphur", "%s%s")
	province = get_part(data, "vProvince", "%s%s")
	postal = data.get("vPostCode", "")

	if province == "จ.กรุงเทพมหานคร":
		thambon = data.get("vThambol") and "แขวง%s" % data["vThambol"] or ""
		amphur = data.get("vAmphur") and "เขต%s" % data["vAmphur"] or ""
		province = data.get("vProvince") and "%s" % data["vProvince"] or ""

	address_parts = filter(
		lambda x: x != "", [house, village, soi, moo, building, floor, room, street]
	)
	return {
		"name": name,
		"address_line1": " ".join(address_parts),
		"city": thambon,
		"county": amphur,
		"state": province,
		"pincode": postal,
	}
