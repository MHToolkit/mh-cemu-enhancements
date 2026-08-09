[MH3G HD JP v96]
moduleMatches = 0x348600a0

.origin = codecave

; ===== 默认视角 (0x40b) 动态缩放 =====
_scale_default_speed:
    li      r25, 0x40b
    
    ; 拿 r0 做临时计算: r25 = (0x40b * $cam_speed) / 256
    lis     r0, $cam_speed@h
    ori     r0, r0, $cam_speed@l
    mullw   r25, r25, r0
    srawi   r25, r25, 8
    
    ; 还原原程序在 0x02286f78 处的 cmpwi 条件判断（关键！防止破坏 prevent branch）
    cmpwi   r0, 0x0
    b       0x02286f7c

; ===== 锁定/瞄准视角 (0x34b) 动态缩放 =====
_scale_aim_speed:
    li      r25, 0x34b
    
    ; 拿 r0 做临时计算: r25 = (0x34b * $cam_speed) / 256
    lis     r0, $cam_speed@h
    ori     r0, r0, $cam_speed@l
    mullw   r25, r25, r0
    srawi   r25, r25, 8
    
    ; 补回被替换的原指令: bl FUN_02862b70
    b       0x02286f90


; ===== 修改原程序 (保留原位置 Hook) =====

; 1. 替换 0x02286f78 处的 li r25, 0x40b
; 0x02286f78 = b _scale_default_speed
.origin = 0x02286f78
    b       _scale_default_speed

; 2. 替换 0x02286f8c 处的 li r25, 0x34b
; 0x02286f8c = b _scale_aim_speed
.origin = 0x02286f8c
    b       _scale_aim_speed