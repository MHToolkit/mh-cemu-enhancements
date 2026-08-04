[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：3DS 静态 ARM #63“气候温度适应”的 JP v96 PPC 转换；仅覆盖下列已钉住原指令的位置。
# English: JP-v96 PPC conversion of 3DS static ARM #63 "Climate and Temperature Adaptation"; only the pinned preimage sites below are replaced.

# 中文：强制效果 ID 0x7E 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x7E to return true.
0x0229ce84 = li r3, 1

# 中文：强制效果 ID 0x82 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x82 to return true.
0x0229ced0 = li r3, 1

# 中文：强制备用温度状态 ID 0x7E 查询返回真。
# English: Force the alternate temperature-status ID 0x7E query to return true.
0x02865264 = li r3, 1

# 中文：强制第一条备用温度状态 ID 0x82 查询返回真。
# English: Force the first alternate temperature-status ID 0x82 query to return true.
0x02866b70 = li r3, 1

# 中文：强制第二条备用温度状态 ID 0x82 查询返回真。
# English: Force the second alternate temperature-status ID 0x82 query to return true.
0x02866b90 = li r3, 1

# 中文：强制效果 ID 0x7E 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x7E to return true.
0x02893610 = li r3, 1

# 中文：强制效果 ID 0x7E 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x7E to return true.
0x0289f9f4 = li r3, 1

# 中文：强制效果 ID 0x7E 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x7E to return true.
0x0289fae0 = li r3, 1

# 中文：强制效果 ID 0x7E 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x7E to return true.
0x0289fccc = li r3, 1

# 中文：强制效果 ID 0x7E 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x7E to return true.
0x028b2ca8 = li r3, 1

# 中文：强制效果 ID 0x82 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x82 to return true.
0x028b2d10 = li r3, 1

# 中文：强制效果 ID 0x7E 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x7E to return true.
0x028b312c = li r3, 1

# 中文：强制效果 ID 0x82 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x82 to return true.
0x028b3184 = li r3, 1
