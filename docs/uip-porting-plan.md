# uIP-uya 迁移清单（按当前实现状态更新）

本文档用于把 **C 版 uIP → 当前 uya 实现** 的迁移状态整理成一份可执行清单。

目标保持不变：

> **只移植 C 版 uIP 已有功能，不扩展，不重构成另一套协议栈。**

---

## 1. 迁移原则

当前迁移继续遵循以下原则：

- 优先保持 **数据模型一致**
- 优先保持 **主流程一致**
- 优先保持 **驱动协作方式一致**
- 优先保持 **编译期配置模型一致**
- 不为了工程美观而改变资源模型
- 不增加超出 C 版 uIP 的能力

允许的变化只有：

1. **语言表达变化**
   - 宏改为常量、枚举、小函数
   - 裸指针改为 offset 或受控状态字段
2. **测试支撑变化**
   - 增加 host-side 辅助入口
   - 但不改变核心协议行为模型

---

## 2. 当前文件布局与映射

当前仓库中的实际实现布局为：

```text
src/uip/
  uip_arch/
    mod.uya
  uip_arp/
    mod.uya
  uip_conf/
    mod.uya
  uip_core/
    mod.uya
  uip_types/
    mod.uya
  uip_types_test.uya
```

对应关系：

| C 版 | 当前 uya 版 | 状态 |
|---|---|---|
| `uip.c` | `src/uip/uip_core/mod.uya` | 已部分迁移 |
| `uip.h` | `src/uip/uip_types/mod.uya` | 已部分迁移 |
| `uipopt.h` + `uip-conf.h` | `src/uip/uip_conf/mod.uya` | 已部分迁移 |
| `uip_arch.h` | `src/uip/uip_arch/mod.uya` | 已部分迁移 |
| `uip_arp.c` | `src/uip/uip_arp/mod.uya` | 已部分迁移 |
| 测试 | `src/uip/uip_types_test.uya` | 已建立 |

说明：这里的“已部分迁移”表示当前已有可运行子集，但尚未声明完成整个 C 版模块的全部能力。

---

## 3. `uip.h` → `uip_types/mod.uya`

### 当前已落地

已定义：

- `UipProcessFlag`
- `UipTcpState`
- TCP flags：`TCP_FIN` `TCP_SYN` `TCP_RST` `TCP_PSH` `TCP_ACK` `TCP_URG`
- ICMP 类型：`ICMP_ECHO` `ICMP_ECHO_REPLY`
- `UipIpAddr`
- `UipEthAddr`
- `UipEthHdr`
- `UipArpHdr`
- `UipIpHdr`
- `UipTcpHdr`
- `UipUdpHdr`
- `UipIcmpHdr`
- `UipTcpIpHdr`
- `UipUdpIpHdr`
- `UipIcmpIpHdr`
- `UipConn`
- `UipUdpConn`
- `UipArpEntry`
- `uip_ipaddr()`
- `uip_ethaddr()`
- `uip_ipaddr_eq()`
- TCP/UDP appdata offset 函数

### 当前未完成项

仍需按 C 版实际需要继续补齐：

- 原版 `uip.h` 中尚未迁移的常量与宏
- 如后续需要的更多状态字段或辅助宏等价物
- 仅在 C 版已有且当前代码确实需要时再补

### 当前结论

`uip_types/mod.uya` 已能支撑当前最小 ARP/IP/ICMP/UDP/TCP 闭环，但还不是完整 `uip.h` 等价物。

---

## 4. `uipopt.h` / `uip-conf.h` → `uip_conf/mod.uya`

### 当前已落地

已提供：

- `UIP_LLH_LEN`
- `UIP_IPH_LEN`
- `UIP_TCPH_LEN`
- `UIP_UDPH_LEN`
- `UIP_ARPH_LEN`
- `UIP_ETHH_LEN`
- `UIP_BUFSIZE`
- `UIP_BUFSIZE_WITH_PADDING`
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
- Ethernet type 常量
- 协议号常量
- 默认 host/router/netmask/MAC

### 当前未完成项

以下只在确有原版对应需求时补齐：

- `UIP_REASSEMBLY`
- `UIP_REASS_MAXAGE`
- `UIP_UDP_CHECKSUMS`
- `UIP_URGDATA`
- `UIP_BROADCAST`
- 其他当前代码尚未用到的原版配置项

### 当前结论

`uip_conf/mod.uya` 已足够支撑当前实现，但还不是完整 `uipopt.h` / `uip-conf.h` 镜像。

---

## 5. `uip_arch.h` → `uip_arch/mod.uya`

### 当前已落地

已实现：

- `read_be16()`
- `write_be16()`
- `read_u32_be()`
- `write_u32_be()`
- `checksum()`
- `upper_layer_checksum()`

### 当前未完成项

如 C 版原始移植仍需要，可继续补齐：

- 更接近原版命名的 add32/checksum helper
- 平台可覆写入口
- 但不扩展成通用 HAL

### 当前结论

`uip_arch/mod.uya` 已提供当前协议路径所需的基础能力。

---

## 6. `uip_arp.c` → `uip_arp/mod.uya`

### 当前已落地

已实现：

