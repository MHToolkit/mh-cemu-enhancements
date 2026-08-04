[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 任务本地一次性激活：交互当帧初始化并激活完整仓库，避免任务 HUD 每帧重置状态。 / Task-local one-shot activation: initialize and activate the full item box on the interaction frame, avoiding per-frame resets from the quest HUD.
0x028c2770 = lis r3, 0x1031
0x028c2774 = lwz r3, 0x44a0(r3)
0x028c2778 = mr r4, r30
0x028c277c = li r5, 0
0x028c2780 = bl 0x021f0a8c
0x028c2784 = lis r3, 0x1031
0x028c2788 = lwz r3, 0x44a0(r3)
0x028c278c = bl 0x021f0d08
0x028c2790 = b 0x021d5ba8

# 消费完整仓库状态转换：酒场逐帧分发器会处理激活器留下的 0x20，任务场景不会，因此在交互返回前调用同一状态处理器一次。 / Consume the full-item-box state transition: the lobby's per-frame dispatcher handles the activator's 0x20 state, but quest scenes do not, so invoke the same state processor once before returning from the interaction.
0x021d5ba8 = lis r3, 0x1031
0x021d5bac = lwz r3, 0x44a0(r3)
0x021d5bb0 = bl 0x02201af8

# 补齐任务场景缺失的最终 UI 挂接：若原生处理器返回后仍停在 0x20，则调用酒场受菜单栈保护而跳过的原生挂接函数；原函数栈帧会在共享收尾路径恢复 LR。 / Complete the final UI attachment missing from quest scenes: if the native processor returns while still in state 0x20, invoke the native attachment routine skipped by the lobby menu-stack guard; the original function frame restores LR in the shared cleanup path.
0x021d5bb4 = lis r3, 0x1031
0x021d5bb8 = lwz r3, 0x44a0(r3)
0x021d5bbc = lbz r0, 0x6e10(r3)
0x021d5bc0 = cmpwi r0, 0x20
0x021d5bc4 = bne 0x021d5bcc
0x021d5bc8 = bl 0x02201a94
0x021d5bcc = b 0x028c27f8

# 红箱使用与蓝箱相同的可交互提示和共享交互选择器。 / Make the red box use the same usable prompt and shared interaction selector as the blue box.
0x028c5824 = li r4, 0
0x028c5838 = li r5, 0xe
0x028c5e80 = li r4, 0

# 在任务 UI 构建器中复用原生大厅背景与完整仓库对象工厂。 / Reuse the native lobby background and full-item-box factories inside the quest UI builder.
0x021b0e50 = mr r3, r27
0x021b0e54 = li r4, 14
0x021b0e58 = li r5, 1
0x021b0e5c = lwz r0, 0x44(r1)
0x021b0e60 = lmw r21, 0x14(r1)
0x021b0e64 = mtlr r0
0x021b0e68 = addi r1, r1, 0x40
0x021b0e6c = b 0x021bb628
0x021b0ed4 = mr r3, r27
0x021b0ed8 = li r4, 4
0x021b0edc = li r5, 0
0x021b0ee0 = lwz r0, 0x44(r1)
0x021b0ee4 = lmw r21, 0x14(r1)
0x021b0ee8 = mtlr r0
0x021b0eec = addi r1, r1, 0x40
0x021b0ef0 = b 0x021bb628

# 保留大厅 GUI 资源，使任务对象能从缓存解析同一资源；随后尾调用原基类析构。 / Retain the hub GUI resources so the quest objects can resolve the same cached resources, then tail-call the original base destructor.
0x0268ab20 = bl 0x021d5bd8
0x026fd1b0 = bl 0x021d5bd8
0x021d5bd8 = li r0, 0
0x021d5bdc = stw r0, 0xf0(r3)
0x021d5be0 = b 0x0228c9ac
