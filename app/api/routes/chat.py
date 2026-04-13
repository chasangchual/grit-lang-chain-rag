from fastapi import APIRouter

from app.api.deps import DbSession, EmbeddingServiceDep
from app.schemas.chat import ChatRequest, ChatResponse, SourceChunk

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "",
    response_model=ChatResponse,
    summary="Chat with RAG",
)
def chat(
    request: ChatRequest,
    session: DbSession,
    embedding_service: EmbeddingServiceDep,
) -> ChatResponse:
    embedding_service.search_similar(request.query, top_k=request.top_k)
    return ChatResponse(
        answer="Chat functionality not yet implemented. This is a placeholder response.",
        sources=[],
        model="placeholder",
    )
