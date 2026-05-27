from fastapi import APIRouter, File, UploadFile

from src.app.schemas.schemas import (
    DeleteDocumentResponse,
    DocumentChunkItem,
    DocumentChunkListResponse,
    DocumentDetailResponse,
    DocumentItem,
    DocumentListResponse,
    UploadDocumentResponse,
)
from src.app.services.document_service import DocumentService

router = APIRouter()


# 上传文档：保存文件并提取可用于后续检索和向量化的文本内容
@router.post(
    "/documents/upload",
    response_model=UploadDocumentResponse,
    tags=["文档"],
    summary="上传文档",
    description="上传本地文件，保存文档元信息并提取文本内容。",
)
async def upload_document_api(
    file: UploadFile = File(...),
) -> UploadDocumentResponse:
    result = await DocumentService().upload_document(file)
    return UploadDocumentResponse(**result)


# 列出文档：返回已上传文档的摘要列表
@router.get(
    "/documents",
    response_model=DocumentListResponse,
    tags=["文档"],
    summary="列出文档",
    description="返回当前系统中已经上传的文档列表。",
)
def list_documents_api() -> DocumentListResponse:
    documents = DocumentService().list_documents()
    return DocumentListResponse(items=[DocumentItem(**item) for item in documents])


# 获取文档详情：查看单个文档的元信息和处理状态
@router.get(
    "/documents/{document_id}",
    response_model=DocumentDetailResponse,
    tags=["文档"],
    summary="获取文档详情",
    description="根据文档 ID 返回该文档的详细信息。",
)
def get_document_api(document_id: str) -> DocumentDetailResponse:
    document = DocumentService().get_document_detail(document_id)
    return DocumentDetailResponse(**document)


# 列出文档分块：查看文档被切分后的 chunk 内容
@router.get(
    "/documents/{document_id}/chunks",
    response_model=DocumentChunkListResponse,
    tags=["文档"],
    summary="列出文档分块",
    description="根据文档 ID 返回该文档切分后的文本块列表。",
)
def list_document_chunks_api(document_id: str) -> DocumentChunkListResponse:
    chunks = DocumentService().get_document_chunks(document_id)
    return DocumentChunkListResponse(
        items=[DocumentChunkItem(**item) for item in chunks]
    )


# 删除文档：移除文档及其关联数据
@router.delete(
    "/documents/{document_id}",
    response_model=DeleteDocumentResponse,
    tags=["文档"],
    summary="删除文档",
    description="根据文档 ID 删除文档及其关联的处理结果。",
)
def delete_document_api(document_id: str) -> DeleteDocumentResponse:
    result = DocumentService().delete_document(document_id)
    return DeleteDocumentResponse(**result)

