from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from backend.scheduler.Scheduler import Scheduler


def request_scheduler_dump(request: HttpRequest) -> HttpResponse:
    Scheduler.get_instance().log_debug_data()
    return redirect("home")
