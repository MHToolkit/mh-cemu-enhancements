# Categorized release layout gate / 分类发行目录门禁（2026-08-12）

- The feature branch first merged current `origin/main`, so the distribution classification covers all 56 manifests: 53 available packs plus three retained `runtime-blocked` task-box evidence packs. / 功能分支先合入当前 `origin/main`，因此发行分类覆盖完整 56 个 manifest：53 个可用包，以及三个保留作证据的 `runtime-blocked` 任务箱包。
- Every manifest now declares exactly one primary category from the seven-entry bilingual catalog. Repository source paths remain the generic five-level layout; only the packaged catalog, manifest `pack_dir`, and pack files gain the ordered category directory. / 每个 manifest 现都从七项双语分类目录中声明且只声明一个主分类。仓库源码路径继续保留通用五级布局；只有打包后的 catalog、manifest `pack_dir` 与插件文件会增加带序号的分类目录。
- The release has one fixed `mh-cemu-enhancements/` root, generates `PACK-INDEX.md` and `catalog/distribution-index.json`, and excludes CI, tests, dist history, editor metadata, caches, and prohibited game assets. / 发行包使用固定 `mh-cemu-enhancements/` 根目录，自动生成 `PACK-INDEX.md` 与 `catalog/distribution-index.json`，并排除 CI、测试、历史 dist、编辑器元数据、缓存及受禁游戏资产。
- Repository validation accepts all 56 source manifests. The complete suite discovers 55 tests, with 54 passed and one optional historical-reference test skipped; it includes byte-identical double packaging, category membership/count assertions, extraction, a second full validation against the rewritten release tree, and an install smoke test from that categorized tree into the unchanged flat Cemu-owned destination. Ruff and `git diff --check` also pass. / 仓库校验接受全部 56 个源码 manifest。完整测试发现 55 项，其中 54 项通过、一个依赖历史 reference 的可选项跳过；覆盖双构建逐字节一致、分类成员与数量、解压、针对重写后发行树的第二次完整校验，以及从该分类树安装到保持扁平结构的 Cemu 自有目录的冒烟测试。Ruff 与 `git diff --check` 同样通过。
- Explicit verification against `/private/tmp/MH3G_Cafe.rpx` succeeds for the pinned SHA-256 and every declared code/data preimage and anchor. / 使用 `/private/tmp/MH3G_Cafe.rpx` 显式复核后，固定 SHA-256 以及全部代码/数据 preimage 与 anchor 均通过。
- Installation destinations deliberately remain keyed by stable `install_folder`, preserving existing Cemu saved-enable paths. Categorization changes archive storage only and does not weaken explicit selection, `runtime-blocked`, preimage, backup, or receipt gates. / 安装目标继续故意使用稳定的 `install_folder`，从而保留既有 Cemu 启用路径。分类只改变发行包存储，不削弱显式选择、`runtime-blocked`、前像、备份或 receipt 门禁。
- No tag or GitHub Release is created from this feature branch. The existing main-only merged-PR workflow will consume the new deterministic package function after a future PR is merged. / 当前功能分支不会创建 Tag 或 GitHub Release；待后续 PR 合入后，现有仅面向 main 已合并 PR 的工作流才会使用新的确定性打包函数。

# 0.1.24 main distribution and automatic release gate / 0.1.24 主分支发行与自动发布门禁（2026-08-09）

## Merge corrections / 合并后修正

1. The newly merged camera-speed and knockback manifests pointed at directories that did not exist, so the repository could not validate or package them. Their `pack_dir` values now match the actual `*-fix` directories and are covered by regression tests. / 新合并的视角速度与吹飞距离 manifest 指向不存在的目录，导致仓库无法校验和打包；现已对齐真实 `*-fix` 目录并加入回归测试。
2. The camera codecave overwrote `r0` with `$cam_speed` and then executed `cmpwi r0, 0`, incorrectly replacing the CR result produced by the native `cmpwi` at `0x02286F74`; the following native `beq` at `0x02286F7C` could therefore never take its zero path. The corrected cave performs only non-record arithmetic, uses `srwi` to avoid the `srawi` carry side effect, and preserves the native CR across the hook. Both surrounding words are now pinned as anchors. / 原视角 codecave 把 `$cam_speed` 写入 `r0` 后又执行 `cmpwi r0, 0`，错误覆盖了原生 `0x02286F74` 产生的 CR，导致紧随其后的 `0x02286F7C beq` 无法进入零分支。修正版只使用不记录 CR 的运算，并以 `srwi` 避免 `srawi` 的进位副作用，从而跨 Hook 保留原生 CR；两条上下文指令现均作为 anchor 固定。
3. The hammer hook changes only `0x0287F43C`; it branches over `0x0287F440` and replays that second instruction exactly once in the cave. The manifest now records `0x0287F440` as an anchor rather than falsely claiming it is overwritten, and the misleading `nop` comment is removed. / 锤子 Hook 实际只改 `0x0287F43C`，分支跳过 `0x0287F440` 后在 cave 中准确重放一次；manifest 现把后者记为 anchor，不再误称其被覆盖，并删除了误导性的 `nop` 注释。
4. The knockback fix targets immutable data word `0x1007E110`, not `.text`. Reference verification now checks every file-backed RPX virtual section and therefore validates both PPC code and static data preimages instead of rejecting or silently weakening data patches. / 吹飞距离修复目标是不可变数据字 `0x1007E110` 而非 `.text`；参考文件校验现覆盖 RPX 全部有文件内容的虚拟 section，可同时验证 PPC 代码与静态数据 preimage，不再拒绝或弱化数据补丁。

