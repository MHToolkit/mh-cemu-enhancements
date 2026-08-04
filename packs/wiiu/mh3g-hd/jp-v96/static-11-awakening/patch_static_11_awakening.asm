[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：3DS 静态 ARM #11“里属性觉醒”的 JP v96 PPC 转换；仅覆盖下列已钉住原指令的位置。
# English: JP-v96 PPC conversion of 3DS static ARM #11 "Awakening"; only the pinned preimage sites below are replaced.

# 中文：强制效果 ID 0xCB 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0xCB to return true.
0x028600a0 = li r3, 1

# 中文：强制效果 ID 0xCB 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0xCB to return true.
0x028606e4 = li r3, 1

# 中文：强制效果 ID 0xCB 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0xCB to return true.
0x028a8c1c = li r3, 1
