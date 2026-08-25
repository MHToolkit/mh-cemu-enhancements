[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：#28 斩斧能量槽最大。原生函数 0x0285DE70 以有符号增量更新
# 武器运行时对象 +0x062C 的 16 位能量值，并把结果限制在 0..100。
# 实机执行断点已分别捕获剑模式消耗 r4=-4 与斧模式回充 r4=+5，且两次均沿
# r3+0x0E30 到达同一个斩斧状态对象。
# English: #28 Switch Axe energy maximum. Native function 0x0285DE70 applies a
# signed delta to the 16-bit gauge at weapon-runtime object +0x062C and clamps
# the result to 0..100. Live execution traces captured sword drain r4=-4 and
# axe recharge r4=+5 through the same r3+0x0E30 Switch Axe state object.

# 中文：正增量路径。保留原生 extsh、sth 与 0..100 钳制控制流，只把将要写回的
# 计算结果改为 100。
# English: Positive-delta path. Preserve the native extsh, sth, and 0..100
# clamp control flow; replace only the computed value about to be written.
0x0285defc = li r10, 100

# 中文：零/负增量路径；剑模式耗能会经过这里。同样只把最终写回值钳制为 100。
# English: Zero/negative-delta path used by sword-mode drain. Likewise clamp
# only the final value written by the native transaction to 100.
0x0285df48 = li r10, 100
