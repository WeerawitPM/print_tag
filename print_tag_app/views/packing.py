from django.shortcuts import render, redirect
from print_tag_app.models import Packing
from print_tag_app.form import UploadFileForm
from django.contrib import messages
import pandas as pd


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
