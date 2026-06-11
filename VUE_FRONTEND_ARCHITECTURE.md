# Vue 前端架构方案

## 1. 方案目标

本方案用于构建一个可维护、可扩展、适合长期迭代的 Vue 前端项目。整体设计重点包括：

- 降低页面开发和维护成本
- 统一代码组织、请求、状态、路由和权限模型
- 支持多人协作和模块化交付
- 保持良好的类型约束、工程规范和构建性能
- 为后续接入更多业务模块、主题体系、权限体系和部署环境预留空间

## 2. 技术选型

| 类型 | 推荐方案 | 说明 |
| --- | --- | --- |
| 前端框架 | Vue 3 | 使用 Composition API，适合复杂业务拆分 |
| 构建工具 | Vite | 启动快、配置轻、生态成熟 |
| 开发语言 | TypeScript | 提升接口、组件、状态和工具函数的可维护性 |
| 路由管理 | Vue Router | 管理页面路由、权限路由和路由守卫 |
| 状态管理 | Pinia | 管理用户信息、权限、菜单、主题和跨页面状态 |
| HTTP 请求 | Axios | 统一封装请求、响应、错误、鉴权和重试逻辑 |
| UI 组件库 | Element Plus | 适合中后台业务系统，组件完整 |
| 样式方案 | SCSS | 支持变量、混入、模块化样式和主题扩展 |
| 代码规范 | ESLint + Prettier | 统一团队编码风格 |
| 提交规范 | Husky + lint-staged | 在提交前自动检查代码质量 |
| 测试工具 | Vitest | 用于工具函数、状态逻辑和关键组件测试 |

## 3. 总体架构

前端整体分为五层：

| 层级 | 职责 |
| --- | --- |
| 展示层 | 页面、布局、组件、交互 |
| 业务层 | 业务页面逻辑、业务组件、业务 Hook |
| 状态层 | 全局状态、用户状态、权限状态、页面缓存状态 |
| 服务层 | API 封装、请求拦截、响应处理、接口类型 |
| 基础层 | 工具函数、常量、样式变量、类型定义、工程配置 |

架构关系如下：

```text
用户界面
  |
  |-- views 页面
  |-- layouts 布局
  |-- components 通用组件
  |
业务逻辑
  |
  |-- hooks 组合式逻辑
  |-- stores 状态管理
  |
数据服务
  |
  |-- api 接口模块
  |-- request 请求封装
  |
基础能力
  |
  |-- utils 工具函数
  |-- types 类型定义
  |-- styles 样式体系
  |-- router 路由与权限
```

## 4. 目录结构

推荐目录结构如下：

```text
src/
  api/
    modules/
    request.ts
    types.ts
  assets/
    images/
    icons/
  components/
    common/
    business/
  hooks/
  layouts/
    BasicLayout.vue
    AuthLayout.vue
  router/
    index.ts
    routes.ts
    guard.ts
  stores/
    modules/
      user.ts
      permission.ts
      app.ts
    index.ts
  styles/
    variables.scss
    reset.scss
    global.scss
    theme.scss
  types/
    user.ts
    api.ts
    route.ts
  utils/
    auth.ts
    storage.ts
    format.ts
    validate.ts
  views/
    login/
    dashboard/
    system/
  App.vue
  main.ts
```

目录职责说明：

| 目录 | 职责 |
| --- | --- |
| `api` | 统一管理后端接口、请求实例、接口类型 |
| `assets` | 静态资源，如图片、图标、字体 |
| `components/common` | 与业务无关的通用组件 |
| `components/business` | 可复用的业务组件 |
| `hooks` | 可复用的组合式逻辑 |
| `layouts` | 页面整体布局 |
| `router` | 路由表、路由守卫、动态路由 |
| `stores` | Pinia 状态模块 |
| `styles` | 全局样式、主题变量、样式重置 |
| `types` | 全局 TypeScript 类型 |
| `utils` | 工具函数 |
| `views` | 页面级组件 |

## 5. 路由设计

路由分为三类：

| 类型 | 示例 | 说明 |
| --- | --- | --- |
| 静态路由 | 登录页、404 页面 | 不依赖权限，项目启动时固定存在 |
| 基础业务路由 | 首页、个人中心 | 登录后默认可访问 |
| 权限路由 | 用户管理、角色管理、业务模块 | 根据后端权限动态生成 |

推荐路由结构：

```ts
{
  path: '/system/user',
  name: 'SystemUser',
  component: () => import('@/views/system/user/index.vue'),
  meta: {
    title: '用户管理',
    requiresAuth: true,
    permission: 'system:user:list',
    keepAlive: true
  }
}
```

路由守卫职责：

