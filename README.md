# V·LAB Design Agent — AI Evals & Tool Calling Prototype

> 车辆设计教学场景的AI产品实践：**Prompt迭代 → RAG知识检索 → Bad Case分析 → 确定性规则工具原型**。
>
> **项目定位：个人学习与产品实践作品，不是车辆工程安全认证系统，也不是V·LAB线上正式版本的源码。**

## 1. 产品简介
面向工程车和列车设计教学，探索如何让AI评审助手理解设计要求、检索知识库、识别硬性约束冲突，并在缺乏证据时避免编造工程参数或标准。项目重点体现产品需求定义、AI效果评测与迭代流程。

## 2. 当前已完成的证据
| 阶段 | 进度 | 证据口径 |
|---|---|---|
| Agent Prompt V1/V2/V2.1 | ✅ 已完成多轮人工测试 | 已有部分真实回答及评测表；早期原始记录仍需补齐，测试集较小 |
| TC-005 前脸设计评审 | ✅ 已执行 | 人工初评9/10，存在硬性约束表述偏弱问题 |
| TC-006 列车卫生间评审 | ✅ 已执行 | 人工初评9/10，测试建议尚不够量化 |
| RAG-001 查询项目需求编号 | ✅ 初步通过 | Agent输出HARD-F01/HARD-F02并附知识库引用；尚未审计底层调用轨迹 |
| RAG-002 项目硬约束冲突应用 | ⏳ **未执行** | 因Dify额度不足，只有测试题与预期答案 |
| RAG-003 无依据工程参数边界 | ⏳ **未执行** | 因Dify额度不足，只有测试题与预期答案 |
| 本地规则查询与约束校验工具 | ✅ 已实现并可离线单元测试 | **Python确定性工具，不是Dify线上Function Calling** |
| Dify真实工具调用 | ⏳ 待联调 | 有额度、接口部署后再验收 |

## 3. 技术结构
```
知识库测试文档 → RAG查询（线上已初测）
                    ↓
              V·LAB Agent
                    |
      [未来：调用独立规则工具]
                    ↓
           JSON规则结果 + ID
                    ↓
         结构化设计评审回答
```

**离线工具原型（已实现）：**
```
Python Demo → dispatch_tool → lookup_requirement
                            → assess_front_design
                            → lookup_verified_parameter
```

## 4. 已知项目硬约束（教学练习材料）
- `HARD-F01`：双层圆盘结构必须完整保留。
- `HARD-F02`：散热格栅不能取消。

这里的`HARD`只表示**本项目内部需求优先级**，不是国家标准或工程认证。

## 5. 一分钟运行离线Demo
电脑安装Python 3.10及以上，在仓库根目录运行：

```bash
python -m src.demo
python -m unittest discover -s tests -v
```

无需Dify、无需模型API Key、无需安装第三方Python库。

## 6. 项目文件索引
- `src/requirements_tool.py`：实际可运行的规则查询、设计硬约束检查、工具分发函数。
- `data/knowledge_rules.json`：从教学知识库提取的规则。
- `data/tool_specification.json`：供后续模型Function Calling接口参考的函数定义示例。
- `data/rag_test_status.csv`：RAG-001/002/003的真实执行状态；**没有把未执行案例写成通过**。
- `tests/test_tools.py`：离线自动化单元测试。
- `docs/product_prd.md`：需求背景、MVP、指标和边界。
- `docs/evaluation_report.md`：Prompt迭代、评测结果、Bad Case。
- `docs/tool_calling_guide.md`：真实Dify工具接入计划和条件。
- `docs/github_upload_steps.md`：零基础上传教程。
- `evidence/previous_evaluation_ledger.xlsx`：先前版本人工评测表。
- `.github/workflows/python-tests.yml`：上传GitHub后自动运行离线单测。

## 7. 下一步验证
1. 恢复模型额度后完成RAG-002/003线上测试并保存完整回答及检索依据；
2. 将Python工具封装成线上API，并在Dify Agent的Tools配置中集成；
3. 使用固定测试集验证工具选择是否正确、参数是否正确、错误时是否安全降级；
4. 持续增加Bad Case、可执行测试和版本对照。

详见[产品需求](docs/product_prd.md) · [评测报告](docs/evaluation_report.md) · [工具调用路线](docs/tool_calling_guide.md)。
