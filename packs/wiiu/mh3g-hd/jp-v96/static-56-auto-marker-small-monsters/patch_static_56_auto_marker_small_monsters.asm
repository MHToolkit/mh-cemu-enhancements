[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：3DS 静态 ARM #56“自动标记并标记当前区小怪”的 JP v96 PPC 转换；仅覆盖下列已钉住原指令的位置。
# English: JP-v96 PPC conversion of 3DS static ARM #56 "Auto-Marker plus Current-Area Small Monsters"; only the pinned preimage sites below are replaced.

# 中文：强制当前区怪物类型查询通过。
# English: Force the current-area monster-type query to pass.
0x026151c8 = li r3, 1

# 中文：强制效果 ID 0x97 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x97 to return true.
0x026151e8 = li r3, 1

# 中文：强制效果 ID 0x97 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x97 to return true.
0x02615204 = li r3, 1

# 中文：强制当前区标记高度/可见性查询通过。
# English: Force the current-area marker height/visibility query to pass.
0x02615230 = li r3, 1

# 中文：强制效果 ID 0x97 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x97 to return true.
0x02892010 = li r3, 1

# 中文：强制效果 ID 0x97 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x97 to return true.
0x02892034 = li r3, 1

# 中文：强制效果 ID 0x97 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x97 to return true.
0x0289383c = li r3, 1

# 中文：强制效果 ID 0x97 的 PPC 直接检查返回真。
# English: Force the direct PPC check for effect ID 0x97 to return true.
0x02893884 = li r3, 1
