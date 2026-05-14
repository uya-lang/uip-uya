# uIP-uya TODO

本文档用于记录：**根据当前代码与 `docs/progress.md`，项目相对 C 版 uIP 仍需补齐的功能清单。**

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
- 多条 TCP ACK/SEQ 边界已补齐：
  - `Established` 下超前 ACK 丢弃
  - `Established` 下旧 ACK + payload/FIN 丢弃
  - `Established` 下 payload/FIN 无 ACK 丢弃
  - `Established` 下无 ACK 标志异常包丢弃
  - `Established` 下 `SYN` 混入丢弃
  - `FinWait1` / `FinWait2` / `Closing` / `LastAck` 下超前 ACK 丢弃
  - `FinWait1` / `FinWait2` / `Closing` / `LastAck` 下错误 seq 丢弃
  - `FinWait1` / `FinWait2` 下 `FIN` 无 ACK 丢弃
  - `Closing` / `LastAck` 下 payload / `FIN` / `SYN` / 无 ACK 输入丢弃
  - `CloseWait` 的 ACK-only / payload+ACK / FIN+ACK / bad-seq ACK-only / over-ack ACK-only 现状已锁定：当前都会生成回复，本地状态不变
  - `TimeWait` 的 ACK-only / FIN+ACK / over-ack ACK-only 现状已锁定：当前会生成 ACK；`payload+ACK` 与 bad-seq payload 当前直接丢弃
  - `SynSent` 下错误序号的 `SYN|ACK` 丢弃
  - `SynSent` 下带 payload/FIN 的 `SYN|ACK` 丢弃
  - `SynSent` 下 `ACK-only` / `SYN-only` / `RST|SYN|ACK` 异常组合丢弃
  - `SynRcvd` 下错误序号 ACK 丢弃
  - `SynRcvd` 下错误 ACK 号丢弃
  - `SynRcvd` 下带 payload / `FIN` / 裸 `SYN` / `SYN|ACK` 混合输入丢弃
- TCP RST 现状已锁定：匹配到现有 conn 时，`Established` / `SynSent` / `SynRcvd` / `FinWait1` / `FinWait2` / `CloseWait` / `Closing` / `LastAck` 都会在主流程入口直接关闭连接
- `SynSent` periodic 语义已补齐：
  - 未到 RTO 不重传
  - 到 RTO 重发 `SYN`
  - 超过 `UIP_MAXSYNRTX` 后关闭
- 当前 host-side 回归测试：`154 / 154` 通过
- IPv4 入口边界已补齐一批测试：
  - 非 IPv4 version 丢弃
  - `IHL < 5` 丢弃
  - 实际帧短于声明 IP header 长度丢弃
  - 错误 IPv4 header checksum 丢弃
  - `total_len < ip_header_len` 丢弃
  - 实际帧短于 `total_len` 丢弃
  - 不支持的 IPv4 protocol 丢弃
- UDP 输入边界已补齐一批测试：
  - UDP header 截断丢弃
  - `udp_len < UIP_UDPH_LEN` 丢弃
  - `udp_len != IP payload len` 丢弃
  - UDP checksum 为 0 的包允许接收
- 当前 UDP 匹配语义已锁定：
  - 不匹配时丢弃
  - 当前实现不会回退到后续更精确的 UDP conn 绑定

当前项目仍未完成或未完整对齐：

- `uip.c` 其余尚未覆盖的主流程分支与边界条件
- 握手态与 outstanding data 的其余 ACK/SEQ 语义
- 更完整的 TCP 关闭状态机与 retransmit / periodic 原版细节
- 除 echo reply 之外的其他 ICMP 类型
- 更完整的 IPv4 / UDP 边界行为
- `uiplib.c` 风格独立辅助功能
- 分片重组与原版可选配置项
- 原版事件/宏语义等价接口层

---

## 2. 最高优先级 TODO

### 核心主流程

- [ ] 对照 C 版补齐 `uip.c` 中尚未覆盖的主流程分支
  - [x] `SynSent` 最小 active-open / `SYN|ACK` / `RST` / retransmit / timeout 路径
  - [x] `SynRcvd` 最小 passive-open / ACK 完成握手 / retransmit / timeout 路径
  - [x] `Established` 最小 ACK-only / payload / FIN / retransmit / timeout 路径
  - [x] `FinWait1` / `FinWait2` / `Closing` / `LastAck` / `TimeWait` 最小迁移路径
  - [x] `CloseWait` / `TimeWait` 输入现状与当前回包语义锁定
  - [ ] 继续扫描其余未显式覆盖的 TCP 标志组合与关闭态角落
- [x] 继续补齐更多输入报文合法性检查与异常分支
- [x] 为当前代码和测试都未体现的原版路径建立最小回归用例

### TCP 语义对齐

- [ ] 继续补齐完整 TCP 状态机细节
  - [x] outstanding data 的最小 ACK 确认语义
  - [x] TCP `RST` 对已匹配连接的当前关闭语义
  - [x] periodic / retransmit 的最小现状对齐
  - [ ] 继续评估 `PSH/URG/window/urgent pointer/reserved bits` 是否需要按 C 版补齐语义