## Static acceptance / 静态验收

- `validate` accepts 53 manifests. The full suite passes 33 tests with one optional historical-path reference test skipped; an explicit `verify-reference` run against an RPX extracted read-only from the user's WUA accepts SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0` and every code/data preimage and anchor. / `validate` 接受 53 个 manifest；完整测试通过 33 项，仅跳过一个依赖已消失历史路径的可选 reference 测试。另以只读方式从用户 WUA 提取 RPX 后显式执行 `verify-reference`，其 SHA-256 为 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0`，全部代码/数据 preimage 与 anchor 通过。
- Cemu's real PPCAssembler accepts every instruction and relocation in the three new packs. Native replay words remain exact (`3B20040B`, `3B20034B`, `ED6C002A`, `3908FFFF`), and the data replacement encodes as `C1100000`. / Cemu 真实 PPCAssembler 接受三个新增包的全部指令与 relocation；原生重放字保持精确（`3B20040B`、`3B20034B`、`ED6C002A`、`3908FFFF`），数据替换编码为 `C1100000`。
- The three packs remain default-off `Runtime Experimental / Gameplay Pending`; these static gates do not claim gameplay success. No Cemu process was launched, and no Cemu binary, MLC, save, or game image was modified. / 三个包继续默认关闭并保持 `Runtime Experimental / Gameplay Pending`；静态门禁不等于实机通过。本轮未启动 Cemu，也未修改 Cemu 二进制、MLC、存档或游戏镜像。
- The main-only merged-PR workflow validates and builds twice before tagging, publishes only the asset-free ZIP and SHA-256 sidecar, and is idempotent for reruns of the same merged commit. / 仅面向 `main` 已合并 PR 的工作流会先校验并双构建，再打 Tag；Release 只发布无游戏资产 ZIP 与 SHA-256 sidecar，同一合并提交重跑保持幂等。

# External equipment-cheat static gates / 外部装备金手指静态门禁（2026-08-12，V7）

Production Unlock and No Materials remain **Runtime Verified**. No Money V6 is now formally rejected: a cold-start log proved the exact V6 pack active, live guest-memory reads found `li r3,0` at all eight declared sites, yet a sufficient-material upgrade still displayed `75000z` while production correctly displayed `0z`. This is a patch-logic failure, not an install/toggle/load failure.

生产全解锁与无需材料继续保持 **Runtime Verified**。无需金钱 V6 已被正式否定：冷启动日志证明精确 V6 已启用，运行中客机内存也在八个声明地址全部读到 `li r3,0`，但材料充足的强化仍显示 `75000z`，而生产已正确显示 `0z`。因此根因是补丁逻辑，不是安装、勾选或加载。

## No Money V7 runtime target evidence / 无需金钱 V7 运行时目标证据

1. A live guest-heap search located the displayed big-endian upgrade price. Switching the selected entry changed the same field from `75000` to `25000`.
2. A hardware read watchpoint on that field recovered guest renderer PC `0x026A74E4`; static continuation `0x026A74F4 = lwz r5,0x31C(r9)` reads selected object `+0x31C`.
3. The candidate record is at the same object `+0x27C`. The tested gunlance record has category `0x0B`, which `0x02159D14` maps to category branch 1.
4. The active smithy controller passes object `+0x27C` and `+0x31C` to `0x0221C730`. That builder clears ten price words, then repopulates them through exactly two category-local calls: `0x0221C850` followed by `0x0221C854: stw r3,0(r21)`, or `0x0221C96C` followed by `0x0221C970: stw r3,0(r21)`.
5. V7 replaces those two calls with `li r3,0`, keeps two gameplay-passed production sites plus two narrow legacy upgrade-record sites, and removes all four V5/V6 generic detail-render guesses. Shared equipment value `0x0221D224`, attack-sensitive category dispatch `0x0215A86C`, sale/refund callers, wallet comparison, and wallet adjustment remain native.

