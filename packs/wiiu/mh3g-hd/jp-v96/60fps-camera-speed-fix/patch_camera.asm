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
    ; 使用无 CA 副作用的逻辑右移；上述指令均不改 CR，保留 0x02286f74 的原 cmpwi 结果。
    ; Use a logical shift without a CA side effect. The instructions above preserve
    ; the CR result from the original cmpwi at 0x02286f74 for the beq at 0x02286f7c.
    srwi    r25, r25, 8
    b       0x02286f7c

; ===== 锁定/瞄准视角 (0x34b) 动态缩放 =====
_scale_aim_speed:
    li      r25, 0x34b
    
    ; 拿 r0 做临时计算: r25 = (0x34b * $cam_speed) / 256
    lis     r0, $cam_speed@h
    ori     r0, r0, $cam_speed@l
    mullw   r25, r25, r0
    srwi    r25, r25, 8
    
    ; 返回 0x02286f90，让未被替换的原生 bl FUN_02862b70 正常执行。
    ; Return to 0x02286f90 so the untouched native bl FUN_02862b70 executes normally.
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