- [x] 继续补齐握手态与 outstanding data 的 ACK/SEQ 边界处理
- [x] 补齐更多 TCP 异常输入包处理路径
- [ ] 继续审查并对齐关闭状态迁移细节

### TCP retransmit / periodic

- [x] 对齐 periodic / retransmit 的原版细节
- [x] 继续审查 `Established` / `SynSent` / `SynRcvd` / `LastAck` / `TimeWait` 的 RTO 与超时语义
- [x] 为尚未覆盖的 retransmit / timeout corner case 增加测试

---

## 3. 中优先级 TODO

### IPv4 / ICMP / UDP

- [ ] 评估并补齐除 echo reply 外的其他原版 ICMP 类型
  - [x] echo request reply 最小路径
  - [x] echo reply 当前静默忽略现状
  - [x] destination unreachable 当前静默忽略现状
  - [x] time exceeded 当前静默忽略现状
  - [x] 其他 non-echo ICMP 当前静默忽略现状
  - [x] truncated ICMP echo request 当前丢弃现状
  - [x] 坏 IPv4 header checksum 的 ICMP echo request 当前丢弃现状
- [x] 补齐更完整的 IPv4 边界分支
- [x] 补齐原版 UDP 其余边界行为
- [x] 为更多 UDP 输入组合增加测试覆盖

### 配置项与可选能力

- [ ] 评估并补齐 `UIP_REASSEMBLY`
  - [x] 当前未实现分片重组现状已锁定
  - [x] MF=1 且 offset=0 的 IPv4 首片会继续进入常规 TCP/UDP 路径
  - [x] MF=1 且 offset=0 的 fragmented ICMP echo request 首片当前可直接生成 echo reply
  - [x] offset!=0 的 IPv4 片段当前不会按普通 TCP/UDP conn/listener 匹配
  - [x] two-fragment UDP 当前现状已锁定：不会完成为普通 UDP conn 投递
  - [ ] 是否按 C 版补齐真正的分片重组仍未实现
- [ ] 评估并补齐 `UIP_REASS_MAXAGE`
  - [x] 当前缺失依赖于 reassembly 的超时老化路径已锁定
  - [ ] 是否按 C 版补齐重组老化仍未实现
- [ ] 评估并补齐 `UIP_UDP_CHECKSUMS`
  - [x] 当前固定行为已锁定：发送总是生成 checksum
  - [x] 当前固定行为已锁定：接收校验非零 checksum
  - [x] 当前固定行为已锁定：zero-checksum UDP 包允许接收
  - [x] wildcard binding 不改变 UDP checksum 校验行为
  - [ ] 是否按 C 版做成可配置项仍未实现
  - [ ] 如不配置化，需在文档中明确保持固定行为
- [ ] 评估并补齐 `UIP_URGDATA`
  - [x] 当前仅定义 `TCP_URG` 常量
  - [x] `URG` 标志无额外处理语义现状已锁定
  - [x] urgent pointer 无额外处理语义现状已锁定
  - [ ] 是否按 C 版补最小 urgent-data 路径仍未实现
  - [ ] 如不实现，需在文档中明确保持未实现
- [ ] 评估并补齐 `UIP_BROADCAST`
  - [x] 当前 UDP broadcast 目标地址不会投递到本机 UDP conn
  - [x] wildcard binding 也不会接收 limited broadcast
  - [x] network directed broadcast 当前也不会投递
  - [ ] 是否按 C 版补 broadcast 投递能力仍未实现
  - [ ] 如不实现，需在文档中明确保持未实现
- [x] IPv4 fragmentation / reassembly 当前现状已锁定
- [ ] 仅在 C 版已有且当前实现确有需要时，再补其他原版配置项

### 辅助模块与 helper

- [ ] 评估是否需要按 C 版补 `uiplib.c` 风格辅助函数
- [ ] 评估是否需要补更接近原版命名/语义的 add32/checksum helper
- [ ] 仅在 C 版已有且当前需要时，再补平台可覆写入口

---

## 4. 低优先级 TODO

### 事件/宏语义等价接口

如后续要继续贴近 C 版应用协作方式，需确认并补齐是否提供：

- [ ] `uip_connected()`
- [ ] `uip_newdata()`
- [ ] `uip_acked()`
- [ ] `uip_rexmit()`
- [ ] `uip_poll()`
- [ ] `uip_closed()`
- [ ] `uip_aborted()`
- [ ] `uip_timedout()`
- [ ] `uip_datalen()`
- [ ] `uip_mss()`

### 文档与测试同步

- [ ] 每次新增能力后同步 `docs/progress.md`
- [ ] 每次修复主流程或 TCP 状态机后同步 `docs/uip-porting-plan.md`
- [ ] 按 C 版语义持续收敛测试断言与报文构造
- [ ] 避免让测试口径偏离 C 版实现语义

---

## 5. 当前工作准则

后续开发统一遵循：

1. 先对照 C 版 uIP 现有路径
2. 再确认当前 uya 代码是否语义一致
3. 只做最小补齐或最小修复
4. 使用保守、稳定的 uya 语法
5. 不新增原版没有的能力
