# 项目说明与代码架构

本文档说明本项目的整体架构、请求处理链路，以及各目录和主要文件的用途。项目主体是一个基于 FastAPI 的后端服务，内部集成 LangGraph/LangChain 构建的智能旅行助手工作流。

> 说明：当前仓库中部分中文注释和 README 内容在读取时存在编码乱码现象，但代码结构和运行逻辑仍可识别。本文档以实际代码行为为准进行整理。

## 一、整体架构

项目可以分为五层：

1. **Web 服务层**
   - 由 `main.py` 启动 FastAPI 应用。
   - 负责挂载静态文件、初始化 CORS、异常处理、路由和接口文档认证。

2. **API 路由层**
   - 位于 `api/`。
   - 提供用户管理接口和智能工作流调用接口。

3. **业务工作流层**
   - 位于 `A_frist_version_projct/`。
   - 使用 LangGraph 构建主 Agent 和多个子 Agent。
   - 主助手负责意图识别和任务分发，子助手负责航班、租车、酒店、短途游等垂直任务。

4. **工具层**
   - 位于 `tools/`。
   - 封装航班、酒店、租车、旅游推荐、FAQ 检索、数据库初始化等工具函数。
   - 这些工具会被 LangChain/LangGraph 的工具调用机制使用。

5. **数据访问层**
   - 位于 `db/`。
   - 使用 SQLAlchemy 定义数据库连接、ORM 模型和 DAO。
   - 用户模块通过 DAO 完成增删改查。

## 二、主要运行链路

### 1. 服务启动链路

`main.py`

1. 创建 `Server` 实例。
2. 初始化日志配置。
3. 创建 FastAPI 应用。
4. 注册全局 OAuth2 文档认证依赖。
5. 挂载 `static/` 静态目录。
6. 初始化异常处理、CORS 和主路由。
7. 使用 `uvicorn.run()` 启动服务。

### 2. 用户登录链路

1. 前端调用 `/api/login/`。
2. `api/system_mgt/user_views.py` 根据用户名查询用户。
3. 使用 `utils/password_hash.py` 校验密码。
4. 使用 `utils/jwt_utils.py` 生成 JWT token。
5. 后续请求通过 token 进行认证。

### 3. 智能助手调用链路

1. 前端调用 `/api/graph/`，提交用户输入和会话配置。
2. `api/graph_api/graph_views.py` 调用 `finall_garph.stream()`。
3. `finall_garph` 来自 `A_frist_version_projct/mian_workflow.py`。
4. LangGraph 先加载用户信息，再进入主助手 `ctripassitant`。
5. 主助手根据用户意图：
   - 直接回答；
   - 调用普通工具；
   - 路由到航班、租车、酒店或短途游子图。
6. 子图内部区分安全工具和敏感工具。
7. 敏感工具执行前会触发 interrupt，等待用户确认。
8. 接口最终返回 AI 助手最后一条文本响应。

## 三、目录与文件用途

### 根目录

| 文件/目录 | 用途 |
| --- | --- |
| `main.py` | FastAPI 应用入口。负责创建服务、初始化日志/CORS/异常/路由、挂载静态文件并启动 Uvicorn。 |
| `README.md` | 项目原始说明文档。当前读取时存在中文编码乱码。 |
| `out.png` | LangGraph 工作流图导出的图片。 |
| `.gitattributes` | Git 属性配置。 |
| `.git/` | Git 仓库元数据。 |
| `.idea/` | JetBrains/PyCharm 工程配置目录。 |
| `.workbuddy/` | 本地工具或工作流辅助目录。 |

### `api/`

| 文件 | 用途 |
| --- | --- |
| `api/__init__.py` | API 包初始化文件。 |
| `api/routers.py` | 汇总并注册所有业务路由。当前包含用户管理路由和工作流调用路由，并统一挂载到 `/api` 前缀下。 |
| `api/schemas.py` | 定义通用 Pydantic/DAO 类型变量，以及 ORM 对象转响应模型所需的 `InDBMixin`。 |

### `api/graph_api/`

| 文件 | 用途 |
| --- | --- |
| `api/graph_api/__init__.py` | 工作流 API 子包初始化文件。 |
| `api/graph_api/graph_views.py` | 定义 `/graph/` 接口。接收用户输入，调用 LangGraph 工作流，并处理工作流中断确认逻辑。 |
| `api/graph_api/graph_schemas.py` | 定义工作流接口请求和响应模型，包括用户输入、`passenger_id`、`thread_id` 和助手响应。 |

