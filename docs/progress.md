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

状态：**已实现最小闭环**

---

## 3.6 IPv4 / ICMP

已实现：

- 最小 IPv4 入站解析路径
- 发往本机的 ICMP echo request 处理
- 生成 ICMP echo reply

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
- `SynRcvd` 可重发 `SYN|ACK`
- `LastAck` 可重发 `FIN|ACK`
- 达到最大重传次数后关闭连接

状态：**已实现当前测试覆盖下的最小 TCP 闭环**

说明：

- 当前 TCP 测试基线已达到 `50 / 50` 通过
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

### RST 与定时器

- RST 关闭 `Established`
- RST 关闭 `FinWait1`
- `TimeWait` 超时关闭
- RTO 后重传计数增加
- 超过最大重传后关闭
- `SynRcvd` 下最小 SYN+ACK 重传
- `LastAck` 下最小 FIN+ACK 重传

### 校验

- TCP checksum 校验
- 坏 checksum 丢弃

状态：**已实现最小 TCP 子集**

未确认完成：

- 完整原版 TCP 全部分支
- 更完整的 ACK/SEQ 边界处理
- 原版其余状态细节
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
- retransmit / periodic 的原版细节对齐
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

根据当前仓库状态，以下内容仍应视为未完成或未独立落地：

- `uiplib.c` 对应独立模块
- 分片重组相关能力
- 原版其余尚未迁移的配置项
- 当前测试和代码都未体现的其他原版路径

---

## 5. 当前结论

当前项目最准确的描述是：

> **已经实现了 C 版 uIP 的最小可运行子集，包含 ARP / IPv4 / ICMP / UDP / TCP 的一部分核心路径，并建立了回归测试基线。**

同时也必须明确：

> **当前还没有完成完整 C 版 uIP 的全部功能移植。后续工作应继续严格围绕补齐原版已有功能展开，不做扩展。**
