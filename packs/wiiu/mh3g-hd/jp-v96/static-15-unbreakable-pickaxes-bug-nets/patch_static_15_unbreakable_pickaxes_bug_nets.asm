[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：3DS 静态 ARM #15“铁镐和虫网不会损坏”的 JP v96 PPC 转换；仅覆盖下列已钉住原指令的位置。
# English: JP-v96 PPC conversion of 3DS static ARM #15 "Unbreakable Pickaxes and Bug Nets"; only the pinned preimage sites below are replaced.

# 中文：把铁镐/虫网耐久余量固定为 100。
# English: Fix the pickaxe/bug-net durability remainder at 100.
0x0211ad38 = li r0, 0x64

# 中文：强制效果 ID 0x8F 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x8F to return true.
0x028b73b4 = li r3, 1

# 中文：强制效果 ID 0x8F 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x8F to return true.
0x028bbd10 = li r3, 1

# 中文：强制效果 ID 0x8F 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x8F to return true.
0x028c3a80 = li r3, 1
