from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import FileRecord, TextChunk
from app.services import TextRankSummarizer

router = APIRouter(prefix="/api/documents", tags=["documents"])
textrank_summarizer = TextRankSummarizer(max_sentences=3)


@router.post("/{id}/summary", summary="生成文档摘要", description="使用TextRank算法为指定文档生成3句关键摘要")
async def generate_summary(
    id: int,
    regenerate: bool = False,
    db: AsyncSession = Depends(get_db)
):
    document = await db.get(FileRecord, id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not regenerate and document.summary:
        return {
            "summary": document.summary,
            "sentences": [s.strip() for s in document.summary.split("。") if s.strip()],
            "generation_time_ms": 0,
            "cached": True
        }
    
    chunks_result = await db.execute(
        select(TextChunk).where(TextChunk.file_id == id).order_by(TextChunk.chunk_index)
    )
    chunks = chunks_result.scalars().all()
    
    if not chunks:
        raise HTTPException(status_code=400, detail="No text content available for summarization")
    
    full_text = " ".join([chunk.content for chunk in chunks])
    
    result = textrank_summarizer.summarize(full_text)
    
    from sqlalchemy import update
    await db.execute(update(FileRecord).where(FileRecord.id == id).values(
        summary=result["summary"]
    ))
    await db.commit()
    
    return {
        "summary": result["summary"],
        "sentences": result["sentences"],
        "generation_time_ms": result["generation_time_ms"],
        "cached": False
    }


@router.get("/{id}", summary="获取文档详情", description="获取指定文档的详细信息")
async def get_document(id: int, db: AsyncSession = Depends(get_db)):
    document = await db.get(FileRecord, id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    from app.models import FileTag
    tags_result = await db.execute(select(FileTag).where(FileTag.file_id == id))
    tags = tags_result.scalars().all()
    
    return {
        "id": document.id,
        "name": document.original_name,
        "standard_name": document.standard_name,
        "bucket": document.bucket,
        "file_type": document.file_type,
        "file_size": document.file_size,
        "status": document.process_status,
        "review_status": document.review_status,
        "summary": document.summary,
        "created_at": document.created_at,
        "tags": tags
    }
