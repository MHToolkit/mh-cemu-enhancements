[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：3DS 静态 ARM #46“毒、麻痹、睡眠无效”的 JP v96 PPC 转换；仅覆盖下列已钉住原指令的位置。
# English: JP-v96 PPC conversion of 3DS static ARM #46 "Poison, Paralysis, and Sleep Immunity"; only the pinned preimage sites below are replaced.

# 中文：强制效果 ID 0x01 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x01 to return true.
0x02896240 = li r3, 1

# 中文：强制效果 ID 0x05 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x05 to return true.
0x028966cc = li r3, 1

# 中文：强制效果 ID 0x03 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x03 to return true.
0x028967d0 = li r3, 1

# 中文：强制效果 ID 0x01 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x01 to return true.
0x0289fc2c = li r3, 1

# 中文：强制效果 ID 0x05 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x05 to return true.
0x028a6938 = li r3, 1
