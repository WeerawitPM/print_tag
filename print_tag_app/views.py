from django.shortcuts import render, redirect
from django.db import connections
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import requests
import re
from .models import Tag, RefTag, Packing, Invoice, RefInvoice
from datetime import datetime
from .form import UploadFileForm
from django.contrib import messages
import pandas as pd
import json


@csrf_exempt
def index(request):
    data = []

    if request.method == "POST":
        fcrefno = request.POST.get("fcrefno")
        with connections["formula_aaa"].cursor() as cursor:
            query = """
                SELECT TOP 100 G.FCSKID, G.FCCODE, G.FCREFNO, G.FMMEMDATA, G.FCCOOR, C.FCCODE, C.FCNAME, G.FDDATE 
                FROM GLREF AS G 
                INNER JOIN COOR AS C ON C.FCSKID = G.FCCOOR
                WHERE G.FCREFNO LIKE %s AND G.FCBOOK = %s 
                ORDER BY G.FDDATE DESC
            """
            cursor.execute(query, [f"%{fcrefno}%", "TrDEJl01"])
            data = cursor.fetchall()

            cleaned_data = []
            for row in data:
                cleaned_row = [
                    field.strip() if isinstance(field, str) else field for field in row
                ]
                # Extract and clean PO number from row[3] (the 4th field)
                po_match = re.search(r"(PO[.-]\w+)", cleaned_row[3])
                if po_match:
                    cleaned_po = po_match.group(0)
                    # Remove 'Rem' from the start, if it exists
                    cleaned_po = re.sub(r"^Rem", "", cleaned_po)
                    # Remove trailing 'Rem' if it exists
                    cleaned_po = re.sub(r"Rem$", "", cleaned_po)
                    # Remove 'PO.' or 'PO-'
                    cleaned_po = re.sub(r"^PO[.-]", "", cleaned_po)
                    cleaned_row[3] = cleaned_po
                else:
                    cleaned_row[3] = "-"  # Handle cases where no PO is found

                # Format the date
                if isinstance(cleaned_row[7], datetime):
                    cleaned_row[7] = cleaned_row[7].strftime("%d-%m-%Y")
                cleaned_data.append(cleaned_row)

            data = cleaned_data

        return render(
            request, "home/index.html", {"data": cleaned_data, "fcrefno": fcrefno}
        )
    else:
        with connections["formula_aaa"].cursor() as cursor:
            query = """
                SELECT TOP 100 G.FCSKID, G.FCCODE, G.FCREFNO, G.FMMEMDATA, G.FCCOOR, C.FCCODE, C.FCNAME, G.FDDATE 
                FROM GLREF AS G 
                INNER JOIN COOR AS C ON C.FCSKID = G.FCCOOR
                WHERE G.FCBOOK = %s 
                ORDER BY G.FDDATE DESC
            """
            cursor.execute(query, ["TrDEJl01"])
            data = cursor.fetchall()

            cleaned_data = []
            for row in data:
                cleaned_row = [
                    field.strip() if isinstance(field, str) else field for field in row
                ]
                # Extract and clean PO number from row[3] (the 4th field)
                po_match = re.search(r"(PO[.-]\w+)", cleaned_row[3])
                if po_match:
                    cleaned_po = po_match.group(0)
                    # Remove 'Rem' from the start, if it exists
                    cleaned_po = re.sub(r"^Rem", "", cleaned_po)
                    # Remove trailing 'Rem' if it exists
                    cleaned_po = re.sub(r"Rem$", "", cleaned_po)
                    # Remove 'PO.' or 'PO-'
                    cleaned_po = re.sub(r"^PO[.-]", "", cleaned_po)
                    cleaned_row[3] = cleaned_po
                else:
                    cleaned_row[3] = "-"  # Handle cases where no PO is found

                # Format the date
                if isinstance(cleaned_row[7], datetime):
                    cleaned_row[7] = cleaned_row[7].strftime("%d-%m-%Y")
                cleaned_data.append(cleaned_row)

            data = cleaned_data

        return render(
            request,
            "home/index.html",
            {
                "data": cleaned_data,
            },
        )


