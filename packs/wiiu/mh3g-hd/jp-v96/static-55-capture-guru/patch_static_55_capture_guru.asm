[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：3DS 静态 ARM #55“观察眼”的 JP v96 PPC 转换；仅覆盖下列已钉住原指令的位置。
# English: JP-v96 PPC conversion of 3DS static ARM #55 "Capture Guru"; only the pinned preimage sites below are replaced.

# 中文：强制效果 ID 0xC0 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0xC0 to return true.
0x02615588 = li r3, 1

# 中文：强制效果 ID 0xC0 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0xC0 to return true.
0x026155ac = li r3, 1

# 中文：强制效果 ID 0xC0 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0xC0 to return true.
0x026155c8 = li r3, 1

# 中文：强制效果 ID 0xC0 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0xC0 to return true.
0x026155e4 = li r3, 1
