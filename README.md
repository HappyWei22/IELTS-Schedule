# 雅思培训机构排课管理系统

这是一个前后端分离的本地可运行项目，用于雅思培训机构助教或教学主管管理学生、老师和课程排课。

当前已完成第一阶段、第二阶段、第三阶段和第四阶段：

- 学生管理：新增、编辑、删除、列表、按姓名搜索
- 老师管理：新增、编辑、删除、列表、按姓名搜索
- 排课管理：新增、编辑、删除、列表、按日期/学生/老师筛选
- 后端保存课程前自动检测老师和学生时间冲突
- 首页仪表盘基础统计
- 每日总课表：按日期查看当天全部课程，按时间排序，可复制提醒消息
- 学生个人课表：按学生和日期范围查看课程
- 老师月度统计：按老师和月份查看课程、总课程数、总课时数、按课程类型统计课时
- CSV 导出：每日总课表、学生个人课表、老师月度课表均可导出 CSV
- 页面优化：统一产品级视觉系统、工作台首页、加载/空态/错误提示、响应式布局
- 使用指南：新增助教操作流程、冲突规则和常见检查入口
- 移动端适配：窄屏下保留高密度表格，并提供横向滑动提示
- 批量管理：学生和老师支持勾选后批量修改、批量删除
- 状态颜色：学生状态按在读、暂停、结课显示不同颜色

## 技术栈

- 前端：Vue3 + Vite + Vue Router + axios
- 后端：FastAPI + SQLAlchemy
- 数据库：SQLite
- 接口风格：REST API

## 项目结构

```text
ielts-scheduler/
├── frontend/
│   ├── package.json
│   ├── index.html
│   ├── vite.config.js
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── api/
│       ├── views/
│       ├── components/
│       └── router/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── requirements.txt
│   ├── routers/
│   └── services/
└── README.md
```

## macOS 启动步骤

项目实际位置：

```text
/Users/sxw/Documents/IELTS Schedule/ielts-scheduler
```

macOS 终端路径使用正斜杠 `/`。因为 `IELTS Schedule` 中间有空格，所以 `cd` 路径必须加英文双引号。

### 1. 启动后端

```bash
cd "/Users/sxw/Documents/IELTS Schedule/ielts-scheduler/backend"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

项目已经在 `backend/requirements.txt` 中加入本地开发用的 PyPI 可信主机配置，用来规避 macOS 常见的 pip SSL 证书问题。通常直接运行 `pip install -r requirements.txt` 即可。

后端地址：

- API 根地址：http://127.0.0.1:8000
- 接口文档：http://127.0.0.1:8000/docs

### 2. 启动前端

另开一个终端：

```bash
cd "/Users/sxw/Documents/IELTS Schedule/ielts-scheduler/frontend"
npm install
npm run dev
```

前端访问地址：

- http://localhost:5173

## Windows 启动步骤

Windows 终端路径使用反斜杠 `\`。下面命令假设项目放在当前命令行所在目录下；如果项目在其他位置，请先切换到对应磁盘和文件夹。

### 1. 启动后端

```bat
cd ielts-scheduler\backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

后端地址：

- API 根地址：http://127.0.0.1:8000
- 接口文档：http://127.0.0.1:8000/docs

### 2. 启动前端

另开一个终端：

```bat
cd ielts-scheduler\frontend
npm install
npm run dev
```

前端访问地址：

- http://localhost:5173

## 如何验证系统运行成功

1. 打开 http://127.0.0.1:8000/docs。
2. 能看到 FastAPI 接口文档，说明后端启动成功。
3. 打开 http://localhost:5173。
4. 能看到“首页仪表盘”，说明前端启动成功。
5. 进入“学生管理”，新增一个学生。
6. 进入“老师管理”，新增一个老师。
7. 进入“排课管理”，搜索并选择学生，再选择老师后新增课程。
8. 进入“每日总课表”，选择日期查看当天全部课程。
9. 进入“学生课表”，选择学生和日期范围查看个人课表。
10. 进入“老师月度统计”，选择老师和月份查看课时统计。
11. 在三个课表页面点击“导出 CSV”，确认浏览器下载 CSV 文件。
12. 进入“使用指南”，确认操作流程、冲突规则和快捷入口可正常查看。
13. 在学生管理或老师管理中点击“多选”，勾选多条记录，确认可以批量修改或批量删除。

