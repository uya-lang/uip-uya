# uIP-uya 设计说明（按当前代码与 C 版 uIP 对齐）

本文档用于说明：**当前 uya 实现与 C 版 uIP 之间的结构映射，以及已经落地的功能边界。**

本文档只描述两件事：

1. 当前代码实际上是如何组织的
2. 后续如何继续按 **C 版 uIP 既有能力** 补齐移植

不讨论协议能力扩展，也不引入超出原版的架构目标。

---

## 1. 设计基准

uya 版重写仍以 C 版 uIP 的真实设计为基准，保留这些核心特征：

- 单一主报文缓冲区 `uip_buf`
- 以 `uip_process(flag)` 为中心的单核处理流程
- TCP / UDP / IP / ICMP 在核心实现中紧耦合处理
- 驱动与协议栈通过全局状态协作
- ARP 独立于核心处理流程，在 `uip_arp` 中实现
- 固定容量连接表、监听表、ARP 表
- 编译期配置决定资源规模与可选功能

这些目标与当前代码保持一致。

---

## 2. 当前代码模块映射

当前实际目录结构为：

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

与 C 版模块的对应关系如下：

| C 版 | 当前 uya 版 |
|---|---|
| `uip.c` | `src/uip/uip_core/mod.uya` |
| `uip.h` | `src/uip/uip_types/mod.uya` |
| `uipopt.h` + `uip-conf.h` | `src/uip/uip_conf/mod.uya` |
| `uip_arch.h` | `src/uip/uip_arch/mod.uya` |
| `uip_arp.c` | `src/uip/uip_arp/mod.uya` |
| 回归测试 | `src/uip/uip_types_test.uya` |

说明：

- 当前实现已经采用目录模块形式。
- 这属于代码组织方式变化，不表示协议架构发生变化。
- 协议核心仍然围绕 `uip_core/mod.uya` 与 `uip_process(flag)` 展开。

---

## 3. 当前已经落地的核心资源模型

### 3.1 单主缓冲区模型

在 `src/uip/uip_core/mod.uya` 中，`UipState` 已承载：

- `uip_buf`
- `uip_len`
- `uip_appdata_offset`
- `uip_sappdata_offset`
- `uip_slen`
- `uip_datalen`
- `uip_send_offset`
- `uip_send_len`
- `uip_flags`
- 当前 TCP/UDP 连接索引

这对应 C 版中围绕 `uip_buf`、`uip_len`、`uip_appdata`、`uip_sappdata` 的全局工作模型。

### 3.2 固定容量状态表

当前已落地：

- `uip_conns[UIP_CONNS]`
- `uip_udp_conns[UIP_UDP_CONNS]`
- `uip_listenports[UIP_LISTENPORTS]`
- `arp_table[UIP_ARPTAB_SIZE]`

这些容量全部由 `uip_conf` 中的编译期常量决定。

### 3.3 编译期配置

`src/uip/uip_conf/mod.uya` 当前已定义：

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
- 协议号、以太网类型、默认地址

这些配置已经足以支撑当前最小移植范围。

---

## 4. 当前模块职责

## 4.1 `src/uip/uip_types/mod.uya`

职责：

- 提供 `UipProcessFlag`
- 提供 `UipTcpState`
- 提供 TCP flags 与 ICMP 类型常量
- 定义：
  - `UipIpAddr`
  - `UipEthAddr`
  - `UipEthHdr`
  - `UipArpHdr`
  - `UipIpHdr`
  - `UipTcpHdr`
  - `UipUdpHdr`
  - `UipIcmpHdr`
  - `UipConn`
  - `UipUdpConn`
  - `UipArpEntry`
- 提供地址构造与比较函数
- 提供 TCP/UDP appdata offset 计算函数

这部分相当于当前已移植的 `uip.h` 子集。

## 4.2 `src/uip/uip_arch/mod.uya`

职责：

- `read_be16()` / `write_be16()`
- `read_u32_be()` / `write_u32_be()`
- 通用 `checksum()`
- 上层伪首部校验和 `upper_layer_checksum()`

这部分承担当前的字节序与校验和基础能力。

## 4.3 `src/uip/uip_arp/mod.uya`

职责：

