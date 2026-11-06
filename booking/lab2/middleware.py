import time
class LogTimeRequestsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration = (time.time() - start_time) * 1000

        method = request.method
        path = request.path
        status = response.status_code
        try:
            with open('LogRequest.txt', "a" ,encoding='utf-8') as f:
                f.write(f'{method} {path} {status} {duration:.1f}ms\n')
        except Exception as e:
            print(f'Ошибка записи лога: {e}')

        return response