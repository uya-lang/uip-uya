# uIP-uya 当前移植进度

本文档用于记录：**当前代码已经实现了哪些 C 版 uIP 功能，哪些还没有。**

本文档只依据当前仓库中的代码与测试，不提前声明未实现能力。

---

## 1. 统计口径

本进度文档的判断标准是：

- 代码中已有对应实现
- 或已有明确测试覆盖能证明该路径存在

如果某项只是文档里写过、但代码与测试里还看不到，就记为“未完成”或“未确认完成”。

---

## 2. 模块级进度

| 模块 | 当前状态 | 说明 |
|---|---|---|
| `uip.h` 对应类型层 | 部分完成 | 已有核心类型、头部、状态、常量 |
| `uipopt.h` / `uip-conf.h` 对应配置层 | 部分完成 | 已有当前实现所需主要配置 |
| `uip_arch.h` 对应辅助层 | 部分完成 | 已有字节序和 checksum 基础能力 |
| `uip_arp.c` 对应 ARP 模块 | 部分完成 | 已完成最小 ARP 闭环 |
| `uip.c` 对应核心模块 | 部分完成 | 已完成最小 IP/ICMP/UDP/TCP 子集 |
| `uiplib.c` 对应辅助模块 | 未完成 | 当前仓库中尚未独立落地 |

说明：这里的“部分完成”表示当前已有可运行子集，但不能等同于“完整 C 版模块已全部移植”。

---

## 3. 已实现功能

## 3.1 基础资源模型

已实现：

- 单一主缓冲区 `uip_buf`
- `uip_len`
- appdata / sappdata 的 offset 语义
- 固定容量 TCP 连接表
- 固定容量 UDP 连接表
- 固定容量监听端口表
- 固定容量 ARP 表
- 编译期配置常量驱动的资源规模

状态：**已实现最小模型**

---

## 3.2 类型与头部结构

已实现：

- IPv4 地址类型
- Ethernet 地址类型
- Ethernet 头
- ARP 头
- IPv4 头
- TCP 头
- UDP 头
- ICMP 头
- TCP/IP、UDP/IP、ICMP/IP 组合头
- TCP 状态枚举
- 处理 flag 枚举
- TCP flags 常量
- ICMP echo 类型常量

状态：**已实现当前代码所需子集**

---

## 3.3 配置层

已实现：

- 报头长度常量
- `UIP_BUFSIZE`
- `UIP_CONNS`
- `UIP_LISTENPORTS`
- `UIP_UDP_CONNS`
- `UIP_ARPTAB_SIZE`
- `UIP_TCP_MSS`
- `UIP_RECEIVE_WINDOW`
- `UIP_RTO`
- `UIP_MAXRTX`
- `UIP_MAXSYNRTX`
- `UIP_TIME_WAIT_TIMEOUT`
- `UIP_ARP_MAXAGE`
- `UIP_UDP`
- `UIP_ACTIVE_OPEN`
- `UIP_STATISTICS`
- `UIP_LOGGING`
- 默认 IP/router/netmask/MAC

状态：**已满足当前实现需要，但不是完整原版配置全集**

---

## 3.4 初始化与基础接口

已实现：

- `uip_init()`
- `uip_setipid()`
- hostaddr getter/setter
- draddr getter/setter
- netmask getter/setter
- ethaddr setter/getter
- `uip_send()`
- `uip_close()`
- `uip_connect()`
- `uip_udp_new()`
- `uip_listen()`
- `uip_unlisten()`
- `uip_input()`
- `uip_periodic()`
- `uip_poll_conn()`
- `uip_udp_periodic()`
- `uip_process(flag)`

状态：**已具备当前最小工作入口**

说明：

当前还存在测试辅助接口，如：

- `uip_send_at()`
- `uip_udp_bind()`

这些接口存在于当前代码中，但不代表最终对外 API 目标。

---

## 3.5 ARP

已实现：

- `uip_arp_init()`
- `uip_arp_update()`
- `uip_arp_timer()`
- `uip_arp_ipin()`
- `uip_arp_arpin()`
- `uip_arp_out()`
- ARP cache 查找 / 更新 / 替换
- ARP 表 aging
- 入站 IPv4 包学习源 MAC
- 出站 IP 包命中 cache 时补 Ethernet 头
- cache miss 时改写为 ARP request
- 针对本机的 ARP request → reply
- 针对本机的 ARP reply 更新 cache
- 非本机目标 IP 的 ARP request 忽略
- 非本机目标 IP 的 ARP reply 忽略