- 判断是否已登录
- 自动跳转登录页
- 拉取用户信息和权限
- 生成动态菜单和动态路由
- 设置页面标题
- 处理无权限访问

## 6. 权限设计

权限建议分为三层：

| 权限类型 | 控制对象 | 实现方式 |
| --- | --- | --- |
| 路由权限 | 页面是否可进入 | 路由 `meta.permission` |
| 菜单权限 | 菜单是否展示 | 后端菜单权限或前端过滤 |
| 按钮权限 | 操作按钮是否展示 | 指令或工具函数判断 |

按钮权限推荐封装为指令：

```ts
v-permission="'system:user:create'"
```

权限数据建议由后端返回，前端只负责消费和展示，不在前端硬编码业务权限归属。

## 7. 状态管理设计

Pinia Store 建议按领域拆分：

| Store | 职责 |
| --- | --- |
| `user` | token、用户信息、角色、权限 |
| `permission` | 菜单、动态路由、按钮权限 |
| `app` | 侧边栏状态、主题、语言、全局配置 |
| `tabs` | 多标签页、页面缓存 |

状态设计原则：

- 只把跨页面共享的数据放入 Store
- 页面内部临时状态保留在页面组件中
- 复杂页面逻辑优先抽到 `hooks`
- Store 中不直接写 UI 细节，避免状态层和展示层耦合

## 8. 请求设计

请求层统一封装在 `src/api/request.ts`，核心能力包括：

- 基础地址配置
- 请求超时配置
- token 自动注入
- 请求参数处理
- 响应数据解包
- 业务错误处理
- 登录过期处理
- 网络异常提示

推荐 API 模块写法：

```ts
import request from '@/api/request'

export function getUserList(params: UserListParams) {
  return request.get<PageResult<UserItem>>('/system/users', { params })
}
```

接口返回建议统一格式：

```ts
interface ApiResponse<T> {
  code: number
  message: string
  data: T
}
```

分页返回建议统一格式：

```ts
interface PageResult<T> {
  list: T[]
  total: number
  page: number
  pageSize: number
}
```

## 9. 组件设计

组件分为两类：

| 类型 | 说明 |
| --- | --- |
| 通用组件 | 不绑定具体业务，如表格容器、搜索表单、上传组件 |
| 业务组件 | 与业务概念相关，如用户选择器、角色分配弹窗 |

建议优先沉淀以下组件：

- `BaseTable`：统一表格、分页、加载状态
- `SearchForm`：统一查询表单
- `FormDialog`：统一新增、编辑弹窗
- `PageContainer`：统一页面标题、操作区和内容区
- `PermissionButton`：统一按钮权限控制
- `UploadFile`：统一文件上传

组件设计原则：

- 通用组件不直接调用业务接口
- 业务组件可以组合 API 和 Store
- 组件对外暴露清晰的 `props` 和 `emits`
- 表单、表格、弹窗优先配置化，但不要过度封装

## 10. 样式与主题

样式采用全局变量加局部样式的方式：

```scss
:root {
  --color-primary: #246bfe;
  --color-success: #16a34a;
  --color-warning: #d97706;
  --color-danger: #dc2626;
  --text-primary: #1f2937;
  --text-secondary: #6b7280;
  --border-color: #e5e7eb;
  --page-bg: #f6f8fb;
}
```

样式规范：

- 全局颜色、间距、圆角、阴影使用变量
- 页面布局统一使用 `PageContainer`
- 避免在页面中散落大量重复样式
- 业务页面优先保持信息清晰、操作高效
- 暗色模式或多主题可以后续基于 CSS 变量扩展

## 11. 登录与鉴权流程

登录流程：

```text
用户输入账号密码
  |
调用登录接口
  |
保存 token
  |
拉取用户信息
  |
拉取权限和菜单
  |
生成动态路由
  |
进入首页
```

登录状态恢复流程：

```text
刷新页面
  |
检查本地 token
  |
拉取用户信息和权限
  |
恢复动态路由
  |
进入目标页面
```

退出登录流程：

```text
调用退出接口
  |
清理 token、用户信息、权限和缓存页面
  |
跳转登录页
```

## 12. 环境配置

推荐按环境拆分配置：

```text
.env.development
.env.test
.env.production
```

示例：

```text
VITE_APP_TITLE=业务管理系统
VITE_API_BASE_URL=/api
VITE_APP_ENV=development
```

环境配置原则：

- 接口地址、构建环境、应用标题通过环境变量控制
- 敏感信息不写入前端环境变量
- 生产环境开启压缩和构建分析
- 测试环境与生产环境保持接近

## 13. 构建与部署

构建流程：

