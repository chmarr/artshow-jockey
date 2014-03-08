from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages

from .models import Piece


@permission_required('artshow.is_artshow_staff')
def index(request):
    return render(request, 'artshow/workflows_index.html')


@permission_required('artshow.is_artshow_staff')
def printing(request):
    bid_sheets_query = Piece.objects.filter(status__in=(Piece.StatusNotInShow, Piece.StatusNotInShowLocked),
                                            bid_sheet_printing=Piece.PrintingNotPrinted)
    control_forms_query = Piece.objects.filter(status__in=(Piece.StatusNotInShow, Piece.StatusNotInShowLocked),
                                               control_form_printing=Piece.PrintingNotPrinted)
    bid_sheets_to_print_query = Piece.objects.filter(bid_sheet_printing=Piece.PrintingToBePrinted)
    control_forms_to_print_query = Piece.objects.filter(control_form_printing=Piece.PrintingToBePrinted)

    if request.method == "POST":
        if request.POST.get("lock_pieces"):
            bid_sheets_marked = bid_sheets_query.update(
                status=Piece.StatusNotInShowLocked,
                bid_sheet_printing=Piece.PrintingToBePrinted)
            control_forms_marked = control_forms_query.update(
                status=Piece.StatusNotInShowLocked,
                control_form_printing=Piece.PrintingToBePrinted)
            messages.info(request, "%d pieces have been marked for bid sheet printing, %d for control form printing" % (
                bid_sheets_marked, control_forms_marked))
            return redirect('.')
        elif request.POST.get("print_bid_sheets"):
            import bidsheets
            response = HttpResponse(mimetype="application/pdf")
            bidsheets.generate_bidsheets(output=response, pieces=bid_sheets_to_print_query)
            messages.info(request, "Bid sheets printed.")
            return response

        elif request.POST.get("print_control_forms"):
            import bidsheets
            response = HttpResponse(mimetype="application/pdf")
            bidsheets.generate_control_forms_for_pieces(output=response, pieces=control_forms_to_print_query)
            messages.info(request, "Control forms printed.")
            return response

        elif request.POST.get("bid_sheets_done"):
            pieces_marked = bid_sheets_to_print_query.update(bid_sheet_printing=Piece.PrintingPrinted)
            messages.info(request, "%d pieces marked as bid sheet printed" % pieces_marked)
            return redirect('.')

        elif request.POST.get("control_forms_done"):
            pieces_marked = control_forms_to_print_query.update(control_form_printing=Piece.PrintingPrinted)
            messages.info(request, "%d pieces marked as control form printed" % pieces_marked)
            return redirect('.')

    context = {
        'num_pieces_bid_sheet_unprinted': bid_sheets_query.count(),
        'num_pieces_control_form_unprinted': control_forms_query.count(),
        'num_bid_sheets_to_be_printed': bid_sheets_to_print_query.count(),
        'num_control_forms_to_be_printed': control_forms_to_print_query.count(),
        'num_bid_sheets_printed': Piece.objects.filter(bid_sheet_printing=Piece.PrintingPrinted).count(),
        'num_control_forms_printed': Piece.objects.filter(control_form_printing=Piece.PrintingPrinted).count(),
    }

    return render(request, 'artshow/workflows_printing.html', context)
