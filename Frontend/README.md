# CMS Frontend

基于 `React + Vite + TypeScript + Ant Design` 的 CMS 前端项目。

## 启动方式

```bash
npm install
npm run dev
```

默认本地地址：`http://localhost:5173`

## 构建

```bash
npm run build
```

## 页面路由

- `/login`
- `/dashboard`
- `/users`
- `/orders`
- `/media`
- `/analytics`
- `/roles`
- `/settings`
- `/profile`
- `/logs`

## 目录结构

- `src/layouts`：后台壳层布局
- `src/router`：路由配置
- `src/pages`：业务页面
- `src/components`：复用组件
- `src/mocks`：演示数据
- `src/services`：API 抽象层
- `src/styles`：主题与全局样式

## 本地联调步骤

1. 启动后端（端口 `8000`）：

```bash
cd ../Backend
bash scripts/run_dev.sh
```

2. 启动前端（端口 `5173`，已配置 `/api` 与 `/static` 代理）：

```bash
cd ../Frontend
npm install
npm run dev
```

3. 登录后台：默认账号 `admin / admin123456`。

4. 如需调整默认管理员账号或密码，请在后端的种子数据/环境配置中修改后重启后端服务。
