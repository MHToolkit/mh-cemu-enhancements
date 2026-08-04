[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：3DS 静态 ARM #6“会心不显示”的 JP v96 PPC 转换；仅覆盖下列已钉住原指令的位置。
# English: JP-v96 PPC conversion of 3DS static ARM #6 "Critical Display Hidden"; only the pinned preimage sites below are replaced.

# 中文：强制效果 ID 0x1B 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x1B to return true.
0x0286036c = li r3, 1

# 中文：将第一条会心加成从 30 改为 100。
# English: Change the first affinity addition from 30 to 100.
0x02860378 = addi r31, r31, 0x64

# 中文：强制效果 ID 0x1B 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x1B to return true.
0x02861840 = li r3, 1

# 中文：将第二条会心加成从 30 改为 100。
# English: Change the second affinity addition from 30 to 100.
0x02861850 = addi r31, r31, 0x64
