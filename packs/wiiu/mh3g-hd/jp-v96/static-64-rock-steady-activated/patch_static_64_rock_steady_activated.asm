[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：3DS 静态 ARM #64“金刚身发动”的 JP v96 PPC 转换；仅覆盖下列已钉住原指令的位置。
# English: JP-v96 PPC conversion of 3DS static ARM #64 "Rock Steady Activated"; only the pinned preimage sites below are replaced.

# 中文：把金刚身最终失败返回改为成功。
# English: Change the final Rock Steady failure return to success.
0x028968a4 = li r3, 1
