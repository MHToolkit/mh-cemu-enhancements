# MH3G 任务红色交纳箱实现计划 / Implementation Plan

1. 在目录测试中先定义新的红箱专用 pack 身份、状态、六个 RPX preimage、控制流 anchors，以及“不得写蓝箱资源/不得使用 code cave”的约束，并观察测试失败。
2. 将旧的双箱资源替换 pack 改名为红箱专用 pack，原地实现 `0x028C27C4..0x028C27D8` 六指令重定向。
3. 用中英双语更新 `rules.txt`、manifest 语义、研究记录和验证说明；同步大厅实测通过与 30 FPS 不稳定的状态。
4. 运行目录校验、固定 RPX preimage 校验、完整测试、Ruff、`git diff --check`、PPCAssembler smoke test 和可复现 ZIP。
5. 确认 Cemu 进程已退出后，只安装 Graphic Pack 到用户实际 Cemu 配置，保留蓝箱原版路径，不启动 Cemu；检查安装文件、哈希与启用状态。

1. Define the red-only pack identity, status, six RPX preimages, control-flow anchors, blue-resource exclusion, and no-code-cave rule in tests; observe the expected failure.
2. Rename the obsolete dual-resource pack and implement the six-instruction in-place redirect at `0x028C27C4..0x028C27D8`.
3. Update bilingual rules, manifest semantics, research, and verification notes; record the lobby gameplay pass and unstable 30 FPS feedback.
4. Run catalog validation, pinned-RPX verification, full tests, Ruff, `git diff --check`, PPCAssembler smoke tests, and reproducible ZIP checks.
5. After confirming Cemu is stopped, install only Graphic Pack files into the user's actual Cemu profile without launching Cemu; verify installed files, hashes, and enabled state.
