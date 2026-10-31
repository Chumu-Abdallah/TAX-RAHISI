class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # hapa naweza kueka logic kabla ya view
        if request.user.is_authenticated:
            print("[AUDIT] User: {request.user} -> {request.path}")
        # mfano print(request.path)
        response = self.get_response(request)
        # hapa logic kabla ya view
        return response    