## 从 Excel 导入 7 月课时数据

项目已经提供导入脚本：

```text
backend/scripts/import_july_xlsx.py
```

默认导入文件：

```text
/Users/sxw/工作/7月课时.xlsx
```

导入规则：

- 学生按姓名去重导入。
- 老师按姓名去重导入。
- 课程只导入 `2025-07` 中能解析出日期和时间段的记录。
- 重复运行时，已存在的同一学生、同一老师、同一科目、同一天、同一时间段课程会自动跳过。
- 导入前会自动备份数据库，备份文件保存在 `backend/` 目录。

导入 Excel 前需要额外安装导入依赖：

```bash
cd "/Users/sxw/Documents/IELTS Schedule/ielts-scheduler/backend"
source .venv/bin/activate
pip install -r requirements-import.txt
```

先预览，不写入数据库：

```bash
cd "/Users/sxw/Documents/IELTS Schedule/ielts-scheduler"
python backend/scripts/import_july_xlsx.py --dry-run
```

正式导入：

```bash
cd "/Users/sxw/Documents/IELTS Schedule/ielts-scheduler"
python backend/scripts/import_july_xlsx.py
```

如果你使用的是 Codex 内置 Python，也可以运行：

```bash
cd "/Users/sxw/Documents/IELTS Schedule/ielts-scheduler"
/Users/sxw/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 backend/scripts/import_july_xlsx.py
```

## 第一阶段验收测试

建议按下面步骤测试：

1. 新增学生：姓名填写“李同学”，状态选择“在读”。
2. 新增老师：姓名填写“张老师”，科目填写“写作”。
3. 新增课程：
   - 学生：在学生搜索框输入“李同学”，从结果中点击选择
   - 老师：张老师
   - 课程类型：写作
   - 日期：2026-06-20
   - 开始时间：10:00
   - 结束时间：11:00
   - 结果：应保存成功。
4. 再新增一节同一老师、同一天、时间为 10:30-11:30 的课程。
   - 结果：应保存失败，并提示老师排课冲突。
5. 再新增一节同一学生、同一天、时间为 10:30-11:30 的课程。
   - 结果：应保存失败，并提示学生排课冲突。
6. 新增一节同一老师、同一天、时间为 11:00-12:00 的课程。
   - 结果：应保存成功，因为 11:00 正好接上一节课结束，不算冲突。
7. 编辑已有课程并保存。
   - 结果：不应和自己产生冲突。
8. 删除没有关联课程的学生或老师。
   - 结果：应删除成功。
9. 删除已有课程关联的学生或老师。
   - 结果：会被阻止，并提示先删除相关课程。

## 第二阶段验收测试

建议先保留第一阶段创建的学生、老师和课程，再继续测试：

1. 进入“每日总课表”。
   - 选择有课程的日期，例如 `2026-06-20`。
   - 结果：应看到当天全部课程，按开始时间排序。
2. 点击单节课程的“复制”。
   - 结果：浏览器剪贴板中应出现类似 `亲们，咱们明天写作上课时间为 6 月 20 号 10:00-11:00 哈～` 的提醒文本。
3. 点击“复制全部提醒”。
   - 结果：当天所有课程提醒会按行复制。
4. 进入“学生课表”。
   - 选择学生，并选择覆盖已有课程的日期范围。
   - 结果：应看到该学生在范围内的所有课程。
5. 点击“本周”或“本月”。
   - 结果：日期范围会自动切换。
6. 进入“老师月度统计”。
   - 选择老师和月份，例如 `2026-06`。
   - 结果：应看到当月总课程数、总课时数、按课程类型统计课时，以及每节课明细。

