[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：3DS 静态 ARM #59“剥取、采集动作与获取加快”的 JP v96 PPC 转换；仅覆盖下列已钉住原指令的位置。
# English: JP-v96 PPC conversion of 3DS static ARM #59 "Faster Carving, Gathering, and Acquisition"; only the pinned preimage sites below are replaced.

# 中文：把共享 1.1 获取倍率重定向到已有 1.5 常量。
# English: Redirect the shared 1.1 acquisition multiplier to an existing 1.5 constant.
0x028bc168 = lfs f31, -0x1d10(r12)

# 中文：把共享 1.3 动作倍率重定向到已有 2.0 常量。
# English: Redirect the shared 1.3 action multiplier to an existing 2.0 constant.
0x028bc174 = lfs f30, -0x1e08(r10)