- ARP 表管理
- `uip_arp_init()`
- `uip_arp_update()`
- `uip_arp_timer()`
- `uip_arp_ipin()`
- `uip_arp_arpin()`
- `uip_arp_out()`

当前它已经实现了最小 ARP 外接闭环：

- IP 入站时学习对端 MAC
- 出站 IP 包按 ARP cache 封装 Ethernet 头
- cache miss 时改写为 ARP request
- 处理针对本机的 ARP request/reply

## 4.4 `src/uip/uip_core/mod.uya`

职责：

- `UipState` 全局状态
- `uip_init()`
- 地址 getter/setter
- `uip_send()`
- `uip_close()`
- `uip_connect()`
- `uip_udp_new()`
- `uip_listen()` / `uip_unlisten()`
- `uip_process(flag)`
- `uip_input()` / `uip_periodic()` / `uip_poll_conn()` / `uip_udp_periodic()`

此外，当前实现中还存在一些明确标注为 transitional 的测试辅助接口或内部 helper，例如：

- `uip_send_at()`
- `uip_udp_bind()`
- 若干直接构造最小 TCP/UDP 出站包的内部 helper

这些接口的定位是：

- 便于当前 host-side 测试
- 不代表未来对外 API 目标
- 后续应优先向 C 版 uIP 的既有调用方式收敛

---

## 5. 当前已实现的协议路径

以下内容已经在代码与测试中落地。

### 5.1 ARP

已实现：

- ARP 表初始化
- ARP cache 更新
- ARP aging
- 针对本机的 ARP request → reply
- 针对本机的 ARP reply 学习
- `uip_arp_out()` 的 cache hit / miss 路径

### 5.2 IPv4 / ICMP

已实现：

- 最小 IPv4 入站解析路径
- 目的地址为本机时的 ICMP echo request 处理
- 生成 ICMP echo reply

### 5.3 UDP

已实现：

- UDP 连接分配
- 最小 UDP 连接匹配
- 不匹配时丢弃
- UDP checksum 校验
- 周期发送路径下构造最小 IPv4/UDP 包

### 5.4 TCP

已实现的最小路径包括：

- 监听端口匹配
- 被动打开最小握手路径
- 主动打开最小握手路径
- `Established` 状态下 ACK-only 处理
- `Established` 状态下 payload 接收与 ACK 生成
- `uip_send()` 驱动的最小 TCP 发送路径
- `uip_close()` 驱动的 FIN/ACK 关闭路径
- `FinWait1` / `FinWait2` / `Closing` / `CloseWait` / `LastAck` / `TimeWait` 的部分状态迁移
- RST 关闭路径
- 定时器驱动的最小重传与超时关闭路径

---

## 6. 当前未声明完成的范围

当前实现不能表述为“完整 C 版 uIP 已完成移植”。

从代码与测试范围看，以下内容仍不应在文档中提前声明为已完成：

- `uip.c` 其余所有分支与边界情况
- 完整 TCP 状态机细节
- 分片重组等可选能力
- 独立 `uiplib` 模块
- 超出当前测试覆盖范围的原版附加路径

因此，当前正确表述应为：

> **当前代码已完成 C 版 uIP 的部分核心能力移植，并建立了 ARP / IPv4 / ICMP / UDP / TCP 的最小可验证闭环。**

---

## 7. 后续文档与实现约束

后续继续补齐时，应遵循以下约束：

1. 只补齐 C 版 uIP 已有功能
2. 不为了“更现代”而改变主流程
3. 不增加超出原版的新协议能力
4. 不把临时测试辅助接口写成长期架构承诺
5. 文档只描述当前代码已具备的能力，或明确列出尚未完成的原版能力

---

## 8. 驱动协作模型

当前仍应以 C 版 uIP 的驱动协作方式理解本项目：

```text
收包：
  if Ethernet type == IP:
    uip_arp_ipin()
    uip_input()
    if uip_len > 0:
      uip_arp_out()
      send()

  if Ethernet type == ARP:
    uip_arp_arpin()
    if uip_len > 0:
      send()

定时：
  uip_periodic(i)
  if uip_len > 0:
    uip_arp_out()
    send()

UDP 定时：
  uip_udp_periodic(i)
  if uip_len > 0:
    uip_arp_out()
    send()
```

这仍然是当前项目应坚持的总体模型。
