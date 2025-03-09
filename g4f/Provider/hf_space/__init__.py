from __future__ import annotations

import random

from ...typing import AsyncResult, Messages, ImagesType
from ...errors import ResponseError
from ..base_provider import AsyncGeneratorProvider, ProviderModelMixin

from .BlackForestLabsFlux1Dev        import BlackForestLabsFlux1Dev
from .BlackForestLabsFlux1Schnell    import BlackForestLabsFlux1Schnell
from .VoodoohopFlux1Schnell          import VoodoohopFlux1Schnell
from .CohereForAI                    import CohereForAI
from .Janus_Pro_7B                   import Janus_Pro_7B
from .Phi_4                          import Phi_4
from .Qwen_QVQ_72B                   import Qwen_QVQ_72B
from .Qwen_Qwen_2_5M_Demo            import Qwen_Qwen_2_5M_Demo
from .Qwen_Qwen_2_72B_Instruct       import Qwen_Qwen_2_72B_Instruct
from .StableDiffusion35Large         import StableDiffusion35Large
from .G4F                            import G4F

class HuggingSpace(AsyncGeneratorProvider, ProviderModelMixin):
    url = "https://huggingface.co/spaces"

    working = True

    default_model = Qwen_Qwen_2_72B_Instruct.default_model
    default_image_model = BlackForestLabsFlux1Dev.default_model
    default_vision_model = Qwen_QVQ_72B.default_model
    providers = [
        BlackForestLabsFlux1Dev,
        BlackForestLabsFlux1Schnell,
        VoodoohopFlux1Schnell,
        CohereForAI,
        Janus_Pro_7B,
        Phi_4,
        Qwen_QVQ_72B,
        Qwen_Qwen_2_5M_Demo,
        Qwen_Qwen_2_72B_Instruct,
        StableDiffusion35Large,
        G4F
    ]

    @classmethod
    def get_parameters(cls, **kwargs) -> dict:
        parameters = {}
        for provider in cls.providers:
            parameters = {**parameters, **provider.get_parameters(**kwargs)}
        return parameters

    @classmethod
    def get_models(cls, **kwargs) -> list[str]:
        if not cls.models:
            models = []
            image_models = []
            vision_models = []
            for provider in cls.providers:
                models.extend(provider.get_models(**kwargs))
                models.extend(provider.model_aliases.keys())
                image_models.extend(provider.image_models)
                vision_models.extend(provider.vision_models)
            models = list(set(models))
            models.sort()
            cls.models = models
            cls.image_models = list(set(image_models))
            cls.vision_models = list(set(vision_models))
        return cls.models

    @classmethod
    async def create_async_generator(
        cls, model: str, messages: Messages, images: ImagesType = None, **kwargs
    ) -> AsyncResult:
        if not model and images is not None:
            model = cls.default_vision_model
        is_started = False
        random.shuffle(cls.providers)
        for provider in cls.providers:
            if model in provider.model_aliases:
                async for chunk in provider.create_async_generator(provider.model_aliases[model], messages, images=images, **kwargs):
                    is_started = True
                    yield chunk
            if is_started:
                return
        error = None
        for provider in cls.providers:
            if model in provider.get_models():
                try:
                    async for chunk in provider.create_async_generator(model, messages, images=images, **kwargs):
                        is_started = True
                        yield chunk
                    if is_started:
                        break
                except ResponseError as e:
                    if is_started:
                        raise e
                    error = e
        if not is_started and error is not None:
            raise error

BlackForestLabsFlux1Dev.parent = HuggingSpace.__name__,
BlackForestLabsFlux1Schnell.parent = HuggingSpace.__name__,
VoodoohopFlux1Schnell.parent = HuggingSpace.__name__,
CohereForAI.parent = HuggingSpace.__name__,
Janus_Pro_7B.parent = HuggingSpace.__name__,
Phi_4.parent = HuggingSpace.__name__,
Qwen_QVQ_72B.parent = HuggingSpace.__name__,
Qwen_Qwen_2_5M_Demo.parent = HuggingSpace.__name__,
Qwen_Qwen_2_72B_Instruct.parent = HuggingSpace.__name__,
StableDiffusion35Large.parent = HuggingSpace.__name__,