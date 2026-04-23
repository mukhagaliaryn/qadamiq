from django.shortcuts import render


# home page
# ----------------------------------------------------------------------------------------------------------------------
def home_view(request):
    return render(request, 'app/main/page.html', {})