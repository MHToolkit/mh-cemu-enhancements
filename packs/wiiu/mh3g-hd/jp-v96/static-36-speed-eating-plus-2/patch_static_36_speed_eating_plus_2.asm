[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：3DS 静态 ARM #36“速食者 +2”的 JP v96 PPC 转换；仅覆盖下列已钉住原指令的位置。
# English: JP-v96 PPC conversion of 3DS static ARM #36 "Speed Eating +2"; only the pinned preimage sites below are replaced.

# 中文：强制效果 ID 0xB2 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0xB2 to return true.
0x028bd23c = li r3, 1

# 中文：强制效果 ID 0xB2 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0xB2 to return true.
0x028bd274 = li r3, 1

# 中文：强制效果 ID 0xB2 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0xB2 to return true.
0x028bfacc = li r3, 1
