"""V·LAB教学场景规则工具 HTTP API。

复用 src.requirements_tool 已验证的本地规则逻辑。
它不是工程安全认证或完整自然语言理解系统。
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from urllib.parse import urlsplit
import os

from fastapi import FastAPI, Query, Request
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field

from src.requirements_tool import (
    assess_front_design,
    lookup_requirement,
    lookup_verified_parameter,
)

app = FastAPI(
    title="VLAB Design Rules API",
    version="0.2.0",
    description=(
        "Vehicle-design education prototype. "
        "Returns project teaching requirements and explicit text-based conflict checks. "
        "Not a safety certification or a national-standards database."
    ),
)


class ProposalRequest(BaseModel):
    proposal: str = Field(
        min_length=1,
        max_length=2000,
        description="中文方案描述。例如：取消散热格栅，将双层圆盘结构简化成单层。",
    )


@app.get("/health", include_in_schema=False)
def health() -> dict:
    """检查API是否已启动；不执行模型调用。"""
    return {"status": "ok", "service": "VLAB Design Rules API", "version": "0.2.0"}


@app.get("/tools/requirement", operation_id="lookup_requirement", tags=["VLAB rules"])
def get_requirement(
    requirement_id: str = Query(
        ..., min_length=1, max_length=64,
        description="项目需求编号，例如 HARD-F01 或 HARD-F02。",
    )
) -> dict:
    """查询项目教学规则；未知编号明确返回 found=false，不编造。"""
    return lookup_requirement(requirement_id)


@app.post("/tools/assess-front-design", operation_id="assess_front_design", tags=["VLAB rules"])
def check_front_design(payload: ProposalRequest) -> dict:
    """检测中文前脸方案文本中明确的硬约束冲突；未命中不代表设计合规。"""
    return assess_front_design(payload.proposal)


@app.get("/tools/verified-parameter", operation_id="lookup_verified_parameter", tags=["VLAB rules"])
def get_verified_parameter(
    parameter: str = Query(
        ..., min_length=1, max_length=120,
        description="需要核实的工程参数，如散热格栅最小通风面积。",
    )
) -> dict:
    """核查知识材料中是否有可验证的工程数值；当前版本明确返回未验证。"""
    return lookup_verified_parameter(parameter)


@app.get("/dify-openapi.json", include_in_schema=False)
def dify_openapi(request: Request) -> dict:
    """给Dify导入的OpenAPI文件，自动补充当前API公网基础网址。"""
    schema = deepcopy(app.openapi())
    configured = os.getenv("PUBLIC_API_BASE_URL", "").strip().rstrip("/")
    if configured:
        parsed = urlsplit(configured)
        if parsed.scheme not in ("https", "http") or not parsed.netloc:
            raise ValueError("PUBLIC_API_BASE_URL must be an http(s) URL")
        base_url = configured
    else:
        # Render等反向代理通常透传 host 和 x-forwarded-proto。
        proto = request.headers.get("x-forwarded-proto", request.url.scheme).split(",")[0].strip()
        if proto not in {"http", "https"}:
            proto = request.url.scheme
        host = request.headers.get("host", request.url.netloc)
        base_url = f"{proto}://{host}"
    schema["servers"] = [{"url": base_url}]
    return schema


def _openapi_30() -> dict:
    """Dify自定义工具采用更广泛兼容的OpenAPI 3.0.3说明。"""
    if app.openapi_schema is None:
        app.openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            openapi_version="3.0.3",
        )
    return app.openapi_schema


app.openapi = _openapi_30