## 第三阶段验收测试

建议先确保后端和前端都已经启动，并且系统里已有课程数据：

1. 进入“每日总课表”。
   - 选择有课程的日期。
   - 点击“导出 CSV”。
   - 结果：浏览器应下载 `每日总课表-日期.csv`，字段包含上课时间、学生姓名、老师姓名、课程类型、时长、备注，并在文件底部包含总时长。
2. 进入“学生课表”。
   - 选择学生和日期范围。
   - 点击“导出 CSV”。
   - 结果：浏览器应下载该学生课表 CSV，字段包含日期、上课时间、课程类型、老师姓名、时长、备注，并在文件底部包含总时长。
3. 进入“老师月度统计”。
   - 选择老师和月份。
   - 点击“导出 CSV”。
   - 结果：浏览器应下载老师月度课表 CSV，字段包含日期、开始时间、结束时间、学生姓名、课程类型、时长、备注，并在文件底部包含总课程数和总课时数。
4. 用 Excel、Numbers 或 WPS 打开 CSV。
   - 结果：中文应正常显示，不应乱码。

## 第四阶段验收测试

1. 打开首页。
   - 结果：应看到“今日工作台”、今日课程、本月课程、学生数量、老师数量、今日课程列表、近期安排和常用操作入口。
2. 在侧边栏切换页面。
   - 结果：导航按“日常工作 / 资料与统计 / 支持”分组，当前页面高亮清晰。
3. 进入学生、老师、排课页面并保存表单。
   - 结果：保存按钮会显示“保存中...”，成功或失败提示清晰。
4. 进入每日总课表和学生课表。
   - 结果：页面会展示课程数和总时长，和 CSV 导出统计一致。
5. 缩小浏览器宽度到手机或平板尺寸。
   - 结果：侧边栏会变成横向导航，表单和统计模块会单列显示，不应出现文字重叠。
6. 进入“使用指南”。
   - 结果：应看到推荐工作流、冲突规则、常见检查和快捷入口。
7. 在手机宽度下进入学生管理、老师管理、排课管理。
   - 结果：右侧表格应保持高密度表格样式，并显示横向滑动提示，方便查看更多列。
8. 在学生管理中查看状态标签。
   - 结果：在读为绿色，暂停为橙色，结课为红色。
9. 在学生管理中点击“多选”后勾选多个学生。
   - 选择批量状态或填写批量备注后点击“批量修改”。
   - 结果：提交后应提示修改数量，学生列表刷新。
10. 在学生管理中点击“多选”，勾选没有课程关联的学生后点击“批量删除”。
   - 结果：提交后应提示删除数量；如果有关联课程，系统应阻止删除并提示具体学生。
11. 在老师管理中点击“多选”后勾选多个老师。
   - 填写批量科目或批量备注后点击“批量修改”。
   - 结果：提交后应提示修改数量，老师列表刷新。
12. 在老师管理中点击“多选”，勾选没有课程关联的老师后点击“批量删除”。
   - 结果：提交后应提示删除数量；如果有关联课程，系统应阻止删除并提示具体老师。

## 已实现接口

学生接口：

- `GET /api/students?keyword=`
- `POST /api/students`
- `PUT /api/students/bulk`
- `POST /api/students/bulk-delete`
- `PUT /api/students/{id}`
- `DELETE /api/students/{id}`

老师接口：

- `GET /api/teachers?keyword=`
- `POST /api/teachers`
- `PUT /api/teachers/bulk`
- `POST /api/teachers/bulk-delete`
- `PUT /api/teachers/{id}`
- `DELETE /api/teachers/{id}`

课程接口：

- `GET /api/courses?date=&student_id=&teacher_id=`
- `POST /api/courses`
- `PUT /api/courses/{id}`
- `DELETE /api/courses/{id}`
- `POST /api/courses/check-conflict`

课表接口：

