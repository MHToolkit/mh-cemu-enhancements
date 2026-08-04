[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：3DS 静态 ARM #49“弩后坐力最小”的 JP v96 PPC 转换；仅覆盖下列已钉住原指令的位置。
# English: JP-v96 PPC conversion of 3DS static ARM #49 "Minimum Bowgun Recoil"; only the pinned preimage sites below are replaced.

# 中文：强制效果 ID 0x2F 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x2F to return true.
0x0289cab0 = li r3, 1

# 中文：强制效果 ID 0x2F 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x2F to return true.
0x028a7b78 = li r3, 1
