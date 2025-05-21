from .routers import NerModelRouter, SummaryModelRouter, TagModelRouter, AISampleRouter

class ModelRouterFactory:
    _router_map = {
        "ner": NerModelRouter,
        "tag": TagModelRouter,
        "summarize": SummaryModelRouter,
        "ai-sample": AISampleRouter,
    }

    @staticmethod
    def get_router(task: str):
        router_cls = ModelRouterFactory._router_map.get(task)
        if not router_cls:
            raise ValueError(f"Unsupported task: {task}")
        return router_cls()
