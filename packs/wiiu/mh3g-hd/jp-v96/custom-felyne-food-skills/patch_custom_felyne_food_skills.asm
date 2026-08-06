[MH3G HD JP v96]
moduleMatches = 0x348600a0

# 随机生成器返回后，直接覆盖原生最终写回循环会读取的三个半字临时槽。 / After the random generator returns, replace the three temporary halfword slots consumed by the native final writeback loop.
# r31 + 0x68/0x6A/0x6C 是该函数先清空、再由去重循环填充的最终技能槽；写入后跳过随机结果去重，保留后续餐食处理与菜单/任务状态镜像。 / r31 + 0x68/0x6A/0x6C are the final skill slots cleared and populated by this function; after writing them, skip random-result deduplication while preserving later meal processing and native menu/runtime mirroring.
0x021d865c = li r0, $skill1
0x021d8660 = sth r0, 0x0068(r31)
0x021d8664 = li r0, $skill2
0x021d8668 = sth r0, 0x006a(r31)
0x021d866c = li r0, $skill3
0x021d8670 = sth r0, 0x006c(r31)
0x021d8674 = b 0x021d86b4
