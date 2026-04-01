from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.database import get_db
from app.models import FileRecord, TextChunk
from app.schemas import SummaryResponse
from app.services.summarizer import TextRankSummarizer

router = APIRouter(prefix="/api/documents", tags=["documents"])
summarizer = TextRankSummarizer()


@router.post("/{id}/summary", summary="生成文档摘要", description="基于TextRank算法生成文档摘要，结果缓存到数据库", response_model=SummaryResponse)
async def generate_summary(
    id: int,
    regenerate: bool = False,
    db: AsyncSession = Depends(get_db)
):
    file = await db.get(FileRecord, id)
    if not file:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not regenerate and file.summary:
        return {
            "summary": file.summary,
            "generation_time_ms": 0,
            "regenerated": False
        }
    
    chunks_result = await db.execute(
        select(TextChunk).where(TextChunk.file_id == id).order_by(TextChunk.chunk_index)
    )
    chunks = chunks_result.scalars().all()
    
    if not chunks:
        raise HTTPException(status_code=400, detail="No content available for summarization")
    
    content = " ".join([c.content for c in chunks])
    result = summarizer.summarize(content, num_sentences=3)
    
    await db.execute(update(FileRecord).where(FileRecord.id == id).values(
        summary=result["summary"]
    ))
    await db.commit()
    
    return {
        "summary": result["summary"],
        "generation_time_ms": result["generation_time_ms"],
        "regenerated": True
    }
