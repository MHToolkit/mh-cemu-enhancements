[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：外部 3DS Gateway“装备生产全解锁”的 JP v96 PPC 语义转换。
# English: JP-v96 PPC semantic conversion of the external 3DS Gateway "Unlock All Equipment Production" cheat.

# 中文：保留无效 ID 和上界检查，仅取消“合法 ID 的解锁位为 0”时的失败分支。
# English: Keep the invalid-ID and upper-bound guards; remove only the failure branch for a clear unlock bit on a valid ID.
0x02198fc8 = nop