### `api/system_mgt/`

| 文件 | 用途 |
| --- | --- |
| `api/system_mgt/__init__.py` | 用户管理 API 子包初始化文件。 |
| `api/system_mgt/user_views.py` | 用户管理接口，包括用户列表、按 ID 查询、注册、登录、文档认证、修改和批量删除。 |
| `api/system_mgt/user_schemas.py` | 用户相关 Pydantic 模型，包括创建/更新用户、用户响应、登录请求和登录响应。 |

### `config/`

| 文件 | 用途 |
| --- | --- |
| `config/__init__.py` | 使用 Dynaconf 加载配置文件，暴露全局 `settings` 对象。 |
| `config/development.yml` | 开发环境配置，包括服务地址、端口、CORS 来源、数据库连接、JWT 配置、白名单和默认密码。 |
| `config/production.yml` | 生产环境配置文件，占位或备用配置。 |
| `config/log_config.py` | 初始化日志配置，设置日志级别等。 |

### `db/`

| 文件 | 用途 |
| --- | --- |
| `db/__init__.py` | 创建 SQLAlchemy 数据库连接、Session 工厂和 ORM 基类 `DBModelBase`。 |
| `db/dao.py` | 通用 DAO 基类，封装查询全部、按主键查询、新增、更新、删除、统计和批量删除。 |

### `db/system_mgt/`

| 文件 | 用途 |
| --- | --- |
| `db/system_mgt/__init__.py` | 用户管理数据层子包初始化文件。 |
| `db/system_mgt/models.py` | 定义用户 ORM 模型 `UserModel`，对应用户表字段。 |
| `db/system_mgt/user_dao.py` | 用户 DAO，继承通用 DAO，增加按用户名查询、条件查询、用户批量删除等逻辑。 |

### `utils/`

| 文件 | 用途 |
| --- | --- |
| `utils/__init__.py` | 工具包初始化文件。 |
| `utils/cors.py` | 初始化 FastAPI CORS 中间件，允许配置中的前端来源访问。 |
| `utils/dependencies.py` | 提供数据库 Session 依赖 `get_db()`，用于 FastAPI 接口注入。 |
| `utils/docs_oauth2.py` | 自定义 OAuth2PasswordBearer，使接口文档支持 JWT 认证，并对白名单接口跳过认证依赖。 |
| `utils/handler_error.py` | 注册全局 HTTP 异常处理器。 |
| `utils/jwt_utils.py` | 创建 JWT token。使用配置中的密钥、算法和过期时间。 |
| `utils/middlewares.py` | 自定义 token 校验中间件。代码中目前在 `main.py` 里被注释，未启用。 |
| `utils/password_hash.py` | 密码哈希和密码校验工具，基于 passlib 的 bcrypt。 |

### `A_frist_version_projct/`

该目录是智能旅行助手的核心实验/第一版工作流实现。目录名存在拼写问题，但不影响运行。

| 文件 | 用途 |
| --- | --- |
| `A_frist_version_projct/__pycache__/` | Python 字节码缓存目录，运行时自动生成，不属于业务源码。 |
| `A_frist_version_projct/agbet_satte_Typeic.py` | 定义 LangGraph 状态 `Projct_State`，包含消息列表、用户信息和当前对话子状态。`update_dialog()` 用于维护子图栈。 |
| `A_frist_version_projct/CtripAssinstant.py` | 定义主助手封装类 `CtripAssinstant` 和 `run_CtripAssinstant()`。负责构建主提示词、绑定通义千问模型、Tavily 搜索、航班搜索、政策检索和子助手路由工具。 |
| `A_frist_version_projct/LLM.py` | 单独初始化一个通义千问 `ChatTongyi` 模型实例，读取环境工具配置中的 API key 和 URL。 |
| `A_frist_version_projct/mian_workflow.py` | 主工作流文件。创建 LangGraph `StateGraph`，添加主助手、用户信息节点、工具节点和各子图，编译成 `finall_garph`，并配置敏感操作中断。文件名存在拼写问题，应理解为 `main_workflow.py`。 |
| `A_frist_version_projct/child_graph.py` | 构建各业务子图：航班、租车、酒店、短途游。每个子图包含入口节点、助手节点、安全工具节点、敏感工具节点和退出节点。 |
| `A_frist_version_projct/child_graph_basemodel.py` | 定义工具调用用的 Pydantic 模型，包括退出/升级、转交航班助手、租车助手、酒店助手和短途游助手。 |
| `A_frist_version_projct/child_graph_runnnable.py` | 定义各子助手的 Prompt/Runnable，以及各业务的安全工具列表和敏感工具列表。 |
| `A_frist_version_projct/enter_node.py` | 创建进入子助手时的节点函数，向消息流中加入 ToolMessage，并更新 `dialog_state`。 |
| `A_frist_version_projct/draw_png.py` | 将 LangGraph 工作流绘制并保存为图片。 |
| `A_frist_version_projct/log_utils.py` | 自定义日志工具类。 |
| `A_frist_version_projct/evn_utili.py` | 保存或读取大模型相关环境配置，例如 Qwen API key 和 URL。文件名存在拼写问题，应理解为 `env_util.py`。 |
| `A_frist_version_projct/web_ui.py` | Gradio 风格的简单 Web UI 交互函数，用于提交消息和反馈。 |
| `A_frist_version_projct/out.png` | 该目录下导出的工作流图片。 |
| `A_frist_version_projct/out` | 工作流导出或调试输出文件。 |

