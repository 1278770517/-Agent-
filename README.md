# 智能旅行助手 (AI Travel Assistant)

## 项目介绍 (Introduction)
本项目是一个基于大语言模型（LLM）和工作流（Workflow）的智能旅行助手（以携程/瑞士航空客户服务为背景）。该系统可以通过自然语言对话与用户进行交互，并调用各类外部工具（如航班查询、酒店预订、租车服务、政策解答等），为用户提供一站式、智能化的商旅出行规划和预订服务。

项目利用基于图的代理系统（Graph-based Agent）实现复杂状态流转与任务分发，能够在不同专业子助手之间进行路由（例如航班预订助手、租车助手、酒店预订助手等），并且在执行敏感操作（如修改/取消预订）时支持人工干预和确认（Human-in-the-loop）。

## 系统架构 (Architecture)
项目的核心架构由 **Web 服务层** 和 **AI 代理工作流层** 两部分组成。

### 1. Web 服务层 (FastAPI Backend)
基于 `FastAPI` 构建提供高并发支持的异步 API 接口，负责与前端或客户端进行交互。
- **主入口**：`main.py` 启动 Uvicorn 服务器并初始化应用。
- **路由管理**：`api/routers.py` 及 `api/graph_api/graph_views.py` 定义了接口路由，其中 `/api/graph/` 接口专门用于接收用户对话并驱动底层 AI 工作流。
- **全局配置及拦截**：使用自定义的 OAuth2 进行认证，同时包含全局跨域（CORS）与异常处理（`utils/`）。

### 2. AI 代理工作流层 (LangGraph & LangChain)
基于 `LangChain` 和 `LangGraph` 框架构建了复杂的多层级 Agent 结构，实现了灵活的状态机管理（StateGraph）。工作流的主要实现在 `A_frist_version_projct` 目录下：
- **核心大脑 (Main Workflow)**：`mian_workflow.py` 定义了全局的图结构（StateGraph），并在入口引入 `CtripAssinstant` 进行意图识别。
- **状态管理**：`agbet_satte_Typeic.py` 定义了基于图的状态模型（如 `Projct_State`），记录对话历史、当前处理节点和用户信息。
- **子图 (Child Graphs)**：通过模块化的子图设计，将任务下发给具体的领域专家（在 `child_graph.py` 中定义）：
  - 航班预订助手 (`book_fligt_childgrapg`)
  - 租车服务助手 (`build_car_graph`)
  - 酒店预订助手 (`builder_hotel_graph`)
  - 周边短途游助手 (`builder_excursion_graph`)
- **大模型 (LLM)**：默认使用通义千问模型 (`ChatTongyi` - `qwen-plus`) 作为推理大脑，通过 `bind_tools` 绑定外部工具能力。

### 3. 工具与集成服务 (Tools & Services)
`tools/` 目录下实现了丰富的外部服务集成封装，供 Agent 节点调用：
- **交通与住宿**：`flights_tools.py`（航班），`hotels_tools.py`（酒店），`car_tools.py`（租车），`trip_tools.py`（短途旅行）。提供查询、预订、修改、取消等全套操作。
- **知识库与政策**：通过向量检索（`retriever_vector.py`）读取基于 Markdown 的 FAQ（如 `order_faq.md`）解答用户相关政策疑问。
- **网络搜索**：集成了 `TavilySearchResults` 等工具用于实时外部信息搜索。
- **数据库**：使用 SQLite 等关系型数据库（`init_db.py`, `.sql` 文件）来持久化管理航班、预订和用户状态。

### 4. 关键特性 (Key Features)
- **多智能体协作**：主助手负责意图路由，特定任务交由领域子助手处理。
- **敏感操作拦截**：预定、取消等关键修改类工具在工作流中设置了中断（interrupt_before），需等待用户确认（Y/N）后才能放行执行。
- **持久化记忆**：使用 `MemorySaver` 来维护会话级别的上下文及状态，支持从断点继续执行对话。
