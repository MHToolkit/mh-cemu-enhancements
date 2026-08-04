[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：3DS 静态 ARM #35“燃鳞”的 JP v96 PPC 转换；仅覆盖下列已钉住原指令的位置。
# English: JP-v96 PPC conversion of 3DS static ARM #35 "Flaming Aura"; only the pinned preimage sites below are replaced.

# 中文：强制效果 ID 0xCF 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0xCF to return true.
0x025a0ff8 = li r3, 1
