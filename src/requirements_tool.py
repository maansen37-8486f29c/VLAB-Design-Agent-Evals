"""可离线运行的确定性规则工具，非LLM Function Calling的云端实测。"""
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Any

RULES_PATH = Path(__file__).resolve().parents[1] / "data" / "knowledge_rules.json"


def _knowledge() -> dict[str, Any]:
    return json.loads(RULES_PATH.read_text(encoding="utf-8"))


def lookup_requirement(requirement_id: str) -> dict[str, Any]:
    """通过需求编号检索项目规则；找不到就明确返回未找到。"""
    rule = next((r for r in _knowledge()["requirements"] if r["id"] == requirement_id), None)
    if not rule:
        return {"found": False, "requirement_id": requirement_id,
                "message": "知识规则中没有该编号，不得猜测。"}
    return {"found": True, **rule, "source_type": "项目教学需求；非国家标准"}


def assess_front_design(proposal: str) -> dict[str, Any]:
    """用明确的关键词规则识别显性违反硬约束的描述。

    不是通用NLP理解器，不保证识别所有同义表达或隐含冲突。
    未检测到冲突 != 符合要求，更 != 工程安全。
    """
    if not proposal.strip():
        return {"status": "insufficient_input", "violations": [],
                "message": "未提供方案内容。"}
    grille_patterns = [
        r"(?:取消|删除|拆除|移除|去掉|去除|不保留)\s*(?:原车)?(?:的)?散热格栅",
        r"散热格栅.{0,12}(?:取消|删除|拆除|移除|去掉|去除|封死|封闭)",
        r"(?:格栅|进风口).{0,10}(?:完全封闭|封死)",
        r"(?:完全封闭|封死).{0,15}(?:散热格栅|格栅)",
    ]
    disc_patterns = [
        r"双层圆盘(?:结构)?.{0,20}(?:改为单层|简化成单层|简化为单层|变成单层|取消|删除|去除|单层装饰)",
        r"(?:取消|删除|移除|去除)\s*(?:原车)?(?:的)?双层圆盘(?:结构)?",
    ]
    ids = []
    if any(re.search(pattern, proposal) for pattern in grille_patterns):
        ids.append("HARD-F02")
    if any(re.search(pattern, proposal) for pattern in disc_patterns):
        ids.append("HARD-F01")
    violations = [lookup_requirement(rid) for rid in ids]
    if violations:
        return {
            "status": "explicit_requirement_conflict",
            "violations": violations,
            "message": "检测到方案描述与项目硬约束存在明确冲突；应修改方案并由人员复核。",
            "engineering_compliance": "未评估，不能由本工具判定",
        }
    return {
        "status": "no_explicit_conflict_detected",
        "violations": [],
        "message": "关键词规则未检测到显性冲突；不代表方案满足全部要求。",
        "engineering_compliance": "未评估，不能由本工具判定",
    }


def lookup_verified_parameter(parameter: str) -> dict[str, Any]:
    """这里没有任何工程参数验证材料；不能编造数值或标准。"""
    return {"parameter": parameter, "verified": False, "value": None,
            "message": "当前教学知识库没有可核实数值或国家标准条款。"}


TOOL_REGISTRY = {
    "lookup_requirement": lookup_requirement,
    "assess_front_design": assess_front_design,
    "lookup_verified_parameter": lookup_verified_parameter,
}


def dispatch_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """本地工具分发示例；不是LLM自主选择工具的运行记录。"""
    if name not in TOOL_REGISTRY:
        return {"error": "unknown_tool", "name": name}
    try:
        return TOOL_REGISTRY[name](**arguments)
    except TypeError as exc:
        return {"error": "invalid_arguments", "details": str(exc)}
