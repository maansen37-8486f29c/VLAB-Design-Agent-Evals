# 工具调用（Tool Calling）设计与下一阶段接入

## 1. 工具与Agent的分工
- Agent：理解自然语言，判断需不需要外部工具，以及选择合适工具（**未来待验证**）。
- Python工具：执行确定性规则查询、显性约束检查、缺失参数返回。
- Agent：把工具的JSON结果解释给用户，不得扩写不存在的工程合规结论。

```
用户问题 → Agent判断调用意图（计划阶段）
              ↓
   lookup_requirement / assess_front_design
              ↓
      JSON结果 + 来源ID
              ↓
     Agent整理最终回复（待实际联调）
```

## 2. 离线演示（无需Dify额度）
在项目根目录打开终端：

```
python -m src.demo
python -m unittest discover -s tests -v
```

工具函数：
- `lookup_requirement(requirement_id)`：给出项目约束及来源；
- `assess_front_design(proposal)`：对明确的“取消格栅/双层改单层”场景做关键词校验；
- `lookup_verified_parameter(parameter)`：未提供工程参数时返回空值；
- `dispatch_tool(name, arguments)`：演示工具分发。

> 局限：这里是预设函数调用，**没有大模型自主选择工具**。关键词匹配不能识别所有句式，必须人工复核。

## 3. Dify真实接入路径（有额度后）
目前新版Dify Agents支持通过工具配置调用插件、自定义API、工作流或MCP。若希望让云端Dify调用本项目代码，不能直接指向电脑里的`.py`文件，需要先把函数包装成Dify可访问的HTTP API（或改成兼容的Dify工具/工作流），完成鉴权、部署和错误处理后，再在Agent的Tools区域配置和测试。

建议按顺序：
1. 选择`lookup_requirement`作为第一个最简单的真实工具；
2. 公开非敏感的测试规则，部署只读接口（注意API限流和鉴权）；
3. 在Dify Agents配置工具，限定只读权限；
4. 运行真实问题，检查工具调用日志里的输入参数、输出JSON及模型最终回答；
5. 然后再接入`assess_front_design`并扩展测试集。

**不得把这份本地函数原型写成“已在Dify实现Function Calling”。**
