[MH3G HD JP v96]
moduleMatches = 0x348600a0  ; 匹配 MH3G HD 模组 ID

.origin = codecave

; ===== 锤子转圈 60 帧正本垒手感修复 Hook =====
_hammer_spin_cave:
    fadds   f0, f0, f0          ; f0 = f0 * 2 (单帧步进角度翻倍，精准适配 60 帧)
    fadds   f11, f12, f0        ; 补回原 0x0287f43c 处的加法指令 (f11 = 旧进度 + 新步进值)
    subi    r8, r8, 0x1         ; 补回原 0x0287f440 处的圈数扣减指令 (r8 = r8 - 1)
    b       0x0287f444          ; 跳回原程序下一个指令地址

; ===== 修改原程序入口 =====
; 0x0287f43c = b _hammer_spin_cave
; 0x0287f440 = nop  ; (被 hook 覆盖，原指令在 codecave 中还原)
.origin = 0x0287f43c
    b       _hammer_spin_cave   ; 替换 0x0287f43c 与 0x0287f440 处的指令