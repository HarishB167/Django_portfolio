import os
from django.shortcuts import render, HttpResponse

from .utils import load_workbook_from_url, get_sheet_from_workbook, parse_sheet_for_revisions, create_mindmaps_from_list

# Sample link
# "https://docs.google.com/spreadsheets/d/<SPREADSHEET-ID>/export?format=xlsx"

# Create your views here.
def homepage(request):
    return render(request, template_name="revision_sync/index.html")
    
def sync(request):
    user = request.user
    if user.is_authenticated:
        link = os.getenv("DATA_SHEET_URL")
        if not link:
            return HttpResponse("Please specify data sheet url in env.")
        print("Syncing")
        book = load_workbook_from_url(link)
        sheet = get_sheet_from_workbook(book, 'Sheet1')
        mindmaps_list = parse_sheet_for_revisions(sheet)    
        create_mindmaps_from_list(mindmaps_list)

        print(mindmaps_list[-1])
        print(len(mindmaps_list))
        return HttpResponse("Synced")
    else:
        return HttpResponse("Please login to continue")