- `GET /api/schedules/daily?date=YYYY-MM-DD`
- `GET /api/schedules/student/{student_id}?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- `GET /api/schedules/teacher/{teacher_id}/monthly?month=YYYY-MM`

导出接口：

- `GET /api/export/daily?date=YYYY-MM-DD`
- `GET /api/export/student/{student_id}?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- `GET /api/export/teacher/{teacher_id}/monthly?month=YYYY-MM`

## 冲突检测规则

保存课程前，后端会检查同一天同一老师或同一学生是否有重叠课程。

判断逻辑：

```text
新课程开始时间 < 已有课程结束时间
并且
新课程结束时间 > 已有课程开始时间
```

示例：

- 已有课程 10:00-11:00，新课程 10:30-11:30：冲突
- 已有课程 10:00-11:00，新课程 11:00-12:00：不冲突

## 常见问题

### 前端页面提示接口请求失败

请确认后端已经启动，并且地址是：

```text
http://127.0.0.1:8000
```

### macOS 提示 `cd: no such file or directory`

请使用 README 里的完整路径：

```bash
cd "/Users/sxw/Documents/IELTS Schedule/ielts-scheduler/backend"
```

不要写成：

```bash
cd ielts-scheduler\backend
```

这是 Windows 路径写法，在 macOS 终端里会被解析错。

### macOS 安装后端依赖时报 SSL 证书错误

如果看到类似下面的错误：

```text
SSLError(SSLCertVerificationError: certificate verify failed)
Could not fetch URL https://pypi.org/simple/fastapi/
```

项目已经把可信主机配置写入 `backend/requirements.txt`，请先确认你是在后端目录运行：

```bash
cd "/Users/sxw/Documents/IELTS Schedule/ielts-scheduler/backend"
source .venv/bin/activate
pip install -r requirements.txt
```

如果仍然失败，通常是 macOS 上 Python 的证书没有正确安装。可以再尝试下面的方法：

```bash
open "/Applications/Python 3.12/Install Certificates.command"
```

如果你的 Python 版本不是 3.12，可以先查看版本：

```bash
python3 --version
```

然后把命令里的 `Python 3.12` 改成你的版本，例如：

```bash
open "/Applications/Python 3.11/Install Certificates.command"
```

运行完成后，回到后端目录重新安装依赖：

```bash
cd "/Users/sxw/Documents/IELTS Schedule/ielts-scheduler/backend"
source .venv/bin/activate
pip install -r requirements.txt
```

也可以直接使用可信主机方式安装：

```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

这个方式适合作为本地开发临时处理。长期建议修复 Python 证书后再正常使用 `pip install -r requirements.txt`。

如果运行 `Install Certificates.command` 时出现权限错误：

```text
Permission denied: '/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/certifi'
```

说明系统 Python 目录没有当前用户写入权限。此时不需要卡在证书脚本上，直接在项目虚拟环境里安装依赖：

```bash
cd "/Users/sxw/Documents/IELTS Schedule/ielts-scheduler/backend"
source .venv/bin/activate
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

安装成功后启动后端：

```bash
uvicorn main:app --reload
```

### 端口 8000 被占用

可以换一个端口启动后端：

```bash
uvicorn main:app --reload --port 8001
```

同时需要修改 `frontend/vite.config.js` 里的代理地址。

### 端口 5173 被占用

Vite 通常会自动切换到另一个端口。请以终端输出的地址为准。

### 数据库在哪里

首次启动后端时会自动创建 SQLite 数据库文件：

```text
backend/ielts_scheduler.db
```

如需清空本地测试数据，可以停止后端后删除这个文件，再重新启动后端。

## 后续阶段

第二阶段已完成：

- 每日总课表
- 学生个人课表
- 老师月度课表

第三阶段已完成：

- 每日课表 CSV 导出
- 学生课表 CSV 导出
- 老师月度课表 CSV 导出

第四阶段已完成：

- 页面布局
- 表单体验
- 错误提示
- 仪表盘展示
- 使用指南页面
