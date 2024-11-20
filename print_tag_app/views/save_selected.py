from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import requests
from print_tag_app.models import Tag, RefTag, Packing, Invoice, RefInvoice


@csrf_exempt
def save_selected(request):
    invoice = ""
    if request.method == "POST":
        selected_indices = request.POST.getlist("selected")

        # ตรวจสอบปุ่มที่ถูกกด
        if "print_tag" in request.POST:
            ref_tag = RefTag.objects.create()
            for index in selected_indices:
                # seq = 0
                # for r in request.POST:
                #     print(f"{seq} ==> {r}")
                #     seq += 1

                index = int(index)
                po_no = request.POST.get(f"po_no_{index}")
                cust_sup = request.POST.get(f"cust_sup_{index}")
                if cust_sup == "ALT":
                    cust_sup = "115047"
                else:
                    pass
                part_name = request.POST.get(f"part_name_{index}")
                part_no = request.POST.get(f"part_no_{index}")
                lot_mat = request.POST.get(f"lot_mat_{index}")
                lot_prod = request.POST.get(f"lot_prod_{index}")
                model = request.POST.get(f"model_{index}")
                mc = request.POST.get(f"mc_{index}")
                date = request.POST.get(f"date")
                qty = request.POST.get(f"packing_{index}")
                qr_code = f"{part_no}${qty}${po_no}${cust_sup}"

                Packing.objects.update_or_create(
                    part_no=part_no,
                    defaults={"std_packing": int(qty)},
                )

                for i in range(4):
                    tag = Tag()
                    tag.qr_code = qr_code
                    tag.po_no = po_no
                    tag.cust_sup = cust_sup
                    tag.part_name = part_name
                    tag.part_no = part_no
                    tag.lot_mat = lot_mat
                    tag.lot_prod = lot_prod
                    tag.model = model
                    tag.mc = mc
                    tag.qty = qty
                    tag.ref_tag = ref_tag
                    if date and len(date) > 0:
                        tag.date = date
                    tag.save()
                    # Tag.objects.create(
                    #     qr_code=qr_code,
                    #     po_no=po_no,
                    #     cust_sup=cust_sup,
                    #     part_name=part_name,
                    #     part_no=part_no,
                    #     lot_mat=lot_mat,
                    #     lot_prod=lot_prod,
                    #     model=model,
                    #     mc=mc,
                    #     date=date,
                    #     qty=qty,
                    #     ref_tag=ref_tag
                    # )

            # URL สำหรับล็อกอิน
            login_url = "http://192.168.20.16:8080/jasperserver/rest_v2/login?j_username=jasperadmin&j_password=jasperadmin"
            login_response = requests.get(login_url)

            if login_response.status_code == 200:
                cookies = login_response.cookies

                # URL ของรายงาน
                report_url = f"http://192.168.20.16:8080/jasperserver/rest_v2/reports/aaa_report/tags.pdf?ParmID={ref_tag}"
                print(report_url)
                report_response = requests.get(report_url, cookies=cookies)
                print(report_response)

                if report_response.status_code == 200:
                    file_name = f"report_{part_name}"
                    response = HttpResponse(
                        report_response.content, content_type="application/pdf"
                    )
                    response["Content-Disposition"] = (
                        f'attachment; filename="{file_name}.pdf"'
                    )
                    return response
                else:
                    return HttpResponse(
                        "Failed to retrieve the report",
                        status=report_response.status_code,
                    )
            else:
                return HttpResponse(
                    "Login to JasperServer failed", status=login_response.status_code
                )

        if "print_invoice" in request.POST:
            ref_invoice = RefInvoice.objects.create()
            po_no = None
            cust_sup = None
            invoice = None
            seq = 0
            for r in request.POST:
                print(f"{seq} ==> {r}")
                if seq == 1:
                    invoice = request.POST.get(r)
                elif seq == 2:
                    po_no = request.POST.get(r)
                elif seq == 4:
                    cust_sup = request.POST.get(r)
                    if cust_sup == "ALT":
                        cust_sup = "115047"
                    else:
                        pass
                seq += 1

            qr_code = f"{po_no}${invoice}${cust_sup}"
            Invoice.objects.create(
                qr_code=qr_code,
                invoice=invoice,
                po_no=po_no,
                cust_sup=cust_sup,
                ref_invoice=ref_invoice,
            )

            # URL สำหรับล็อกอิน
            login_url = "http://192.168.20.16:8080/jasperserver/rest_v2/login?j_username=jasperadmin&j_password=jasperadmin"
            login_response = requests.get(login_url)

            if login_response.status_code == 200:
                cookies = login_response.cookies

                # URL ของรายงาน
                report_url = f"http://192.168.20.16:8080/jasperserver/rest_v2/reports/aaa_report/Invoice_QRCODE_AAA.pdf?ParmID={ref_invoice}"
                print(report_url)
                report_response = requests.get(report_url, cookies=cookies)
                print(report_response)

                if report_response.status_code == 200:
                    file_name = f"report_{invoice}"
                    response = HttpResponse(
                        report_response.content, content_type="application/pdf"
                    )
                    response["Content-Disposition"] = (
                        f'attachment; filename="{file_name}.pdf"'
                    )
                    return response
                else:
                    return HttpResponse(
                        "Failed to retrieve the report",
                        status=report_response.status_code,
                    )
            else:
                return HttpResponse(
                    "Login to JasperServer failed", status=login_response.status_code
                )

    return redirect("/")
