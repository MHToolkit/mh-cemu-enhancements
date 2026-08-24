[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 中文：V9 的 0x028764A4/0x02878D58 只位于 ammo index 10 分支；火炎弹等 index 7..9 会绕过它们。
# V10 在 A/B 两个蹲射发射函数入口统一检查 selector 4 的真实备弹，精确为零时在任何弹种分流之前结束本次开火。
# English: V9's 0x028764A4/0x02878D58 gates exist only in the ammo-index-10 branch; ammo indices 7..9 such as Flaming S bypass them.
# V10 gates both A/B siege-fire function entries so exact-zero selector-4 reserve returns before every ammo-type dispatch.
0x02875dec = b _hbg_all_ammo_entry_a_gate
0x02878738 = b _hbg_all_ammo_entry_b_gate

# 中文：公共弹仓回填。真实备弹为正时写入 min(弹仓容量, 真实备弹)；重弩活动态 +0x0002 == 4 且备弹归零时立即清空。
# English: Refill the common magazine with min(capacity, real reserve). When the live HBG selector +0x0002 is 4 and reserve reaches zero, clear it immediately.
0x0289248c = b _weapon_auto_refill_hook

# 中文：两条蹲射事务尾。它们会将公共弹仓减一；V9 只在实机已证明的重弩活动态 selector 4 中同步本次蹲射计数。
# English: Two siege-transaction tails decrement the common magazine. V9 synchronizes the active siege counters only for live-proven HBG selector 4.
0x02876248 = b _hbg_siege_transaction_a_hook
0x02878b5c = b _hbg_siege_transaction_b_hook

# 中文：蹲射活动循环的四个原生计数 writer。正库存时按 min(容量, 备弹) 回填，零库存写 0，负数哨兵值保留原版递减。
# English: Four native active-siege counter writers. Positive stock refills with min(capacity, reserve), zero writes 0, and negative sentinels retain vanilla decrement behavior.
0x02876550 = b _hbg_siege_a_byte_counter_hook
0x028765b8 = b _hbg_siege_a_half_counter_hook
0x02878e04 = b _hbg_siege_b_byte_counter_hook
0x02878e6c = b _hbg_siege_b_half_counter_hook

# 中文：最后的 A/B 开火门禁。备弹精确为 0 时强制两个蹲射计数为 0，交回紧随其后的原生结束分支，阻止无弹继续生成弹丸。
# English: Final A/B fire gates. Exact-zero reserve clears both siege counters and returns to the adjacent native completion branch, preventing ammo-less projectile generation.
0x028764a4 = b _hbg_siege_fire_gate_a_hook
0x02878d58 = b _hbg_siege_fire_gate_b_hook

.origin = codecave
_weapon_auto_refill_hook:
lbz r10, 0x0002(r7)
cmpwi r10, 9
beq _weapon_refill_gunlance
cmplwi r10, 3
blt _weapon_refill_original
cmplwi r10, 7
bgt _weapon_refill_original
lbz r11, 0x045b(r7)
cmpwi r11, 1
blt _weapon_refill_original
cmplwi r11, 31
bgt _weapon_refill_original
b _weapon_refill_clamp

_weapon_refill_gunlance:
lbz r11, 0x045b(r7)
cmpwi r11, 0
beq _weapon_refill_original

_weapon_refill_clamp:
lha r12, 0x0462(r7)
cmpwi r12, 0
beq _weapon_refill_zero_remaining
blt _weapon_refill_original
cmpw r11, r12
ble _weapon_refill_store
mr r11, r12

_weapon_refill_store:
stb r11, 0x045a(r7)
b _weapon_refill_original

_weapon_refill_zero_remaining:
# 中文：+0x0002 是运行态 selector，不是此前文档所称的固定“武器类型”。实机蹲射现场值为 4。
# English: +0x0002 is a runtime selector, not the fixed "weapon type" claimed by earlier notes. Live HBG siege evidence is 4.
cmpwi r10, 4
bne _weapon_refill_original
li r11, 0
stb r11, 0x045a(r7)
stb r11, 0x0008(r7)
sth r11, 0x062c(r7)
sth r11, 0x063c(r7)

_weapon_refill_original:
lfs f13, 0x0440(r7)
b 0x02892490

_hbg_siege_transaction_a_hook:
lbz r0, 0x0002(r12)
cmpwi r0, 4
bne _hbg_siege_a_vanilla
lha r0, 0x0462(r12)
cmpwi r0, 0
beq _hbg_siege_a_zero
blt _hbg_siege_a_vanilla
lbz r11, 0x045b(r12)
cmpw r11, r0
ble _hbg_siege_a_sync
mr r11, r0
b _hbg_siege_a_sync

_hbg_siege_a_zero:
li r11, 0

_hbg_siege_a_sync:
stb r11, 0x0008(r12)
sth r11, 0x062c(r12)
sth r11, 0x063c(r12)
b _hbg_siege_a_return

_hbg_siege_a_vanilla:
addi r11, r11, -1

_hbg_siege_a_return:
b 0x0287624c

_hbg_siege_transaction_b_hook:
lbz r0, 0x0002(r27)
cmpwi r0, 4
bne _hbg_siege_b_vanilla
lha r0, 0x0462(r27)
cmpwi r0, 0
beq _hbg_siege_b_zero
blt _hbg_siege_b_vanilla
lbz r11, 0x045b(r27)
cmpw r11, r0
ble _hbg_siege_b_sync
mr r11, r0
b _hbg_siege_b_sync

_hbg_siege_b_zero:
li r11, 0

_hbg_siege_b_sync:
stb r11, 0x0008(r27)
sth r11, 0x062c(r27)
sth r11, 0x063c(r27)
b _hbg_siege_b_return

_hbg_siege_b_vanilla:
addi r11, r11, -1

_hbg_siege_b_return:
b 0x02878b60

_hbg_siege_a_byte_counter_hook:
lbz r0, 0x0002(r12)
cmpwi r0, 4
bne _hbg_siege_a_byte_vanilla
lha r0, 0x0462(r12)
cmpwi r0, 0
beq _hbg_siege_a_byte_zero
blt _hbg_siege_a_byte_vanilla
lbz r7, 0x045b(r12)
cmpw r7, r0
ble _hbg_siege_a_byte_return
mr r7, r0
b _hbg_siege_a_byte_return

_hbg_siege_a_byte_zero:
li r7, 0
b _hbg_siege_a_byte_return

_hbg_siege_a_byte_vanilla:
addi r7, r7, -1

_hbg_siege_a_byte_return:
b 0x02876554

_hbg_siege_a_half_counter_hook:
lbz r0, 0x0002(r12)
cmpwi r0, 4
bne _hbg_siege_a_half_vanilla
lha r0, 0x0462(r12)
cmpwi r0, 0
beq _hbg_siege_a_half_zero
blt _hbg_siege_a_half_vanilla
lbz r7, 0x045b(r12)
cmpw r7, r0
ble _hbg_siege_a_half_return
mr r7, r0
b _hbg_siege_a_half_return

_hbg_siege_a_half_zero:
li r7, 0
b _hbg_siege_a_half_return

_hbg_siege_a_half_vanilla:
addi r7, r7, -1

_hbg_siege_a_half_return:
b 0x028765bc

_hbg_siege_b_byte_counter_hook:
lbz r0, 0x0002(r27)
cmpwi r0, 4
bne _hbg_siege_b_byte_vanilla
lha r0, 0x0462(r27)
cmpwi r0, 0
beq _hbg_siege_b_byte_zero
blt _hbg_siege_b_byte_vanilla
lbz r7, 0x045b(r27)
cmpw r7, r0
ble _hbg_siege_b_byte_return
mr r7, r0
b _hbg_siege_b_byte_return

_hbg_siege_b_byte_zero:
li r7, 0
b _hbg_siege_b_byte_return

_hbg_siege_b_byte_vanilla:
addi r7, r7, -1

_hbg_siege_b_byte_return:
b 0x02878e08

_hbg_siege_b_half_counter_hook:
lbz r0, 0x0002(r27)
cmpwi r0, 4
bne _hbg_siege_b_half_vanilla
lha r0, 0x0462(r27)
cmpwi r0, 0
beq _hbg_siege_b_half_zero
blt _hbg_siege_b_half_vanilla
lbz r9, 0x045b(r27)
cmpw r9, r0
ble _hbg_siege_b_half_return
mr r9, r0
b _hbg_siege_b_half_return

_hbg_siege_b_half_zero:
li r9, 0
b _hbg_siege_b_half_return

_hbg_siege_b_half_vanilla:
addi r9, r9, -1

_hbg_siege_b_half_return:
b 0x02878e70

_hbg_siege_fire_gate_a_hook:
lbz r10, 0x0002(r12)
cmpwi r10, 4
bne _hbg_siege_fire_gate_a_original
lha r10, 0x0462(r12)
cmpwi r10, 0
bne _hbg_siege_fire_gate_a_original
li r10, 0
stb r10, 0x045a(r12)
stb r10, 0x0008(r12)
sth r10, 0x062c(r12)
sth r10, 0x063c(r12)
b 0x028764a8

_hbg_siege_fire_gate_a_original:
lbz r10, 0x0008(r12)
b 0x028764a8

_hbg_siege_fire_gate_b_hook:
lbz r7, 0x0002(r27)
cmpwi r7, 4
bne _hbg_siege_fire_gate_b_original
lha r7, 0x0462(r27)
cmpwi r7, 0
bne _hbg_siege_fire_gate_b_original
li r7, 0
stb r7, 0x045a(r27)
stb r7, 0x0008(r27)
sth r7, 0x062c(r27)
sth r7, 0x063c(r27)
b 0x02878d5c

_hbg_siege_fire_gate_b_original:
lbz r7, 0x0008(r27)
b 0x02878d5c

# 中文：路径 A 的跨弹种入口门禁。r3 是外层玩家对象，+0x0E30 指向已验证的武器运行态对象。
# 精确零备弹时清理公共弹仓与蹲射快照后直接返回；正数和负数哨兵均完整执行原函数。
# English: All-ammo entry gate for path A. r3 is the outer player object and +0x0E30 points to the verified weapon runtime state.
# Exact-zero reserve clears common/siege snapshots and returns; positive stock and negative sentinels execute the original function.
_hbg_all_ammo_entry_a_gate:
lwz r12, 0x0e30(r3)
lbz r11, 0x0002(r12)
cmpwi r11, 4
bne _hbg_all_ammo_entry_a_original
lha r11, 0x0462(r12)
cmpwi r11, 0
bne _hbg_all_ammo_entry_a_original
li r11, 0
stb r11, 0x045a(r12)
stb r11, 0x0008(r12)
sth r11, 0x062c(r12)
sth r11, 0x063c(r12)
blr

_hbg_all_ammo_entry_a_original:
mflr r0
b 0x02875df0

# 中文：路径 B 的同构跨弹种入口门禁；必须和 A 保持完全一致的零库存语义。
# English: Symmetric all-ammo entry gate for path B with the same exact-zero contract as path A.
_hbg_all_ammo_entry_b_gate:
lwz r12, 0x0e30(r3)
lbz r11, 0x0002(r12)
cmpwi r11, 4
bne _hbg_all_ammo_entry_b_original
lha r11, 0x0462(r12)
cmpwi r11, 0
bne _hbg_all_ammo_entry_b_original
li r11, 0
stb r11, 0x045a(r12)
stb r11, 0x0008(r12)
sth r11, 0x062c(r12)
sth r11, 0x063c(r12)
blr

_hbg_all_ammo_entry_b_original:
mflr r0
b 0x0287873c

# 中文：未执行的尾部保护字。
# English: Unreachable tail guard.
.origin = 0x00000400
nop
