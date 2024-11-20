from django.shortcuts import render
from django.db import connections
from django.http import JsonResponse, HttpResponse
import requests
from print_tag_app.models import Tag, RefTag
import json

def index(request):
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

                for _ in range(4):  # สร้าง 6 tags สำหรับแต่ละ part
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