```text
安装依赖
  |
代码检查
  |
类型检查
  |
单元测试
  |
生产构建
  |
部署 dist 目录
```

推荐命令：

```bash
npm run lint
npm run type-check
npm run test
npm run build
```

部署建议：

- 使用 Nginx 托管静态资源
- 前端路由使用 history 模式时配置 fallback
- API 代理由 Nginx 或网关处理
- 静态资源设置合理缓存策略
- HTML 文件不做强缓存，避免版本更新不生效

Nginx 示例：

```nginx
location / {
  try_files $uri $uri/ /index.html;
}

location /api/ {
  proxy_pass http://backend-service/;
}
```

## 14. 代码规范

命名规范：

| 类型 | 规范 | 示例 |
| --- | --- | --- |
| 组件文件 | PascalCase | `UserSelect.vue` |
| 页面目录 | kebab-case 或业务名 | `user-management` |
| 工具函数 | camelCase | `formatDate` |
| 类型定义 | PascalCase | `UserInfo` |
| 常量 | UPPER_CASE | `TOKEN_KEY` |
| Store | camelCase | `useUserStore` |

开发规范：

- 组件单文件保持职责清晰
- API、类型、页面逻辑分离
- 禁止在多个页面复制相同请求和转换逻辑
- 表单校验规则尽量集中维护
- 提交前必须通过 lint 和类型检查

## 15. 测试策略

测试优先覆盖以下内容：

- 工具函数
- 请求参数转换
- 权限判断逻辑
- Store 行为
- 关键业务组件
- 复杂表单校验

推荐测试分层：

| 类型 | 工具 | 覆盖内容 |
| --- | --- | --- |
| 单元测试 | Vitest | 工具函数、Store、Hook |
| 组件测试 | Vue Test Utils | 通用组件和关键业务组件 |
| 端到端测试 | Playwright | 登录、核心业务流程 |

## 16. 性能优化

推荐优化方向：

- 路由懒加载
- 大组件按需加载
- UI 组件库按需引入
- 图片压缩和懒加载
- 表格大数据场景使用分页或虚拟滚动
- 合理使用 `keep-alive`
- 生产环境开启 gzip 或 brotli
- 使用构建分析检查包体积

路由懒加载示例：

```ts
component: () => import('@/views/system/user/index.vue')
```

## 17. 风险与应对

| 风险 | 影响 | 应对 |
| --- | --- | --- |
| 权限逻辑分散 | 难维护、容易漏控 | 统一路由守卫、权限指令和 Store |
| 组件过度封装 | 灵活性下降 | 只封装稳定、重复、高频的能力 |
| 接口类型缺失 | 联调成本高 | 所有 API 定义请求和响应类型 |
| 页面状态混乱 | 维护困难 | 页面状态、Store 状态、缓存状态明确边界 |
| 样式不统一 | 体验割裂 | 建立变量、布局组件和基础样式规范 |
| 构建配置膨胀 | 升级困难 | 保持 Vite 配置简洁，复杂能力模块化 |

## 18. 迭代计划

第一阶段：项目基础搭建

- 初始化 Vue 3 + Vite + TypeScript 项目
- 接入路由、Pinia、Element Plus、SCSS
- 配置 ESLint、Prettier、环境变量
- 完成基础布局和登录页

第二阶段：核心能力建设

- 封装请求层
- 实现登录鉴权
- 实现路由守卫
- 实现权限菜单和按钮权限
- 沉淀基础页面容器、表格、表单、弹窗组件

第三阶段：业务模块开发

- 开发首页仪表盘
- 开发用户、角色、菜单等系统模块
- 按业务域扩展页面和 API
- 建立业务组件库

第四阶段：质量与上线

- 补充关键测试
- 优化构建体积
- 完善异常页和空状态
- 配置生产部署
- 输出前端开发规范文档

## 19. 推荐落地顺序

建议按照以下顺序实施：

1. 搭建项目基础工程
2. 建立目录结构和编码规范
3. 接入 UI 组件库和全局样式
4. 实现登录和请求封装
5. 实现路由守卫和权限模型
6. 搭建主布局和菜单
7. 沉淀表格、表单、弹窗等通用组件
8. 开发第一批业务页面
9. 补充测试、异常处理和部署配置

## 20. 总结

本架构方案以 Vue 3、TypeScript、Vite、Pinia、Vue Router 和 Element Plus 为核心，适合构建中后台、业务管理系统和企业内部应用。整体设计强调清晰分层、统一规范、权限可控、组件可复用和工程可持续演进。

后续如果业务规模扩大，可以继续扩展为微前端、多主题、多语言、低代码配置页面或组件物料库，但初始阶段应优先保证基础架构简单、稳定、易维护。
