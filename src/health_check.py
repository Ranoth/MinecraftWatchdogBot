import logging
from aiohttp import web


class HealthCheck:
    def __init__(self):
        self.ready = False

    async def health_check_handler(self, request):
        """Health check endpoint"""
        if self.ready:
            return web.Response(text="OK", status=200)
        return web.Response(text="NOT READY", status=503)

    async def start_server(self):
        """Start health check HTTP server"""
        app = web.Application()
        app.router.add_get("/health", self.health_check_handler)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", 8080)
        await site.start()
        logging.info("Health check server started on port 8080")
