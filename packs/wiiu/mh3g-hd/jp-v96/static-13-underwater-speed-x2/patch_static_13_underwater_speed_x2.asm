[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：3DS 静态 ARM #13“水下速度 2 倍”的 JP v96 PPC 转换；仅覆盖下列已钉住原指令的位置。
# English: JP-v96 PPC conversion of 3DS static ARM #13 "Underwater Speed ×2"; only the pinned preimage sites below are replaced.

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

# 中文：实测证明只改动作倍率不会提升整体位移；把第一条水下坐标积分路径使用的 0.5 常量重定向到同一 JP v96 RPX 中的 1.0 常量。
# English: Gameplay showed that action-rate changes alone do not raise overall displacement; redirect the first underwater coordinate-integration path from the JP-v96 0.5 constant to its 1.0 constant.
0x028c7654 = lfs f12, -0x1e0c(r11)

# 中文：覆盖第二条水下坐标积分分支，同样把每帧位移倍率从 0.5 提升到 1.0。
# English: Cover the second underwater coordinate-integration branch and likewise raise its per-frame displacement scalar from 0.5 to 1.0.
0x028c76dc = lfs f12, -0x1e0c(r11)

# 中文：覆盖第三条水下坐标积分分支，避免输入/动作分支回落到原始 0.5 位移倍率。
# English: Cover the third underwater coordinate-integration branch so alternate input/action flow cannot fall back to the original 0.5 displacement scalar.
0x028c7744 = lfs f12, -0x1e0c(r11)

# 中文：强制效果 ID 0xC7 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0xC7 to return true.
0x028c7ab0 = li r3, 1

# 中文：强制效果 ID 0xC7 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0xC7 to return true.
0x028c7af0 = li r3, 1

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
