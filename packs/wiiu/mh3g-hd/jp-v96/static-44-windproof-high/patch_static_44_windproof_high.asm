[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：3DS 静态 ARM #44“风压（大）无效”的 JP v96 PPC 转换；仅覆盖下列已钉住原指令的位置。
# English: JP-v96 PPC conversion of 3DS static ARM #44 "Windproof (High)"; only the pinned preimage sites below are replaced.

# 中文：强制效果 ID 0x86 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x86 to return true.
0x02898590 = li r3, 1

# 中文：强制效果 ID 0x86 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x86 to return true.
0x028985c0 = li r3, 1

# 中文：强制效果 ID 0x86 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x86 to return true.
0x02898790 = li r3, 1
