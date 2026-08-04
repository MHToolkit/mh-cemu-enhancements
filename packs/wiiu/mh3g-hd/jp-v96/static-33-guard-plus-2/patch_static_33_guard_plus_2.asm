[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：3DS 静态 ARM #33“防御性能 +2”的 JP v96 PPC 转换；仅覆盖下列已钉住原指令的位置。
# English: JP-v96 PPC conversion of 3DS static ARM #33 "Guard +2"; only the pinned preimage sites below are replaced.

# 中文：强制效果 ID 0x22 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x22 to return true.
0x0289589c = li r3, 1

# 中文：强制效果 ID 0x21 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x21 to return true.
0x028958c4 = li r3, 1

# 中文：强制防御性能的备用状态查询返回真。
# English: Force the alternate Guard status query to return true.
0x02896a38 = li r3, 1
