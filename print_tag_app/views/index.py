from django.shortcuts import render
from django.db import connections
from django.views.decorators.csrf import csrf_exempt
import re
from datetime import datetime
from django.http import JsonResponse


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
