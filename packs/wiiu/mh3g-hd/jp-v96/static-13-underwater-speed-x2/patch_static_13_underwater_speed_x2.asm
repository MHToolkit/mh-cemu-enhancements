[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：3DS 静态 ARM #13“水下速度 2 倍”的 JP v96 PPC 转换；仅覆盖下列已钉住原指令的位置。
# English: JP-v96 PPC conversion of 3DS static ARM #13 "Underwater Speed ×2"; only the pinned preimage sites below are replaced.

# 中文：水下动作分派状态 2/14 的坐标积分原本使用 0.5；改为同一 RPX 中的 1.0。
# English: Redirect the coordinate integration for underwater action states 2/14 from 0.5 to the pinned 1.0 constant in the same RPX.
0x028c6bdc = lfs f12, -0x1e0c(r10)

# 中文：强制效果 ID 0xC7 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0xC7 to return true.
0x028c7368 = li r3, 1

# 中文：强制效果 ID 0xC7 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0xC7 to return true.
0x028c73b4 = li r3, 1

# 中文：强制效果 ID 0xC7 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0xC7 to return true.
0x028c7420 = li r3, 1

# 中文：强制效果 ID 0xC7 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0xC7 to return true.
0x028c7464 = li r3, 1

# 中文：强制效果 ID 0xC7 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0xC7 to return true.
0x028c74a8 = li r3, 1

# 中文：把 1.05 倍路径重定向到 JP v96 已有的 2.0 常量。
# English: Redirect the 1.05 path to an existing JP-v96 2.0 constant.
0x028c74d0 = lfs f10, -0x1e08(r12)

# 中文：强制效果 ID 0xC7 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0xC7 to return true.
0x028c7578 = li r3, 1

# 中文：水下动作分派状态 6/7 的第一条坐标积分路径：0.5 改为 1.0。
# English: Redirect the first coordinate-integration path for underwater action states 6/7 from 0.5 to 1.0.
0x028c7654 = lfs f12, -0x1e0c(r11)

# 中文：水下动作分派状态 6/7 的第二条坐标积分路径：0.5 改为 1.0。
# English: Redirect the second coordinate-integration path for underwater action states 6/7 from 0.5 to 1.0.
0x028c76dc = lfs f12, -0x1e0c(r11)

# 中文：水下动作分派状态 6/7 的第三条坐标积分路径：0.5 改为 1.0。
# English: Redirect the third coordinate-integration path for underwater action states 6/7 from 0.5 to 1.0.
0x028c7744 = lfs f12, -0x1e0c(r11)

# 中文：强制效果 ID 0xC7 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0xC7 to return true.
0x028c7ab0 = li r3, 1

# 中文：强制效果 ID 0xC7 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0xC7 to return true.
0x028c7af0 = li r3, 1

# 中文：水下动作分派状态 16/17 的坐标积分原本使用 0.5；改为 1.0。
# English: Redirect the coordinate integration for underwater action states 16/17 from 0.5 to 1.0.
0x028c8c34 = lfs f0, -0x1e0c(r9)

# 中文：强制效果 ID 0xC7 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0xC7 to return true.
0x028c966c = li r3, 1

# 中文：强制效果 ID 0xC7 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0xC7 to return true.
0x028c96c0 = li r3, 1

# 中文：强制效果 ID 0xC7 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0xC7 to return true.
0x028c96f8 = li r3, 1

# 中文：把 1.10 倍路径重定向到 JP v96 已有的 2.0 常量。
# English: Redirect the 1.10 path to an existing JP-v96 2.0 constant.
0x028c971c = lfs f0, -0x1e08(r10)

# 中文：水下动作分派状态 29 的第一条坐标积分路径：0.5 改为 1.0。
# English: Redirect the first coordinate-integration path for underwater action state 29 from 0.5 to 1.0.
0x028c9bdc = lfs f13, -0x1e0c(r9)

# 中文：水下动作分派状态 29 的第二条坐标积分路径：0.5 改为 1.0。
# English: Redirect the second coordinate-integration path for underwater action state 29 from 0.5 to 1.0.
0x028c9c9c = lfs f13, -0x1e0c(r9)
