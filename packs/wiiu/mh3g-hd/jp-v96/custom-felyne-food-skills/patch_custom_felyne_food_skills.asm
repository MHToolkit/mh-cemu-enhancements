[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 在原生用餐结算尾段一次性写入三个自定义技能，并同步菜单状态和任务运行状态。 / Write all three selected skills once in the native meal finalizer and mirror them to menu and quest runtime state.
# r27 已由原函数构造成 r30 + 0x83F4；+0x0A/+0x0C/+0x0E 对应菜单侧三个半字槽。 / The original function has already formed r27 = r30 + 0x83F4; +0x0A/+0x0C/+0x0E are the three menu-side halfword slots.
0x021d8740 = lwz r11, 0x140(r31)
0x021d8744 = li r0, $skill1
0x021d8748 = sth r0, 0x000a(r27)
0x021d874c = sth r0, 0x0e3e(r11)
0x021d8750 = li r0, $skill2
0x021d8754 = sth r0, 0x000c(r27)
0x021d8758 = sth r0, 0x0e40(r11)
0x021d875c = li r0, $skill3
0x021d8760 = sth r0, 0x000e(r27)
0x021d8764 = sth r0, 0x0e42(r11)