状态：**已实现最小闭环**

---

## 3.6 IPv4 / ICMP

已实现：

- 最小 IPv4 入站解析路径
- 发往本机的 ICMP echo request 处理
- 生成 ICMP echo reply
- 发往本机的非 echo ICMP 静默忽略
- 非 IPv4 version 丢弃
- `IHL < 5` 丢弃
- 实际帧短于声明 IPv4 header 长度丢弃
- 错误 IPv4 header checksum 丢弃
- `total_len < ip_header_len` 丢弃
- 实际帧短于 `total_len` 丢弃
- 不支持的 IPv4 protocol 丢弃

状态：**已实现最小闭环**

未确认完成：

- 其他 ICMP 类型
- 更完整的 IPv4 边界分支
- 分片重组

---

## 3.7 UDP

已实现：

- UDP 连接分配
- UDP 连接表满时返回失败
- 最小 UDP 入站匹配
- 不匹配时丢弃
- 设置 appdata offset
- UDP 周期发送路径
- 构造最小 IPv4/UDP 出站包
- UDP checksum 生成
- UDP checksum 校验
- 坏 checksum 丢弃
- UDP checksum 为 0 的包允许接收
- 当前 `uip_input()` 顶层只接收 IPv4 ethertype
- 以太帧长度短于 Ethernet 头时丢弃
- UDP header 截断丢弃
- `udp_len < UIP_UDPH_LEN` 丢弃
- `udp_len != IPv4 payload len` 丢弃
- 当前实现下，UDP 匹配不会回退到后续更精确绑定

状态：**已实现最小收发闭环**

未确认完成：

- 原版 UDP 其余边界行为
- 当前未被测试覆盖的更多输入组合

---

## 3.8 TCP

已实现：

### 监听与建连

- 监听端口表管理
- 被动打开：匹配 listening port 的 SYN
- 被动打开：SYN → SYN+ACK → ACK 最小握手
- 主动打开：`uip_connect()` 建立 `SynSent`
- 主动打开：SYN+ACK → `Established`

### Established 下最小收发

- ACK-only 输入处理
- payload 输入设置 datalen
- 收到 payload 后生成 ACK
- `uip_send()` 触发最小 ACK+payload 发送
- 合法 ACK-only / payload 会清理最小 retransmit 状态
- outstanding data 在合法 ACK 确认时会清空 `len`
- `URG|ACK` / `PSH|ACK` 无 payload 时当前不触发额外语义
- 小窗口 ACK-only 当前不会触发 ACK-only 清理语义

### CloseWait / TimeWait 当前现状

- `CloseWait` 收 ACK-only 时当前会生成 ACK，不改变本地状态
- `CloseWait` 收 payload+ACK 时当前会保留 payload 并直接形成回复，不改变本地状态
- `CloseWait` 收 FIN+ACK 时当前会生成 `FIN|ACK` 回复，不改变本地状态
- `CloseWait` 收 bad-seq ACK-only 时当前仍会生成 ACK
- `CloseWait` 收 over-ack ACK-only 时当前仍会生成 ACK
- `TimeWait` 收 ACK-only 时当前会生成 ACK，不改变本地状态
- `TimeWait` 收 FIN+ACK 时当前会生成 `FIN|ACK` 回复，不改变本地状态
- `TimeWait` 收 over-ack ACK-only 时当前会生成 ACK
- `TimeWait` 收 payload+ACK 时当前直接丢弃
- `TimeWait` 收 bad-seq payload 时当前直接丢弃

### 关闭状态机

- `uip_close()` 从 `Established` 进入 `FinWait1`
- `uip_close()` 从 `CloseWait` 进入 `LastAck`
- `FinWait1 -> FinWait2`
- `FinWait1 -> Closing`
- `FinWait2 -> TimeWait`
- `Closing -> TimeWait`
- `LastAck -> Closed`
- `Established + FIN -> CloseWait` 并返回 ACK

### Timer / periodic

