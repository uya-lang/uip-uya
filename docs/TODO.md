# uIP-uya TODO

本文档用于记录：**当前项目相对 C 版 uIP 仍需补齐的功能清单。**

原则保持不变：

> **只补齐 C 版 uIP 已有功能，不扩展，不重构成新的网络栈。**

---

## 1. 当前状态摘要

当前项目已经实现：

- 单主缓冲区 / 固定容量状态表
- ARP 最小闭环
- IPv4 / ICMP echo reply 最小闭环
- UDP 最小收发闭环
- TCP 最小建连 / 最小收发 / 最小关闭 / 基础 timer/retransmit
- 当前 host-side 回归测试：`50 / 50` 通过

当前项目尚未完成：

- C 版 `uip.c` 的完整 TCP 主状态机与全部边界分支
- 更完整的 ACK/SEQ / outstanding data 语义对齐
- `uiplib.c` 风格独立辅助功能
- 分片重组与更多可选配置项

---

## 2. 当前最高优先级 TODO

### TCP 语义补齐

- [ ] 继续补齐 `uip.c` 中尚未覆盖的 TCP 分支
- [ ] 进一步对齐 ACK/SEQ 与 outstanding data 语义
- [ ] 对照 C 版补齐更多异常输入包处理路径

### TCP retransmit / periodic

- [ ] 对齐 periodic / retransmit 与原版 outstanding data 模型
- [ ] 继续审查 `Established` / `SynSent` / `SynRcvd` 的 RTO 语义

### 文档与测试一致性

- [ ] 持续按 C 版语义维护 TCP 测试报文构造
- [ ] 避免测试口径再次偏离实现与原版路径

---

## 3. 中优先级 TODO

### TCP 语义补齐

- [ ] 继续补齐 `uip.c` 中尚未覆盖的 TCP 分支
- [ ] 继续补齐 ACK/SEQ 边界行为
- [ ] 继续补齐更多输入异常包处理路径

### 配置与可选能力

- [ ] 评估并补齐 C 版已有但当前未落地的配置项
- [ ] 仅在 C 版已有对应能力时，再补 `UIP_REASSEMBLY` / `UIP_URGDATA` / `UIP_BROADCAST` 等

### 辅助模块

- [ ] 评估是否需要按 C 版补 `uiplib.c` 风格辅助函数

---

## 4. 低优先级 TODO

### 文档同步

- [ ] 每次新增能力后同步 `docs/progress.md`
- [ ] 每次修复 TCP 状态机后同步 `docs/uip-porting-plan.md`
- [ ] 保持 `docs/README.md` 中索引完整

### 测试维护

- [ ] 按 C 版语义持续收敛测试断言
- [ ] 避免让测试口径偏离 C 版实现语义

---

## 5. 当前工作准则

后续开发统一遵循：

1. 先对照 C 版 uIP 现有路径
2. 再确认当前 uya 代码是否语义一致
3. 只做最小修复
4. 使用保守、稳定的 uya 语法
5. 不新增原版没有的能力
