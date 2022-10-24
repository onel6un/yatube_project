from datetime import datetime
def year_now(request):
    year = datetime.now().year
    return {
        'year': year
    }