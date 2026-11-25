# 科研 Skill 候选版 v0.3

本目录是十题作品的改进候选版。它补充环境/安装说明、只读依赖探测和十个可运行的合成微型示例；核心科研辅助脚本沿用已审阅版本。该版本不代表平台 RuntimeError 已修复，也未形成正式比赛得分。

## 内容和复现

- skills/：十个独立文本Skill。每题新的 examples/worked/ 给出输入、命令、真实脚本产物预览和验证范围。
- shared/：维护版公共脚本；tests/：回归与示例产物集成检查。
- build_suite.py 和 build_worked_examples.py：重建包；从本目录运行 python build_worked_examples.py 即可补齐生成资源。
- suite-manifest.json：每题文件数、体积与逐文件SHA256。

使用Python3.10+，先阅读所选Skill的 references/environment.md。局部示例依赖按 examples/worked/requirements-demo.txt 安装到独立虚拟环境。运行示例时，把 --out 指到Skill目录之外。

v0.3本次完成标准Skill格式脚本、公共脚本回归和实际合成产物检查。旧版曾做Playground CLI打包预检；v0.3没有进行新的含会话轨迹ARM打包或正式上传。它们都不等于官方固定案例/DeepSeek Harness评测。示例是确定性脚本演示，不是Agent质量或增益对照实验。

Windows十个合成微型例子实际运行并通过各自检查；数据冲突和无编译器的情况保留partial。现有Ubuntu Python3.12实测八个标准库示例，PDF和RDF的Linux额外依赖未安装，所以那两项未跑。没有伪造OCR、TeX编译、Office预览或官方案例分数。

原有提交记录和原包保留。完整失败原因尚需平台后台日志，公开仓库不包含私人对话轨迹、账号配置、凭据、正式案例或正式答案。

本次源码候选版回归35项通过，Windows十个脚本化合成示例通过各自局部检查；不等于官方案例成功。
