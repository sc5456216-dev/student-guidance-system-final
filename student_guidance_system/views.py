from django.http import HttpResponse

def home(request):
    return HttpResponse("""
        <h1>🎓 Student Guidance System</h1>
        <p>Welcome to the Student Guidance System!</p>
        <p><a href="/admin">Admin Panel</a></p>
        <p><a href="/api/">API Root</a></p>
    """)
