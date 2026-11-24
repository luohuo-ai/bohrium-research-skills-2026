# 玻尔科研 Skill 参赛作品首版

十个独立 Skill 对应北化分站赛第一期的十道题。每个目录可独立提交，包含 SKILL.md、专项流程、实际辅助脚本和明确标注的合成接口示例。

实现重点：原始契约适配、证据定位、数值/单位/引用/公式保护、保守文献去重、图谱来源和真实工具运行记录。

本地验证：33 项功能测试通过；学术润色和结构化笔记完成两次独立合成材料试用并复核；十个 Skill 均通过官方格式检查和 submit --dry-run。上述结果不等同于固定 DeepSeek 案例评测或比赛得分。

## 内容

- skills：十个独立 Skill；对应题目见 suite-manifest.json。
- shared：公共 Python 辅助脚本的可维护源文件。
- tests：本地功能测试；TeX 复制隔离测试使用明确的模拟编译器，不代表实际编译成功。
- build_suite.py：从共享源码和专项流程重新生成十个包。
- docs：开发计划和进度记录。

## 使用

让 Agent 读取所选 Skill 的 SKILL.md，再提供实际输入、任务要求和输出契约。平台内按 /input/case.json、task.md、environment/resources.yaml 发现实际资源，结果写 /app/output。

本地测试需要 Python 3；PDF 小样本测试另需 pdfplumber 和 reportlab，否则会明确跳过。运行：

python -B -m unittest discover -s tests

帮助脚本只进行明示的结构、数字、引文或文件检查，不替代科学语义核验。OCR、TeX、Office 渲染及正式固定案例依赖实际平台环境，不假定本地已具备。

## 发布范围

本审阅包不包含凭据、账号配置、私人会话日志、原始材料或正式测试答案。GitHub 公开链接尚未填写或发布；待用户明确授权后再执行。