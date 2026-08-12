[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：V7 保留已验证的生产费用单点和两条旧强化记录路径，并在当前加工界面实际使用的强化候选生成器 0x0221C730 内，将防具类和武器类两个价格计算调用缩窄为 0。不再修改通用详情渲染器。
# English: V7 keeps the verified production-local sites and two legacy upgrade-record paths, then zeros the armor and weapon price-calculation calls inside the actual upgrade-candidate builder 0x0221C730 used by the active smithy screen. Generic detail renderers are no longer patched.

# 中文：生成“生产”候选时，原逻辑调用费用包装器并把结果保存到候选对象 +0x08；直接保存 0，使生产界面与实际扣款费用都为 0。
# English: While building production candidates, the original call calculates a price stored at candidate +0x08; return zero here so both displayed and charged production cost are zero.
0x02206ecc = li r3, 0

# 中文：可用性判定中的同一费用包装器调用也直接返回 0；随后保留原生“费用 <= 钱包”比较和分支，不再需要绕过不足金钱标志。
# English: Return zero at the matching availability-check cost call as well; the native cost<=wallet comparison and branch remain intact, so no insufficient-money bypass is needed.
0x0221b694 = li r3, 0

# 中文：旧的 8 字节强化候选记录会把费用保存到 +0x04，再用于钱包比较和确认扣款；继续保留该窄范围兼容。
# English: A legacy eight-byte upgrade-candidate layout stores cost at +0x04 for wallet comparison and confirmation charging; retain this narrow compatibility site.
0x021cdc7c = li r3, 0

# 中文：另一条旧强化记录路径经栈 +0x0C 把费用写到详细记录 +0x31C；继续保留该窄范围兼容。
# English: Another legacy upgrade-record path carries cost through stack +0x0C into detailed record +0x31C; retain this narrow compatibility site.
0x0220b584 = li r3, 0

# 中文：当前加工界面使用的候选生成器 0x0221C730 会先把 10 个价格字段清零。装备类别映射为 0 时，原逻辑在此调用 0x0221BE94，下一条指令把返回值写到候选价格数组；改为 0 后该字段、低余额判定和确认扣款共用同一零值。
# English: The active candidate builder 0x0221C730 first clears ten price fields. For category-map 0, this call to 0x0221BE94 produces the value immediately stored into the candidate price array; return zero so display, wallet gating, and confirmation charging share zero.
0x0221c850 = li r3, 0

# 中文：装备类别映射为 1 时（实测铳枪类别 0x0B 即走此分支），原逻辑在此调用 0x0221C4D4/0x0221B364，并在 0x0221C970 写入实测渲染器读取的同一 +0x31C 价格字段。
# English: For category-map 1 (the tested gunlance category 0x0B takes this branch), the original call reaches 0x0221C4D4/0x0221B364 and 0x0221C970 stores its result into the same +0x31C price field observed by the live renderer.
0x0221c96c = li r3, 0