### `tools/`

| 文件 | 用途 |
| --- | --- |
| `tools/__init__.py` | 工具包初始化文件。 |
| `tools/car_tools.py` | 租车工具，提供搜索租车、预订租车、修改租车、取消租车。 |
| `tools/flights_tools.py` | 航班工具，提供查询用户航班、搜索航班、改签、取消机票。 |
| `tools/hotels_tools.py` | 酒店工具，提供搜索酒店、预订酒店、修改酒店、取消酒店。 |
| `tools/trip_tools.py` | 短途游/旅游推荐工具，提供搜索推荐、预订、修改和取消。 |
| `tools/retriever_vector.py` | 向量检索工具。加载 FAQ 文档，构建检索器，并提供 `lookup_policy()` 用于政策/FAQ 查询。 |
| `tools/order_faq.md` | FAQ/政策知识库文本，被向量检索工具读取。 |
| `tools/tools_handler.py` | LangGraph 工具节点辅助函数。提供工具异常 fallback 和事件打印函数。 |
| `tools/init_db.py` | 初始化或更新测试数据库日期数据，使示例数据更接近当前时间。 |
| `tools/test_db4.sql` | 测试数据库 SQL 脚本。 |
| `tools/location_trans.py` | 城市/地点名称转换工具。 |

### `static/`

| 文件 | 用途 |
| --- | --- |
| `static/graph8.jpg` | 静态图片资源，可通过 FastAPI `/static` 路径访问。 |

### `__pycache__/`

多个目录中存在 `__pycache__/`。这些是 Python 运行时生成的字节码缓存文件，例如 `*.cpython-312.pyc`。它们用于加速模块加载，不需要人工维护，也不应作为主要业务代码阅读对象。

## 四、核心模块说明

### 1. FastAPI 服务模块

核心文件：

- `main.py`
- `api/routers.py`
- `utils/cors.py`
- `utils/handler_error.py`
- `utils/docs_oauth2.py`

服务启动时会创建一个带全局依赖的 FastAPI 应用。全局依赖主要用于接口文档的 OAuth2/JWT 认证展示。`api/routers.py` 汇总业务路由，再由 `main.py` 挂载到应用。

### 2. 用户模块

核心文件：

- `api/system_mgt/user_views.py`
- `api/system_mgt/user_schemas.py`
- `db/system_mgt/models.py`
- `db/system_mgt/user_dao.py`
- `utils/password_hash.py`
- `utils/jwt_utils.py`

用户模块采用典型的三层结构：

- View 层：处理 HTTP 请求。
- Schema 层：定义请求和响应数据结构。
- DAO/Model 层：处理数据库读写。

登录成功后返回用户信息和 JWT token。

### 3. Agent 工作流模块

核心文件：

- `A_frist_version_projct/mian_workflow.py`
- `A_frist_version_projct/CtripAssinstant.py`
- `A_frist_version_projct/child_graph.py`
- `A_frist_version_projct/child_graph_runnnable.py`
- `A_frist_version_projct/agbet_satte_Typeic.py`
- `tools/*_tools.py`

工作流核心是 `StateGraph(Projct_State)`。`Projct_State` 保存：

- `messages`：对话历史；
- `user_info`：当前用户或旅客信息；
- `dialog_state`：当前子助手状态栈。

主助手节点叫 `ctripassitant`。它可以：