- `TimeWait` 超时关闭
- `Established` 到 RTO 时增加重传计数
- `SynSent` 到 RTO 时重发 `SYN`
- `SynSent` 超过 `UIP_MAXSYNRTX` 后关闭
- `SynRcvd` 可重发 `SYN|ACK`
- `FinWait1` 可重发 `FIN|ACK`
- `LastAck` 可重发 `FIN|ACK`
- `CloseWait` 在 periodic 下保持静态
- `FinWait2` 在 periodic 下保持静态
- `Closing` 在 periodic 下保持静态
- 达到最大重传次数后关闭连接

状态：**已实现当前测试覆盖下的最小 TCP 闭环**

说明：

- 当前 TCP 测试基线已达到 `85 / 85` 通过
- 但这不等于“已完整复刻 C 版 uIP 全部 TCP 边界语义”
- 后续仍需继续对照 `uip.c` 补齐 outstanding data、异常包、更多定时器分支

### 关闭路径

- `uip_close()` 从 `Established` 进入 FIN 路径
- `uip_close()` 从 `CloseWait` 进入 `LastAck`
- `FinWait1 -> FinWait2`
- `FinWait1 -> Closing`
- `Closing -> TimeWait`
- `FinWait2 -> TimeWait`
- `LastAck -> Closed`
- `Established` 收 FIN → `CloseWait`

### 已补齐的输入边界

- `SynRcvd`：错误 `seq` / 错误 `ack` / payload / `FIN` / 裸 `SYN` / `SYN|ACK` 混合输入丢弃
- `SynSent`：错误 `seq` 的 `SYN|ACK`、带 payload/`FIN` 的 `SYN|ACK`、`ACK-only`、`SYN-only`、`RST|SYN|ACK` 异常组合丢弃
- `Established`：超前 `ACK`、旧 `ACK + payload/FIN`、payload/`FIN` 无 `ACK`、无 `ACK` 标志的异常包、`SYN` 混入丢弃
- `FinWait1` / `FinWait2`：超前 `ACK`、错误 `seq`、`FIN` 无 `ACK` 丢弃
- `Closing` / `LastAck`：超前 `ACK`、错误 `seq`、payload、`FIN`、`SYN`、无 `ACK` 输入丢弃

### RST 与定时器

- RST 关闭 `Established`
- RST 关闭 `SynSent`
- RST 关闭 `SynRcvd`
- RST 关闭 `FinWait1`
- RST 关闭 `FinWait2`
- RST 关闭 `CloseWait`
- RST 关闭 `Closing`
- RST 关闭 `LastAck`
- `TimeWait` 超时关闭
- RTO 后重传计数增加
- 超过最大重传后关闭
- `SynSent` 下最小 SYN 重传
- `SynRcvd` 下最小 SYN+ACK 重传
- `LastAck` 下最小 FIN+ACK 重传

### 配置项现状

- `UIP_UDP_CHECKSUMS`：当前未配置化；发送总是生成 UDP checksum，接收会校验非零 checksum，并允许 zero-checksum UDP 包；wildcard binding 不改变校验行为
- `UIP_URGDATA`：当前仅定义 `TCP_URG` 常量，URG 标志与 urgent pointer 都无额外处理语义，未实现 urgent-data 处理
- `UIP_BROADCAST`：当前未实现；UDP broadcast 目标地址不会投递到本机 UDP conn，包括 wildcard binding 与 network directed broadcast
- `UIP_REASSEMBLY` / `UIP_REASS_MAXAGE`：当前未实现完整分片重组；MF=1 且 offset=0 的 IPv4 首片仍可能进入常规 TCP/UDP/ICMP 路径，offset!=0 的 IPv4 片段当前不会按普通 TCP/UDP conn 或 listener 匹配；fragmented ICMP echo request 首片当前可直接生成 echo reply；two-fragment UDP 当前现状已锁定：不会完成为普通 UDP conn 投递

### ICMP 当前现状

- 发往本机的 ICMP echo request 会生成 echo reply
- 发往本机的 ICMP echo reply 当前静默忽略
- 发往本机的 ICMP destination unreachable 当前静默忽略
- 发往本机的 ICMP time exceeded 当前静默忽略
- 发往本机的其他 non-echo ICMP 当前静默忽略
- truncated ICMP echo request 当前丢弃
- 坏 IPv4 header checksum 的 ICMP echo request 当前丢弃

### 校验

- TCP checksum 校验
- 坏 checksum 丢弃

状态：**已实现最小 TCP 子集，并补齐了一批贴近 C 版的 ACK/SEQ、RST 与 retransmit 边界**