- `uip_arp_init()`
- `uip_arp_update()`
- `uip_arp_timer()`
- `uip_arp_ipin()`
- `uip_arp_arpin()`
- `uip_arp_out()`
- ARP 表查找、替换、老化
- cache miss 时把待发 IP 包改写为 ARP request
- 命中时补 Ethernet 头
- 针对本机的 ARP request 改写成 reply
- 针对本机的 ARP reply 更新 cache

### 当前未完成项

- 仅补齐 C 版 `uip_arp.c` 中当前尚未移植的剩余细节
- 不引入通用链路层抽象

### 当前结论

ARP 模块已经完成最小可验证闭环，是当前最完整的子模块之一。

---

## 7. `uip.c` → `uip_core/mod.uya`

这是当前迁移工作的核心。

## 7.1 当前已落地的全局状态

已迁移：

- `uip_hostaddr`
- `uip_draddr`
- `uip_netmask`
- `uip_ethaddr`
- `uip_buf`
- `uip_len`
- `uip_appdata` 的 offset 语义
- `uip_sappdata` 的 offset 语义
- `uip_slen`
- `uip_datalen`
- `uip_flags`
- 当前 TCP/UDP 连接索引
- `uip_conns[]`
- `uip_listenports[]`
- `uip_udp_conns[]`
- `ipid`
- `iss`
- `lastport`
- `uip_acc32`

### 当前说明

`uip_appdata` / `uip_sappdata` 当前以 offset 形式表达，而不是直接裸指针。
这属于语言表达变化，不改变其核心语义。

## 7.2 当前已落地的基础函数

已实现：

- `uip_init()`
- `uip_setipid()`
- host/router/netmask getter/setter
- `uip_setethaddr()` / `uip_getethaddr()`
- `uip_send()`
- `uip_close()`
- `uip_connect()`
- `uip_udp_new()`
- `uip_listen()`
- `uip_unlisten()`
- `uip_process(flag)`
- `uip_input()`
- `uip_periodic()`
- `uip_poll_conn()`
- `uip_udp_periodic()`

### 当前明确为测试辅助或过渡接口的项

这些接口存在于当前代码中，但不应作为长期架构承诺写入“最终设计”：

- `uip_send_at()`
- `uip_udp_bind()`
- 若干 internal send helper

## 7.3 当前已落地的协议路径

### IP / ICMP

已实现：

- 最小 IP 入站路径
- 发往本机的 ICMP echo request → echo reply

### UDP

已实现：

- UDP 入站匹配
- 不匹配时丢弃
- UDP checksum 校验
- UDP periodic 发送最小路径

### TCP

已实现的最小路径包括：

- listen table 匹配 SYN
- `SynRcvd` / `SynSent` / `Established` 最小握手路径
- `Established` 下 ACK-only / payload / ACK 生成
- `uip_send()` 的最小 payload 发送路径
- `uip_close()` 的 FIN/ACK 关闭路径
- `FinWait1` / `FinWait2` / `Closing` / `CloseWait` / `LastAck` / `TimeWait` 的部分迁移
- RST 关闭
- periodic 下最小重传与超时关闭

## 7.4 当前未完成项

后续仍需继续按 C 版补齐：

- `uip.c` 中尚未覆盖的分支与边界条件
- 完整 TCP 状态机细节
- 如原版已有且项目需要时，再补可选能力
- 不提前做新特性

---

## 8. 当前测试基线说明

`src/uip/uip_types_test.uya` 当前已覆盖：

- 配置常量
- IP/MAC 地址构造
- `uip_init()`
- listen/unlisten
- send intent 注册
- UDP send / input / checksum / drop
- ARP cache / request / reply / aging / out
- ICMP echo reply
- TCP SYN / SYN+ACK / ACK
- TCP payload / ACK / FIN / RST
- TCP periodic retransmit / timeout / timewait
- active open / passive open 的最小路径

这意味着当前项目已经具备：

> **围绕现有最小移植子集的回归测试能力。**

但测试存在不等于完整移植完成；测试只说明当前覆盖到的路径已有验证。

---

## 10. 当前与 C 版 uIP 的功能对照结论

基于当前代码与测试，uIP-uya 与 C 版 uIP 的关系可以概括为：

### 已落地的 C 版核心能力

- 单主缓冲区与全局状态模型
- 固定容量连接/监听/ARP 表
- ARP 最小闭环
- IPv4/ICMP echo reply 最小闭环
- UDP 最小收发闭环
- TCP 最小建连、最小收发、最小关闭、部分重传与定时器路径

### 仍待继续按 C 版补齐的能力

- `uip.c` 其余主流程分支
- 更完整的 TCP ACK/SEQ 语义
- 更完整的 TCP 关闭状态迁移
- periodic / retransmit 的原版细节
- `uiplib.c` 风格功能
- 分片重组和其他可选配置能力

### 当前迁移工作的重点

后续不再以“是否能工作”为主要标准，而应以：

1. 该路径在 C 版 uIP 中是否存在
2. 当前 uya 实现是否与该路径语义一致
3. 是否使用保守、稳定的 uya 语法完成该路径移植

---

## 11. 后续迁移要求

后续继续推进时，遵循以下顺序：

1. 先补齐 C 版已存在但当前未完成的主流程分支
2. 再补齐当前缺失的原版配置项或 helper
3. 仅在 C 版已有对应功能时才继续实现
4. 不新增超出原版的接口层、协议层或抽象层

最终目标始终是：

> **让 uya 版越来越接近 C 版 uIP，而不是逐步演变成另一套协议栈。**