def autocomplete(request):
    if "term" in request.GET:
        term = request.GET.get("term")
        with connections["formula_aaa"].cursor() as cursor:
            query = """
                Select Top 10 G.FCSKID, G.FCCODE, G.FCREFNO, G.FMMEMDATA, G.FCCOOR, C.FCCODE, C.FCNAME, G.FDDATE from GLREF as G 
                INNER JOIN COOR as C ON C.FCSKID = G.FCCOOR
                WHERE G.FCREFNO LIKE %s AND G.FCBOOK = %s ORDER BY G.FDDATE DESC
            """
            cursor.execute(query, [f"%{term}%", "TrDEJl01"])
            results = cursor.fetchall()
            part_codes = [row[2].strip() for row in results]
        return JsonResponse(part_codes, safe=False)
    return JsonResponse([], safe=False)


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

                for i in range(2):
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


def get_invoice_data(request, fcskid):
    po = ""
    cust = ""

    with connections["formula_aaa"].cursor() as cursor:
        query = """
            Select G.FCSKID, G.FCCODE, G.FCREFNO, G.FMMEMDATA, G.FCCOOR, C.FCCODE, C.FCNAME, G.FDDATE, P.FCCODE, P.FCNAME, P.FCSNAME 
            from GLREF as G 
            INNER JOIN COOR as C ON C.FCSKID = G.FCCOOR
            INNER JOIN REFPROD as R ON R.FCGLREF = G.FCSKID
            INNER JOIN PROD as P ON P.FCSKID = R.FCPROD
            WHERE G.FCSKID = %s
            """
        cursor.execute(query, [fcskid])
        data = cursor.fetchall()

        cleaned_data = []
        for row in data:
            cleaned_row = [
                field.strip() if isinstance(field, str) else field for field in row
            ]
            # Extract and clean PO number from row[3] (the 4th field)
            po_match = re.search(r"(PO[.-]\w+)", cleaned_row[3])
            if po_match:
                cleaned_po = po_match.group(0)
                # Remove 'Rem' from the start, if it exists
                cleaned_po = re.sub(r"^Rem", "", cleaned_po)
                # Remove trailing 'Rem' if it exists
                cleaned_po = re.sub(r"Rem$", "", cleaned_po)
                # Remove 'PO.' or 'PO-'
                cleaned_po = re.sub(r"^PO[.-]", "", cleaned_po)
                cleaned_row[3] = cleaned_po
            else:
                cleaned_row[3] = "-"  # Handle cases where no PO is found
            cleaned_data.append(cleaned_row)
            po = cleaned_row[3]
            cust = cleaned_row[5]

            ### Packing
            stdQty = 0
            p = Packing.objects.filter(part_no=str(cleaned_row[8]).strip()).first()
            if p:
                stdQty = p.std_packing
            cleaned_row.append(stdQty)
        data = cleaned_data

    return render(
        request,
        "invoice/index.html",
        {"data": cleaned_data, "po": po, "cust": cust},
    )


