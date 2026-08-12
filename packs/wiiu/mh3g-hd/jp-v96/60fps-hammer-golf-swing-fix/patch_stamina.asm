[MH3G HD JP v96]
moduleMatches = 0x348600a0

.origin = codecave

; ===== 锤子转圈 60 帧正本垒手感修复 / 60 FPS hammer golf-swing fix =====
_hammer_spin_cave:
    fadds   f0, f0, f0          ; f0 = f0 * 2 (单帧步进角度翻倍，精准适配 60 帧)
    fadds   f11, f12, f0        ; 补回原 0x0287f43c 处的加法指令 (f11 = 旧进度 + 新步进值)
    subi    r8, r8, 0x1         ; 补回原 0x0287f440 处的圈数扣减指令 (r8 = r8 - 1)
    b       0x0287f444          ; 跳回原程序下一个指令地址

; ===== 修改原程序入口 / Patch the native entry =====
; 0x0287f43c = b _hammer_spin_cave
; 分支会跳过 0x0287f440；codecave 已将该原指令准确执行一次。
; The branch skips 0x0287f440; the codecave replays that original instruction exactly once.
.origin = 0x0287f43c
    b       _hammer_spin_cave   ; 仅替换 0x0287f43c；only 0x0287f43c is overwritten