## Current verification gates / 当前验证门禁

- Repository validation and exact RPX preimage/anchor verification passed against `/private/tmp/MH3G_Cafe.rpx` (SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0`).
- The real Cemu PPC assembler accepted all six V7 `li r3,0` replacements as `0x38600000`, with zero relocations.
- `pytest tests/ -q` passed 49 executed tests with one optional historical-reference test skipped; `python3 -m unittest discover -s tests -v` passed all 50 discovered tests with that same one skip. Repository validation accepted 53 manifests, explicit pinned-RPX verification passed, and Ruff plus `git diff --check` passed.
- The standard Cemu profile was refreshed in place from its existing 48-pack receipt; the receipt ID set was preserved exactly, inspection reported No Money enabled, and the installed leaf was V7. The user subsequently cold-started that installation and confirmed the formerly failing upgrade route now works.

These gates establish exact binary targeting, parser/assembler validity, installation integrity, and the runtime-observed price-field data flow. On 2026-08-12 the user then cold-started the installed V7 pack and confirmed that the previously failing upgrade route now works. This adds gameplay proof for the core production/upgrade-without-money behavior, so V7 is promoted to **Runtime Verified / Gameplay Passed**. The verdict does not claim an independent retest or exhaustive coverage of every equipment category.

以上门禁证明目标二进制、解析器/汇编器、安装完整性，以及运行时真实价格字段的数据流。随后用户于 2026-08-12 冷启动已安装的 V7 并确认：此前失败的强化路径已正常生效。该结果补齐生产/强化无需金钱核心功能的实机证据，因此 V7 升级为 **Runtime Verified / Gameplay Passed**；不冒充独立测试者或全部装备类别穷举。
# #13 ordinary-swim final-integration candidate / #13 普通游泳最终积分候选（2026-08-07，0.1.22）

## Preliminary gameplay pass / 本机初步实机通过（2026-08-07）

After installing 0.1.22 and comparing it again in game, the user reported that underwater movement now shows an unmistakable speed increase and that actual coordinate travel—not only the animation—visibly doubles. This is the first positive runtime evidence for the corrected state-9 final integrations. The same isolated pack was sent to Pipi for an independent retest with fixed FPS, weapon, stick magnitude, camera, action, and route. That independent result and the requested three-run median transcript are still pending, so #13 remains default-off `Runtime Experimental` rather than being promoted prematurely.

安装 0.1.22 后，用户再次进行游戏内对照并反馈：水下移动速度已经明显加快，**实际坐标位移而非只有动画**也能清楚看出翻倍。这是状态 9 最终积分修正后的首份正向运行时证据。同一单项包已经通过 QQ 发给皮皮鸟，要求在固定 FPS、武器、摇杆幅度、镜头、动作与路线的条件下独立复测。皮皮鸟结果以及每组至少三次的中位数记录仍待回报，因此 #13 继续默认关闭并保持 `Runtime Experimental`，暂不提前升级状态。

## Superseding runtime verdict / 覆盖性实测结论

The 0.1.21 candidate did **not** pass gameplay acceptance. Cemu log evidence confirms that the isolated profile loaded JP-v96 module checksum `0x348600a0`, updated RPX hash `8cb62099`, and the exact installed #13 pack. The user still observed faster action presentation without a clear increase in actual ordinary-swim route displacement. This is therefore a patch-logic failure, not an installation/configuration failure.

0.1.21 候选**没有通过实机验收**。Cemu 日志已确认隔离配置载入 JP-v96 模块校验值 `0x348600a0`、更新后 RPX hash `8cb62099` 与当时精确安装的 #13 包；用户仍只观察到动作表现变快，普通游泳路线的实际位移没有明显提升。因此这是补丁逻辑问题，不是安装或配置问题。

Before the positive user retest above, 0.1.22 was a new **Runtime Experimental / Gameplay Pending** candidate. The static evidence below alone was not a claim that underwater travel was already 2x.

在上述用户正向复测之前，0.1.22 仍只是新的 **Runtime Experimental / Gameplay Pending** 候选；以下静态证据本身并不等于“实际水下位移已经达到 2 倍”。

## RCA and narrow correction / 根因与窄范围修正

1. The original 3DS #13 entry forces effect ID `0xC7` and raises action-rate scalars. Its first relevant ARM routine still multiplies the final coordinate delta by `0.5` at `0x008A3E90`; the cheat does not patch that instruction. The source cheat therefore does not prove physical travel ×2.
2. JP-v96 PPC player update dispatches underwater actions through `0x028CA170`. Ordinary swimming is handler state 9 at `0x028C78C4`, structurally matching the first 3DS routine.
3. State 9 loads shared `f31 = 0.5` at `0x028C7924`. Two mutually exclusive ordinary-swim branches then execute `fmuls f0,f9,f31` at `0x028C7E6C` and `0x028C7FE0` before writing the delta into `state + 0xE0/+0xE4/+0xE8`. 0.1.21 searched nearby `lfs 0.5` sites and therefore missed these two final multiplications because their constant was loaded far earlier at the shared function entry.
4. Changing the shared load at `0x028C7924` would also alter unrelated state-entry/event logic at `0x028C7A68`. 0.1.22 deliberately leaves it untouched and replaces only the two final `fmuls` instructions with `fmr f0,f9`, giving an effective integration factor of `1.0` in both ordinary-swim branches.
5. The same state-9 source-semantic path also loads action scalar `1.10` at `0x028C7B18`; 0.1.21 missed it. 0.1.22 redirects that one load to the pinned JP-v96 `2.0` constant. These three writes are a narrow Wii U physical-travel adaptation beyond the literal 3DS patch.

3DS 原 #13 会强制效果 `0xC7` 并提高动作标量，但其第一条相关 ARM 路径在 `0x008A3E90` 仍把最终坐标增量乘以 `0.5`，金手指没有修改这条指令，因此源金手指本身不能证明“实际位移 ×2”。JP-v96 普通游泳走水下分派器状态 9（`0x028C78C4`）：函数入口 `0x028C7924` 把共用 `0.5` 装入 `f31`，两条互斥分支随后在 `0x028C7E6C` 与 `0x028C7FE0` 执行 `速度 × f31` 再写回 `state + 0xE0/+0xE4/+0xE8`。0.1.21 因只扫描附近的 `lfs 0.5` 而漏掉这两条。0.1.22 不修改还被入口/事件逻辑共用的 `0x028C7924`，只把两条最终乘法改为直接使用速度 `f9`，并补上同状态 `0x028C7B18` 漏掉的 `1.10→2.0` 动作标量；三条写入均为面向 Wii U 实际位移目标的窄范围适配。

## Required gameplay acceptance / 必须完成的实机验收

- Disable #13 for the baseline, then enable only #13 for the candidate; keep #65 and every other static cheat disabled. / 基线关闭 #13，候选只启用 #13；#65 与其他静态金手指全部关闭。
- Keep FPS cap, weapon, full-stick magnitude, camera/direction, action, and start/end markers identical. / 固定 FPS、武器、满幅摇杆、镜头/方向、动作与起终点标记。
- Time the same ordinary-forward-swim route at least three times in each mode and compare median elapsed time; animation appearance is not an acceptance metric. / 两种模式对同一普通前游路线各计时至少三次并比较中位耗时；动画观感不作为通过标准。
- Separately check dash, turning, ascent/descent, evasion, wall collision, stopping, and input recovery for overshoot or lock-up. / 另查冲刺、转向、上浮/下潜、闪避、撞墙、停止与输入恢复是否过冲或锁死。

## 0.1.22 static and isolated-install gates / 0.1.22 静态与隔离安装门禁

1. `pytest tests/ -q` passes **29/29** executed tests; one optional immutable-reference test is skipped because its historical default fixture path is absent. The equivalent reference gate was run explicitly against the active extracted RPX.
2. `validate` accepts all **50** manifests. `verify-reference` accepts JP-v96 RPX SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0` and every declared preimage/anchor, including new preimages `C169E2D0`, `EC0907F2`, and `EC0907F2`.
3. Cemu's real `PPCAssembler` encodes the three new instructions with zero relocations: `028C7B18 -> C169E1F8`, `028C7E6C -> FC004890`, and `028C7FE0 -> FC004890`.
4. Ruff and `git diff --check` pass. The static mapping ledger now totals **179** PPC writes; #13 contains **23** fixed-address writes/preimages. A regression test also forbids modifying shared entry `0x028C7924`.
5. With no Cemu game process running, only #13 was refreshed in the isolated underwater-test profile. Inspection reports `installed=true` and preserves `enabled=true`. Repository and installed pack tree hashes both equal `0ec0a254455090f2a20e0fd40fafb934f4fb948c202c1cda607f581a9ac50ad0`.
6. The isolated `settings.xml` SHA-256 remains `229e0e06225027d07b2e1077596011445cb5f477d85835c7cfbb98631b8506ac`; no save/MLC path was modified, and no Cemu process was launched by this verification.
7. Two independent 0.1.22 package builds are byte-identical. Final archive SHA-256 is `379d386bd726f0fbab907ec25557da2b2c579fd571e13619bc07bedca065f3b3` and is recorded in `dist/mh-cemu-enhancements-0.1.22.zip.sha256`.

These gates prove exact-binary targeting, assembler validity, narrow state-9 coverage, deterministic packaging, and installation integrity only. The later user report above adds preliminary gameplay evidence that actual travel visibly doubles, but the pack remains **Runtime Experimental / Gameplay Pending** until the fixed-route three-run median and independent retest are recorded.

以上门禁只证明目标二进制、汇编器编码、状态 9 窄范围覆盖、确定性打包与安装完整性。后续用户反馈补充了“实际位移明显翻倍”的初步实机证据，但在固定路线三次中位数和独立复测记录齐全前，仍保持 **Runtime Experimental / Gameplay Pending**。

# Runtime feedback correction / 实测反馈修正（2026-08-06，0.1.19）

## Root-cause result / 根因结论

1. **猫饭技能自定义 / Custom Felyne Food Skills:** the source ID is correct (`0x41 = 招财猫的厄运 / Unlucky Cat`), but the old patch replaced only the downstream mirror loop at `0x021D8740..0x021D8764`. Native temporary slots `r31 + 0x68/0x6A/0x6C` could therefore remain random and diverge from later meal processing/display. The corrected patch writes those three source slots after generator call `0x021D8658`, branches to native post-processing at `0x021D86B4`, and preserves the complete native menu/runtime mirror loop. This is a static/data-flow correction and still requires a real meal retest.
2. **#13/#21/#34/#50/#60:** re-disassembly with the correct RPX `.text` base `0x02000020` confirmed their effect IDs, call sites, branch consumers, and declared preimages. No replacement-address defect was found. The saved test profile enabled almost every static pack, including #65; #65 forces the normal-mode generic skill-slot comparison true and prevents a clean on/off comparison for these skill-based effects. #59 independently masks #60's collection timing.

猫饭源编号无误（`0x41 = 招财猫的厄运`），问题在首版补丁的数据流：只改最终镜像循环，没有先统一原生临时源槽。修正版改为写入 `r31 + 0x68/0x6A/0x6C`，再交回原生后处理和最终镜像循环。五个静态包没有发现地址或 PPC 指令错误；之前几乎全开的配置中，#65 会让通用技能查询恒真，#59 还会单独掩盖 #60，因此该次结果不能判定这五项不生效。

## Isolated retest / 隔离复测

Every comparison starts with all other static packs disabled. In particular, disable #65 for #13/#21/#34/#50/#60 and also disable #59 for #60. Keep the FPS cap identical between baseline and enabled runs.

每项都必须在其余静态包关闭的条件下单独对照；#13/#21/#34/#50/#60 一律关闭 #65，#60 还要关闭 #59。基线与启用后的 FPS 设置必须完全相同。

| Target / 项目 | Required comparison / 必须对照方式 |
| --- | --- |
| #13 水下速度 2 倍 | Same underwater route, action, start/end points, and FPS; record elapsed time rather than visual impression. / 固定同一路线、动作、起终点和 FPS，记录耗时。 |
| #21 回避距离 UP | Same weapon, flat start point, camera/direction, and one full roll; compare endpoints. / 固定武器、平地起点、镜头方向，比较一次完整翻滚终点。 |
| #34 防御强化 | Shielded weapon against a normally unblockable attack; an ordinary block proves nothing. / 用带盾武器格挡原本不可防御的攻击；普通攻击无验证价值。 |
| #50 弩无摇晃 | Bowgun with built-in left/right deviation, same ammo and long-range target; this is deviation, not #49 recoil. / 使用自带左右偏移的弩、相同弹药和远距离目标；该项不是 #49 后坐力。 |
| #60 高速收集 | Only #60 enabled, #59/#65 disabled; time a complete cycle at the same gathering point. / 只启用 #60，关闭 #59/#65，对同一采集点完整循环计时。 |
| 猫饭 / Felyne | Enable the pack, select `41/00/00`, fully restart/reload the title, eat a new meal, then check the post-meal result for `招财猫的厄运`; pre-meal preview may remain random. / 启用包并选 `41/00/00`，完整重启或重载标题后重新吃饭，用餐后核对“招财猫的厄运”；餐前预览仍可能随机。 |

## 2026-08-06 static and install gates / 静态与安装门禁

1. `pytest tests/ -q` passes **29/29** tests; `validate` accepts all **50** manifests.
2. The pinned JP-v96 RPX SHA-256 is `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0`; every declared preimage and anchor passes against that immutable file.
3. Cemu's real `PPCAssembler` accepts the corrected seven-instruction Felyne block. With defaults `06/36/00`, the words are `38000006`, `B01F0068`, `38000036`, `B01F006A`, `38000000`, `B01F006C`, and `48000040`; the three selectors use `U32_MASKED_IMM` relocations and the final branch uses `BRANCH_S26`.
4. Ruff and `git diff --check` pass.
5. With no Cemu process running, the installer refreshes exactly **47 available packs** at `/Users/vincentadamnemessis/Library/Application Support/Cemu/graphicPacks/mh-cemu-enhancements`; all 47 installed tree hashes match their repository sources.
6. The receipt binds the install to the pinned RPX. `settings.xml` remains valid XML and its SHA-256 stays `90aff50f44231d06ae33f799e1136a0929da394958547259864216e5b1947a3f`; saved enable states are not edited.
7. Two independent `0.1.19` package builds are byte-identical; the final archive digest is stored in its adjacent `.sha256` sidecar.

These gates prove static correction and installation integrity only. The five subtle effects and the corrected Felyne meal path remain `Runtime Experimental / Gameplay Pending` until the isolated gameplay tests above pass.

以上门禁只证明静态修正与安装完整性。五个细微效果及修正版猫饭流程仍为 `Runtime Experimental / Gameplay Pending`，必须通过上面的隔离实测后才能升级结论。

# Runtime feedback correction / 实测反馈修正（2026-08-05，0.1.18 历史记录）

## Confirmed defects / 已确认缺陷

1. **#07 HP 无限 / Infinite HP**: the previous PPC conversion suppressed the normal write at `0x02865FF8` but left the lethal zero-clamp at `0x02866004`. This exactly explains surviving ordinary damage but dying to overkill damage. The corrected pack suppresses both writes. This PPC behavior is intentionally stronger than the source 3DS one-instruction patch; overkill survival on 3DS remains unverified.
2. **#65 战斗体验改善器 / Combat Experience Enhancer**: ARM `0x008A68BC` is in the normal-game-mode skill-slot branch. The previous PPC conversion incorrectly patched the special-mode branch at `0x02890AE4`; the corrected address is the normal branch at `0x02890B14`.
3. **猫饭技能自定义 / Custom Felyne Food Skills**: the latest `settings.xml` and `log.txt` showed that the pack was disabled and not loaded. Cemu resolves Graphic Pack variables while loading the title. After selecting and enabling presets, restart or reload the title, then eat a new meal; changing presets during a running title is not a valid test.

## Feedback classification / 反馈分类

| # | Feedback / 反馈 | Static conclusion / 静态结论 | Isolated retest / 隔离复测 |
| ---: | --- | --- | --- |
| 13 | 水下速度 2 倍不明显 | Eleven effect-ID checks plus the 1.05/1.10 to 2.0 scalar routes remain mapped correctly. / 11 条效果检查与两条倍率路径映射仍正确。 | Keep the same FPS/action and time the same underwater route. / 保持相同 FPS 与动作，对同一路线计时。 |
| 21 | 回距 UP 不明显 | All nine JP-v96 checks for effect ID `0xB8` are covered. / 已覆盖 `0xB8` 的 9 条检查。 | Use a fixed weapon, start point, and direction; compare one roll endpoint. / 固定武器、起点、方向并比较翻滚终点。 |
| 29 | 电阻弹可用 | User gameplay confirmed the intended availability behavior. / 用户已确认预期可用性行为。 | No corrective change. / 无需修正。 |
| 34 | 防强不明显 | Both JP-v96 checks for effect ID `0x25` are covered. / 已覆盖 `0x25` 的两条检查。 | Use a shielded weapon against a normally unblockable attack; ordinary blocks do not test Guard Up. / 用带盾武器格挡原本不可防御攻击。 |
| 35 | 燃鳞不明显 | Three ARM paths fold into one shared PPC check for effect ID `0xCF`; the mapping is structurally consistent. / 三条 ARM 路径在 PPC 合并为 `0xCF` 公共检查。 | Observe small-monster behavior in the same area, not a visible stat or large-monster aura. / 观察同区小怪行为。 |
| 44 | 对煌黑龙吹倒无效 | All three ordinary high-wind checks matching the 3DS source are covered. Special/scripted knockback may bypass them. / 与 3DS 源相同的三条普通大风压检查均已覆盖，特殊吹飞可能绕过。 | Test ordinary large wind pressure separately; Alatreon alone is not a mapping verdict. / 另测普通大风压。 |
| 48 | 未测 | No new failure evidence. / 暂无失败证据。 | Test invulnerability timing separately from #21 distance. / 与 #21 位移分开测试无敌帧。 |
| 50 | 弩无摇晃不明显 | Both JP-v96 checks for effect ID `0xAE` are covered. / 已覆盖 `0xAE` 的两条检查。 | Use a bowgun with built-in left/right deviation and compare long-range trajectories; this is not recoil. / 使用自带左右偏移的弩远距离对比弹道。 |
| 60 | 高速收集不明显 | All 18 JP-v96 checks for effect ID `0x8D` are covered. / 已覆盖 `0x8D` 的 18 条检查。 | Disable #59 and time a full cycle at the same gathering point. / 关闭 #59 后对同一采集点完整循环计时。 |

The reported run enabled almost every static pack at once, including both #59/#60 and #6/#72. Cemu logged every selected pack as applied and no patch parser errors, but that combined run cannot isolate subtle effects. After the corrections above, all packs remain `Runtime Experimental / Gameplay Pending` until a focused gameplay retest is recorded.

该次反馈运行几乎同时启用了全部静态包，包括 #59/#60 与 #6/#72。Cemu 日志显示所选包均已应用且没有补丁解析错误，但该组合无法隔离判断细微效果。本轮修正后，各项仍保持 `Runtime Experimental / Gameplay Pending`，等待逐项实测。

## 2026-08-05 static and install gates / 静态与安装门禁

1. `pytest tests/ -q` passed **27/27** tests; `validate` accepted all **50** manifests.
2. The pinned JP-v96 RPX passed every declared preimage and anchor check.
3. Cemu's real `PPCAssembler` encoded the corrected instructions as `02865FF8 -> 60000000`, `02866004 -> 60000000`, and `02890B14 -> 7C084040`.
4. Ruff and `git diff --check` passed.
5. With no Cemu process running, the installer refreshed the same **47-pack** receipt at `/Users/vincentadamnemessis/Library/Application Support/Cemu/graphicPacks/mh-cemu-enhancements`.
6. Installed #07, #65, and Felyne-food trees exactly match their source trees. `settings.xml` remained valid XML and its SHA-256 stayed `90aff50f44231d06ae33f799e1136a0929da394958547259864216e5b1947a3f`; saved enable states were not edited.
7. Two independent `0.1.18` builds were byte-identical; the final archive digest is stored in its adjacent `.sha256` sidecar.

# Local verification record / 本地验证记录（2026-08-04，0.1.17）

## Current static gates / 当前静态门槛

1. `python3 -m unittest discover -s tests -v` — **25/25 tests passed**. Coverage includes 50 catalog manifests, 43 independent static ARM conversions, the 44-FPS control conversion, the three-slot Felyne-food contract, fail-closed quest candidates, pinned RPX assertions, idempotent standard/isolated installation, inspection, and reproducible asset-free packaging.
2. `python3 scripts/mh-cemu-enhancements.py validate` — **50 manifests accepted**, of which 47 are available leaves and three quest-box research candidates are `runtime-blocked`.
3. `verify-reference` accepted RPX SHA-256 `7c78aad3810aa76a04e9d0fa2032718f71a21e3763f5394e627aa1cbdfe857a0` and every declared PPC preimage/anchor, including all ten Felyne-food overwrite words.
4. The Felyne-food rules contract contains exactly three categories and exactly 66 bilingual values (`0x00..0x41`) per category. Defaults inside the disabled pack are `0x06/0x36/0x00`.
5. Cemu 2.6's real `PPCAssembler` accepted all ten fixed-address instructions and produced the expected default words. The three `$skill*` expressions produced `U32_MASKED_IMM` relocations over the 16-bit immediate field, matching Graphic Pack variable resolution:

```text
021d8740 817f0140 lwz r11, 0x140(r31)
021d8744 38000006 li r0, $skill1
021d8748 b01b000a sth r0, 0x000a(r27)
021d874c b00b0e3e sth r0, 0x0e3e(r11)
021d8750 38000036 li r0, $skill2
021d8754 b01b000c sth r0, 0x000c(r27)
021d8758 b00b0e40 sth r0, 0x0e40(r11)
021d875c 38000000 li r0, $skill3
021d8760 b01b000e sth r0, 0x000e(r27)
021d8764 b00b0e42 sth r0, 0x0e42(r11)
```

6. `ruff check scripts tests` and `git diff --check` passed.
7. Two independent `0.1.17` package builds were byte-identical. The archive contains the complete catalog and no RPX, WUA, save, MLC, Cemu binary, game asset, `.idea`, or tool cache; the final SHA-256 is stored in the adjacent sidecar.

These gates establish static correctness and installation integrity only. They do not promote a pack to `Runtime Verified` without gameplay evidence.

以上门槛只证明静态正确性与安装完整性；没有游戏内证据时，不得把包升级为 `Runtime Verified`。

## Runtime evidence / 运行时证据

- **Lobby / 大厅：** The one-word `0x02799678 = li r5, 0` pack was tested by the user. The full menu appears, and equipment change, equipment sets, and talisman operations work. It remains opt-in `Runtime Verified`.
- **30 FPS：** User testing was unstable; hunting behavior was not completed. It remains default-off `Runtime Experimental`.
- **Quest boxes / 任务箱：** Red stayed crossed; blue and later combined candidates either opened no menu, caused crashes/stuck input, or damaged unrelated quest UI. All three candidates are retained as negative research evidence and are `runtime-blocked`.
- **43 static conversions / 43 项静态转换：** Static mapping and installation tooling pass; gameplay is still pending for each independent default-off pack.
- **Custom Felyne Food Skills / 猫饭技能自定义：** ARM/PPC semantic mapping, rules, preimages, real assembler, and installation pass. No real meal/quest-effect test exists yet, so it remains **Runtime Experimental / Gameplay Pending**.

The food pack changes the next native meal finalization only. Cemu resolves Graphic Pack parameters when loading the title, so after selecting presets the user must restart or reload the title and then eat again. Pre-meal preview may remain game-generated, and native incompatible combinations such as `0x41 + 0x1E` may apply only one effect.

猫饭包只改变下一次原生用餐结算。Cemu 在标题加载时解析 Graphic Pack 参数，因此修改预设后必须重启或重新载入游戏，再重新吃饭。餐前预览可能仍是原版随机结果，`0x41 + 0x1E` 等原生互斥组合也可能只生效其中一项。

## Installed isolated profile / 已安装隔离配置

After confirming zero Cemu processes, the installer wrote only its owned directory:

```text
/Volumes/GameHub/Development/Games/Nemessix/nemessix-multi-engine-apple-design-worktree/.build/nemessix-bundled-cemu-runtime-proof-20260721/home/Library/Application Support/Nemessix Dev/cemu/data/graphicPacks/mh-cemu-enhancements/
```

The receipt contains exactly:

```text
mh3g-hd-jp-v96-lobby-full-item-box
mh3g-hd-jp-v96-fps-lock-30
mh3g-hd-jp-v96-custom-felyne-food-skills
```

The installer intentionally did not edit `config/settings.xml`. Its existing saved states were preserved and the XML parses successfully:

| Pack | Installed | Saved enabled state |
| --- | --- | --- |
| Lobby Full Item Box | yes | enabled |
| Lock 30 FPS | yes | enabled |
| Custom Felyne Food Skills | yes | disabled |
| Lock 44 FPS | no | disabled |
| All three quest-box candidates | no | disabled |

Receipt tree hashes:

```text
Lobby       76225166f133acfa0ea11b8773a5f2d1fe2317c24529c01e54378fb221c33580
30 FPS      c9b1b6639576486560ecfc7c9ea94ad183ba75d4e12a5cf12b6af7444e18a42d
Felyne food 15bdce2c9c8f61907a381d7d5b166d8e5c87a725c15106143ceb9011bb304246
```

The installed Felyne-food tree equals the source tree. Per-file SHA-256 values match source and destination:

```text
manifest.json                         0e37d063d266882e3bbae5338a90cc50b8e90d366423f24fd6048fc3a3ed287f
rules.txt                             294ac52965496822a986242cc294755cf5a1459ffba25fb12a2585dc0108c76a
patch_custom_felyne_food_skills.asm   499ba021caf506aceacf71b0855f5f21bd5fcdf6b85eb9b2d4363239a4fa75ef
```

No Cemu process was launched, and no WUA, RPX, Cemu binary, MLC, or save file was modified.

## Distribution / 分发

`dist/mh-cemu-enhancements-0.1.17.zip` is the deterministic distribution archive; `dist/mh-cemu-enhancements-0.1.17.zip.sha256` is its adjacent digest. The Felyne-food pack requires explicit selection plus `--include-experimental`; it is not auto-installed merely because experimental packs are allowed.
