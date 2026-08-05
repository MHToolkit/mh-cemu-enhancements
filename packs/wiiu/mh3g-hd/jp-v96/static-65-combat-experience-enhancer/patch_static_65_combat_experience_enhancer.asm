[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：3DS 静态 ARM #65“战斗体验改善器”的 JP v96 PPC 转换；仅覆盖下列已钉住原指令的位置。
# English: JP-v96 PPC conversion of 3DS static ARM #65 "Combat Experience Enhancer"; only the pinned preimage sites below are replaced.

# 中文：把常规游戏模式技能槽查询的比较改为自比较；特殊模式分支保持原样。
# English: Replace the normal-game-mode skill-slot comparison with a self-comparison while leaving the special-mode branch unchanged.
0x02890b14 = cmplw r8, r8
