"""无需Dify、无需API Key的本地函数调用演示。"""
import json
from src.requirements_tool import dispatch_tool

if __name__ == "__main__":
    calls = [
        {"name":"lookup_requirement", "arguments":{"requirement_id":"HARD-F02"}},
        {"name":"assess_front_design", "arguments":{"proposal":"将原车散热格栅取消，将双层圆盘结构简化成单层装饰盖。"}},
        {"name":"lookup_verified_parameter", "arguments":{"parameter":"双层圆盘结构准确直径（毫米）"}}
    ]
    for call in calls:
        print("TOOL:", call["name"])
        print(json.dumps(dispatch_tool(**call), ensure_ascii=False, indent=2))
        print()
