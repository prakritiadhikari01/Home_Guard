from django.shortcuts import render


def login_page(request):
    return render(request, "index.html")


def register_page(request):
    return render(request, "register.html")


def dashboard_page(request):
    return render(request, "pages/dashboard.html")


def live_page(request):
    return render(request, "pages/live.html")


def timeline_page(request):
    return render(request, "pages/timeline.html")


def alerts_page(request):
    return render(request, "pages/alerts.html")


def members_page(request):
    return render(request, "pages/members.html")

def member_detail_page(request, member_id):
    return render(request, "pages/member_detail.html", {"member_id": member_id})

def devices_page(request):
    return render(request, "pages/devices.html")

def devices_detail_page(request, device_id):
    return render(request, "pages/device_detail.html", {"device_id": device_id})

def cameras_page(request):
    return render(request, "pages/cameras.html")


def assistant_page(request):
    return render(request, "pages/assistant.html")


def settings_page(request):
    return render(request, "pages/settings.html")

def home_setup_page(request):
    return render(request, "pages/home-setup.html")

def scan_page(request):
    return render(request, "pages/scan.html")