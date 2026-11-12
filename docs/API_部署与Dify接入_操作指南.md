# V·LAB API 从 GitHub 到 Dify：零基础分步教程

> 这是个人教学项目的只读演示 API。不会接入企业内部数据库，不适用于安全认证，不要输入隐私或保密项目资料。

## 0. 先确认升级文件上传到仓库根目录

将本ZIP解压后打开文件夹**内部**，上传至已有的 GitHub 仓库 `VLAB-Design-Agent-Evals` 的**根目录**。现有 `src/`、`data/`、`tests/test_tools.py` 保持不变。新增文件包括：

- `main.py` —— 把离线函数封装成HTTP接口。
- `requirements.txt` —— 云端安装依赖。
- `.python-version` —— 固定Python版本，可能因隐藏文件设置而不显示；可以在Render手动配置。
- `tests/test_api.py` —— 8个新增API测试。
- `.github/workflows/python-tests.yml` —— 更新原有工作流，加上依赖安装。

仓库根目录必须能看到 `main.py` 和 `requirements.txt`。点击 Actions，检查运行日志中是否出现 `Ran 15 tests` 和 `OK`。这一步不消耗Dify额度。

## 1. 部署到 Render

1. 打开 https://dashboard.render.com/ ，使用GitHub登录或授权。
2. 点击 **New → Web Service**。
3. 选择 `maansen37-8486f29c/VLAB-Design-Agent-Evals` 仓库（如果GitHub用户名不是这个，以自己的实际账号为准）。
4. 按照下表填写：

| 字段 | 值 |
|---|---|
| Name | `vlab-design-rules-api`（如果重名，可加随机后缀） |
| Language / Runtime | `Python 3` |
| Branch | `main` |
| Root Directory | **留空**（使用仓库根目录） |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Instance Type | `Free`（只有可用时才选择） |

5. 如果面板有环境变量区域，可设 `PYTHON_VERSION=3.11.11`，不需要填写任何密钥；也可以依赖 `.python-version` 文件。
6. 点击 `Create Web Service` / `Deploy`，等到状态为 `Live`。获得一个唯一的公网地址，例如 `https://vlab-design-rules-api-xxxx.onrender.com`；**这个网址只是格式示例**，实际地址应以Render界面为准。

免费服务闲置15分钟后可能休眠，下一次访问可能需约1分钟唤醒。不要因此重复创建服务。

## 2. 先在浏览器验证 API

把下列示例中的 `<你的Render地址>` 替换成实际地址：

1. `<你的Render地址>/health` 应返回 `"status":"ok"`。
2. `<你的Render地址>/docs` 应打开交互式 Swagger API 文档。
3. 在 `/docs` 页面打开 `GET /tools/requirement` → `Try it out`，输入 `HARD-F02`，点击 `Execute`；响应中应有 `"found": true` 和 `"id": "HARD-F02"`。
4. 打开 `POST /tools/assess-front-design`，输入 JSON：

```json
{"proposal":"散热格栅取消，将双层圆盘结构简化成单层装饰盖。"}
```

预期返回 `explicit_requirement_conflict` 且 `violations` 包含 `HARD-F01`、`HARD-F02`。
5. 打开 `<你的Render地址>/dify-openapi.json`，确认显示 OpenAPI 规范且其中的 `servers` 是你的真实网址。

上面验证的是API远程调用成功，还不是Dify自主选择工具。

## 3. 将 API 导入 Dify 自定义工具

1. 登录 Dify Cloud，在工作空间找到 **Integrations → Tools**（可能显示“集成 → 工具”）。
2. 选择 **Swagger API / Custom API** 类型，点击新增。
3. 用 **Import from URL** 导入 `<你的Render地址>/dify-openapi.json`，或者打开该URL复制JSON文本粘贴到Schema框。
4. 工具提供方建议命名 `VLAB-Design-Rules-API`。本项目为公开演示接口，认证选 **None / No authentication**；不要上传任何个人API Key。
5. 解析成功后，应显示 `lookup_requirement`、`assess_front_design`、`lookup_verified_parameter` 三个工具。
6. 若工具测试时遇到超时，先在浏览器打开 `<你的Render地址>/health` 唤醒Render，再重试。

**注意：** 如果Dify的新版Agents工具列表中找不到新API工具，可返回主界面核对工具是否已在同一个工作空间创建。

## 4. 关联到新版 Agents

1. 打开 **Agents → VLAB-Design-Review-Agent → Configure**。
2. 找到 **Tools**（工具）部分，点击 **Add**。
3. 选择 `VLAB-Design-Rules-API` 下的三个工具，保存。
4. 保留原来的知识库和 V2.1 Prompt，只在Prompt末尾添加以下工具使用规则：

> 当用户询问项目专属需求编号时，优先调用 `lookup_requirement`；当用户提供前脸方案并需检查硬约束时，调用 `assess_front_design`；当用户要求知识库没有依据的毫米数、通风面积或标准编号时，调用 `lookup_verified_parameter`。回答时注明工具结果来自教学项目规则，不等于工程合规。工具未检出显性冲突，也不能说方案已通过安全验证。工具调用失败要明确说明，不能伪造工具执行结果。

5. 有模型额度后，在 **Preview** 新建会话，输入：

> 请根据项目规则检查：我要取消散热格栅，并将原有双层圆盘结构改为单层装饰盖。请明确列出违反的规则编号，且说明结论来自工具还是推断。

6. 观察工具调用轨迹：能否看到模型选择了 `assess_front_design`，并返回两个需求编号。保存截图作为Tool Calling证据。

## 5. 验收口径与故障排查

| 验收项 | 需要的证据 |
|---|---|
| API本地测试 | GitHub Actions中 `Ran 15 tests`、`OK` |
| API云端可用 | Render `Live` + `/health`成功 |
| API业务接口可用 | `/docs` 实际调用返回正确JSON |
| Dify已导入工具 | Dify Tools 列表出现3个工具 |
| Agent真实工具调用 | 预览或执行记录显示工具调用及返回值（**未执行前不能声称通过**） |

常见错误：

- Render Deploy Failed：检查 Root Directory 是否留空、Build/Start命令是否与表格一致、文件是否已放仓库根目录。
- `ModuleNotFoundError: fastapi`：缺少或未执行 `pip install -r requirements.txt`。
- `ModuleNotFoundError: src`：根目录错误或 `src` 文件夹漏传。
- API打开慢：Render免费实例已休眠；先访问 `/health`。
- Dify OpenAPI解析失败：先检查 `/dify-openapi.json` 是否可访问，`servers[0].url` 是否为实际Render HTTPS地址，三项 operationId 是否存在。
- Dify没有主动调用工具：检查是否已在 Agent 的 Tools 配置中添加工具，以及模型是否支持工具调用、是否还有额度。

## 6. 安全边界

该API部署后默认**任何人知道网址都可以调用**，仅适合公开、无敏感数据的教学演示。不要输入保密车型数据、个人信息、企业内部资料或密钥。若将来用于实际业务，需要加入认证、访问限流、日志脱敏及安全评估。
