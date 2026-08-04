[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：3DS 静态 ARM #18“泥雪无效”的 JP v96 PPC 转换；仅覆盖下列已钉住原指令的位置。
# English: JP-v96 PPC conversion of 3DS static ARM #18 "Mud and Snow Immunity"; only the pinned preimage sites below are replaced.

# 中文：强制效果 ID 0x0A 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x0A to return true.
0x02897b68 = li r3, 1

# 中文：强制效果 ID 0x0A 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x0A to return true.
0x02897bcc = li r3, 1