未确认完成：

- 完整原版 TCP 全部分支
- 更完整的 ACK/SEQ 边界处理
- 原版其余状态细节
- outstanding data 的更完整语义
- 其他当前未测试覆盖的 TCP corner case

---

## 5. 当前对比 C 版 uIP 的整体判断

如果直接对比 C 版 uIP 当前已经落地的能力，可以作如下判断：

### 已与 C 版设计明显对齐的部分

- 单主缓冲区 `uip_buf + uip_len`
- 固定容量 TCP/UDP/listen/ARP 表
- `uip_process(flag)` 为中心的核心处理模型
- ARP 独立于核心，在 `uip_arp` 中外接处理
- 最小 IPv4/ICMP echo reply 路径
- 最小 UDP 收发闭环
- TCP 的最小建连、最小收发、最小关闭、部分定时器/重传路径

### 当前仍明显落后于 C 版的部分

- `uip.c` 其余未覆盖主流程分支
- 更完整的 TCP ACK/SEQ 语义
- 更完整的 TCP 关闭状态机细节
- outstanding data 的更完整语义
- 原版更多边界条件与 corner case
- `uiplib.c` 风格独立辅助模块
- 分片重组与更多可选配置项

### 粗略完成度判断

这不是代码行数占比，而是“功能与行为对齐程度”的粗略工程判断：

- 资源模型 / 全局状态：≈ 80%+
- ARP：≈ 75~85%
- IPv4 / ICMP 最小路径：≈ 50~60%
- UDP：≈ 65~75%
- TCP：≈ 50~60%
- 整体相对 C 版 uIP：≈ 50% 左右

### 当前最准确的阶段描述

> 当前项目已经完成了 C 版 uIP 的核心资源模型移植，并实现了 ARP、IPv4/ICMP、UDP、TCP 的最小可运行子集；其中 ARP 与 UDP 已基本形成闭环，TCP 已具备基础状态机和部分定时/关闭逻辑，但尚未完整对齐 C 版 `uip.c` 的全部 TCP 行为与边界路径。

---

## 6. 未实现或未独立落地功能

根据当前仓库状态，以下内容仍应视为未完成、未完整对齐，或尚未独立落地：

### 6.1 `uip.c` / 核心主流程

- `uip.c` 中其余尚未覆盖的主流程分支
- 更多输入报文边界检查与异常分支
- 当前测试和代码都未体现的其他原版路径

### 6.2 TCP

- 完整原版 TCP 全部分支
- 更完整的 ACK/SEQ 边界处理
- 更完整的 outstanding data 语义
- 更完整的 TCP 关闭状态机细节
- retransmit / periodic 的原版细节对齐
- 其他当前未测试覆盖的 TCP corner case

### 6.3 IPv4 / ICMP / UDP

- 除 echo reply 之外的其他 ICMP 类型
- 更完整的 IPv4 边界分支
- 原版 UDP 其余边界行为
- 当前未被测试覆盖的更多 UDP 输入组合

### 6.4 配置项与可选能力

- `UIP_REASSEMBLY`
- `UIP_REASS_MAXAGE`
- `UIP_UDP_CHECKSUMS`
- `UIP_URGDATA`
- `UIP_BROADCAST`
- 原版其余尚未迁移的配置项

### 6.5 辅助模块与 helper

- `uiplib.c` 对应独立模块
- 更接近原版命名/语义的 add32/checksum helper
- 仅在 C 版已有且当前确实需要时再补的平台可覆写入口

### 6.6 事件/宏语义等价接口

当前代码已经有 `uip_flags`、`uip_datalen` 等内部状态，但尚未确认形成完整的原版事件/宏语义接口层，例如：

- `uip_connected()`
- `uip_newdata()`
- `uip_acked()`
- `uip_rexmit()`
- `uip_poll()`
- `uip_closed()`
- `uip_aborted()`
- `uip_timedout()`
- `uip_datalen()`
- `uip_mss()`

---

## 7. 当前结论

当前项目最准确的描述是：

> **已经实现了 C 版 uIP 的最小可运行子集，包含 ARP / IPv4 / ICMP / UDP / TCP 的一部分核心路径，并建立了回归测试基线。**

同时也必须明确：

> **当前还没有完成完整 C 版 uIP 的全部功能移植。后续工作应继续严格围绕补齐原版已有功能展开，不做扩展。**