def upload_packing(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES["file"]
            try:
                df = pd.read_excel(excel_file)
                for _, row in df.iterrows():
                    part_no = row["part_no"]
                    std_packing = row["std_packing"]
                    Packing.objects.update_or_create(
                        part_no=part_no,
                        defaults={"std_packing": int(std_packing)},
                    )
                messages.success(request, "Data uploaded successfully.")
                return redirect("/upload_packing")
            except Exception as e:
                messages.error(request, f"Error uploading data: {e}")
                return redirect("/upload_packing")
    else:
        form = UploadFileForm()
    return render(request, "upload_packing/index.html", {"form": form})


def product(request):
    with connections["formula_aaa"].cursor() as cursor:
        query = """
                Select FCCODE, FCNAME
                from PROD
                """
        cursor.execute(query)
        data = cursor.fetchall()

    # ใช้ list comprehension เพื่อใช้ .strip() กับแต่ละค่าใน data
    data = [(fccode.strip(), fcname.strip()) for fccode, fcname in data]

    return render(request, "product/index.html", {"data": data})


def save_product(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            cust_sup = data.get("cust_sup")
            po_no = data.get("po_no")
            selected_items = data.get("selected_items", [])

            if not cust_sup or not selected_items:
                return JsonResponse({"error": "Missing required data"}, status=400)

            ref_tag = RefTag.objects.create()
            for item in selected_items:
                part_no = item.get(f"part_no")
                part_name = item.get(f"part_name")
                qr_code = f"{part_no}${part_name}${cust_sup}"

                for _ in range(2):  # สร้าง 6 tags สำหรับแต่ละ part
                    tag = Tag.objects.create(
                        qr_code=qr_code,
                        cust_sup=cust_sup,
                        part_no=part_no,
                        part_name=part_name,
                        ref_tag=ref_tag,
                        po_no=po_no,
                    )

            # URL สำหรับล็อกอิน
            login_url = "http://192.168.20.16:8080/jasperserver/rest_v2/login?j_username=jasperadmin&j_password=jasperadmin"
            login_response = requests.get(login_url)

            if login_response.status_code == 200:
                cookies = login_response.cookies

                # URL ของรายงาน
                report_url = f"http://192.168.20.16:8080/jasperserver/rest_v2/reports/aaa_report/tags.pdf?ParmID={ref_tag}"
                report_response = requests.get(report_url, cookies=cookies)

                if report_response.status_code == 200:
                    file_name = f"report_{cust_sup}.pdf"
                    response = HttpResponse(
                        report_response.content, content_type="application/pdf"
                    )
                    response["Content-Disposition"] = (
                        f'attachment; filename="{file_name}"'
                    )
                    return response
                else:
                    return JsonResponse(
                        {"error": "Failed to retrieve the report"},
                        status=report_response.status_code,
                    )
            else:
                return JsonResponse(
                    {"error": "Login to JasperServer failed"},
                    status=login_response.status_code,
                )

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)


# def get_modal_data(request, fcskid):
#     packings = Packing.objects.all()
#     packing_dict = {
#         packing.part_no: {
#             "part_no": packing.part_no,
#             "std_packing": packing.std_packing,
#         }
#         for packing in packings
#     }

#     with connections["formula_aaa"].cursor() as cursor:
#         query = """
#             Select G.FCSKID, G.FCCODE, G.FCREFNO, G.FMMEMDATA, G.FCCOOR, C.FCCODE, C.FCNAME, G.FDDATE, P.FCCODE, P.FCNAME, P.FCSNAME
#             from GLREF as G
#             INNER JOIN COOR as C ON C.FCSKID = G.FCCOOR
#             INNER JOIN REFPROD as R ON R.FCGLREF = G.FCSKID
#             INNER JOIN PROD as P ON P.FCSKID = R.FCPROD
#             WHERE G.FCSKID = %s
#             """
#         cursor.execute(query, [fcskid])
#         data = cursor.fetchall()

#         cleaned_data = []
#         for row in data:
#             cleaned_row = [
#                 field.strip() if isinstance(field, str) else field for field in row
#             ]
#             # Extract and clean PO number from row[3] (the 4th field)
#             po_match = re.search(r"(PO[.-]\w+)", cleaned_row[3])
#             if po_match:
#                 cleaned_po = po_match.group(0)
#                 # Remove trailing 'Rem' if it exists
#                 cleaned_po = re.sub(r"Rem$", "", cleaned_po)
#                 cleaned_row[3] = cleaned_po
#             else:
#                 cleaned_row[3] = "PO Not Found"  # Handle cases where no PO is found
#             cleaned_data.append(cleaned_row)
#         data = cleaned_data

#     return JsonResponse({"data": cleaned_data, "packing": packing_dict})
