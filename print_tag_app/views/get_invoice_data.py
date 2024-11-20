from django.shortcuts import render
from django.db import connections
import re
from print_tag_app.models import Packing

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
