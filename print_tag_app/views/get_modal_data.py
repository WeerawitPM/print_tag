from django.db import connections
from django.http import JsonResponse
import re
from print_tag_app.models import Packing


def get_modal_data(request, fcskid):
    packings = Packing.objects.all()
    packing_dict = {
        packing.part_no: {
            "part_no": packing.part_no,
            "std_packing": packing.std_packing,
        }
        for packing in packings
    }

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
                # Remove trailing 'Rem' if it exists
                cleaned_po = re.sub(r"Rem$", "", cleaned_po)
                cleaned_row[3] = cleaned_po
            else:
                cleaned_row[3] = "PO Not Found"  # Handle cases where no PO is found
            cleaned_data.append(cleaned_row)
        data = cleaned_data

    return JsonResponse({"data": cleaned_data, "packing": packing_dict})