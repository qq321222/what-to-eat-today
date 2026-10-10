# 依赖配置指南

本技能依赖麦当劳 MCP（mcd-mcp）与 Python 运行环境。环境检查由 scripts/check_environment.py 完成（只读，不修改配置、不登录、不输出凭据）。

## 麦当劳 MCP（mcd-mcp，必需）

- 用途：门店、菜单、券、试算、下单与订单状态的全部真实数据。
- 受影响功能：全部点餐流程；缺失时无法提供真实价格与下单。
- 服务端点：https://mcp.mcd.cn（streamablehttp），注册于 WorkBuddy MCP 配置。
- 麦当劳官方主页：https://www.mcdonalds.com.cn

配置步骤：

1. 打开 WorkBuddy 对话窗口左下角「+」连接器菜单。
2. 搜索「麦当劳」，安装麦当劳 MCP 连接器。
3. 按提示完成账号授权；在连接器管理页对新服务器点击「信任」以启用。
4. 确认连接器状态为已连接/已启用。

验证：在对话中说「帮我点麦当劳」或询问当前时间（对应 now-time-info 工具）；能返回门店、时间等真实数据即连接正常。

凭据与安全：

- 凭据由 WorkBuddy 连接器托管并加密存储于本地配置；不要在对话中粘贴 Token、密码或验证码。
- 仅授予点餐所需最小能力；对话中不要求提供任何凭据明文。

轮换与撤销：在连接器管理页禁用或解绑麦当劳连接器即撤销授权；重新走一遍授权流程即可完成轮换。

核验日期：2026-10-10；适用版本：mcd-mcp（streamablehttp）。

## Python 运行环境（python-runtime，可选）

- 用途：运行 scripts/combo_builder.py 与 scripts/compare_plans.py（仅标准库，无网络、无子进程）。
- 受影响功能：搭配生成与比价汇总的自动化；缺失时按 SKILL.md 脚本降级执行人工推理与手算，主流程不中断。
- 最低版本：Python 3.10。
- 官方主页：https://www.python.org ；官方文档：https://docs.python.org ；下载：https://www.python.org/downloads/
- 验证：运行 `python --version`，输出 3.10 及以上。

## 环境状态路由

- ready：跳过本指南，直接进入点餐流程。
- needs_setup：只展示缺失必需项（mcd-mcp）的上述配置步骤，完成后重新运行检查。
- partial：继续可用功能，仅说明受影响功能（如 Python 缺失时搭配与比价结果标注「估算」）。
- unavailable：展示原因（认证失效/服务故障/权限不足）与恢复步骤；mcd-mcp 不可用时不承诺任何真实价格与下单。