- 使用搜索工具；
- 查询政策；
- 搜索航班；
- 将任务转交给专门子助手。

子助手包括：

- `update_flight`：航班相关；
- `book_car_rental`：租车相关；
- `book_hotel`：酒店相关；
- `book_excursion`：短途游/旅游推荐相关。

### 4. 安全工具与敏感工具

子图中通常会把工具分为两类：

- **安全工具**：只查询数据，不修改用户订单或数据库状态。
- **敏感工具**：会创建、修改或取消订单，例如改签、取消、预订等。

`mian_workflow.py` 在 `workflow.compile()` 时通过 `interrupt_before` 指定敏感节点：

- `update_flight_sennsative`
- `book_car_rental_sensitive_tools`
- `book_hotel_sensitive_tools`
- `book_excursion_sensitive_tools`

当工作流即将执行这些节点时会中断，接口层会提示用户输入 `y` 继续。

## 五、接口概览

### 用户接口

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| `GET` | `/api/users/getUsers/` | 获取用户列表。 |
| `GET` | `/api/users/{pk}/` | 按 ID 查询用户。 |
| `POST` | `/api/register/` | 注册用户。 |
| `POST` | `/api/login/` | 用户登录，返回 JWT token。 |
| `POST` | `/api/auth/` | Swagger/OpenAPI 文档中的 OAuth2 表单认证接口。 |
| `PATCH` | `/api/users/{pk}/` | 修改用户。 |
| `POST` | `/api/users/delete/` | 批量删除用户。 |

### 工作流接口

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| `POST` | `/api/graph/` | 调用智能旅行助手工作流。 |

请求体核心字段：

```json
{
  "user_input": "帮我查一下明天去北京的航班",
  "config": {
    "configurable": {
      "passenger_id": "3442 587242",
      "thread_id": "会话ID"
    }
  }
}
```

响应体：

```json
{
  "assistant": "AI 助手返回内容"
}
```

## 六、数据与配置

### 数据库

开发配置中数据库为 MySQL：

- 数据库名：`test_db4`
- 地址：`127.0.0.1:3306`
- 用户名：`root`
- 密码：`123123`
- 字符集：`utf8mb4`

SQLAlchemy 连接配置在 `db/__init__.py` 中生成。

### JWT

JWT 配置位于 `config/development.yml`：

- `JWT_SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`

生成逻辑在 `utils/jwt_utils.py`。

### CORS

允许来源配置在 `config/development.yml` 的 `ORIGINS` 中，由 `utils/cors.py` 加载。

## 七、代码中值得注意的问题

1. **多个文件和变量名存在拼写错误**
   - `A_frist_version_projct`
   - `mian_workflow.py`
   - `agbet_satte_Typeic.py`
   - `finall_garph`
   - `book_fligt_childgrapg`
   - `sennsative`

2. **部分密钥硬编码在代码或配置中**
   - `CtripAssinstant.py` 中存在 Tavily API key 和 DashScope/Qwen API key。
   - `development.yml` 中存在数据库密码和 JWT 密钥。
   - 更推荐使用环境变量或密钥管理服务。

3. **README 和注释存在编码乱码**
   - 建议统一保存为 UTF-8。

4. **`main.py` 中 token 中间件未启用**
   - `middlewares.init_middleware(self.app)` 当前被注释。
   - 当前主要依赖文档 OAuth2 展示和自定义依赖，不等同于完整的全接口强校验。

5. **工作流导图在导入时执行**
   - `mian_workflow.py` 导入时会调用 `draw_graph(finall_garph, 'out.png')` 和 `update_dates()`。
   - 这意味着启动或导入模块时可能产生文件写入和数据库更新副作用。

6. **测试缓存文件已进入仓库目录**
   - `__pycache__/` 通常不建议纳入版本管理。

## 八、推荐阅读顺序

如果要继续维护该项目，建议按以下顺序阅读源码：

1. `main.py`
2. `api/routers.py`
3. `api/graph_api/graph_views.py`
4. `A_frist_version_projct/mian_workflow.py`
5. `A_frist_version_projct/CtripAssinstant.py`
6. `A_frist_version_projct/child_graph.py`
7. `A_frist_version_projct/child_graph_runnnable.py`
8. `tools/flights_tools.py`、`tools/car_tools.py`、`tools/hotels_tools.py`、`tools/trip_tools.py`
9. `db/__init__.py`、`db/dao.py`、`db/system_mgt/user_dao.py`

