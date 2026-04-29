# uIP-uya 开发路线图

本文档用于把“使用 uya 重写 C 版 uIP 协议栈”的目标落地为可执行的阶段计划。

本路线图强调三点：

- 忠实保留 C 版 uIP 的核心架构
- 按最小可验证闭环分阶段推进
- 先完成协议栈核心，再逐步迁移上层应用

相关参考：

- 项目说明：`README.md`
- 架构说明：`docs/architecture.md`
- 迁移清单：`docs/uip-porting-plan.md`

---

## 1. 目标与范围

### 1.1 总目标

uIP-uya 的目标不是实现“受 uIP 启发的新协议栈”，而是：

> 使用 uya 重新实现一遍 C 语言版 uIP，并尽量保留其单缓冲区、固定容量、事件驱动、编译期裁剪的原始设计取舍。

### 1.2 第一阶段目标

第一阶段只追求“最小可运行闭环”，不追求一次覆盖全部功能。

优先实现：

- 单一主缓冲区 `uip_buf`
- `uip_process(flag)` 主处理流程
- IPv4
- TCP 最小 server 路径
- ARP
- 固定容量连接表
- host 环境下可回放/可测试的驱动协作模型
- 一个最小示例应用（hello-world）

### 1.3 非目标

当前阶段不做以下工作：

- 不改造成现代 socket API
- 不引入多 buffer 池
- 不引入动态分配驱动的连接管理
- 不先做完整 webserver / webclient / DHCP / DNS
- 不先做“漂亮分层”重构

---

## 2. 开发原则

### 2.1 数据模型优先一致

优先保持与原版一致的：

- `uip_buf`
- `uip_len`
- `uip_appdata`
- `uip_sappdata`
- `uip_conn`
- `uip_udp_conn`
- `uip_conns[]`
- `uip_udp_conns[]`
- `uip_listenports[]`

### 2.2 主流程优先一致

优先保持以 `uip_process(flag)` 为中心的单核处理流程。

允许将部分宏改写为 uya 函数/内联函数，但不改变主处理模型。

### 2.3 编译期资源模型优先一致

优先保留原版的：

- 固定容量数组
- 编译期常量裁剪
- 无 GC
- 无运行时动态扩容

### 2.4 先测试闭环，再功能扩张

每一阶段都必须有明确验收标准：

- 输入什么报文
- 预期什么状态迁移
- 预期输出什么报文
- 是否具备回归测试

---

## 3. 建议模块布局

建议落地如下目录：

```text
src/uip/
  uip_types.uya
  uip_conf.uya
  uip_arch.uya
  uip_checksum.uya
  uip_state.uya
  uip.uya
  uip_arp_types.uya
  uip_arp.uya
  uiplib.uya
  driver_sim.uya
  app_hello_world.uya
```

说明：

- `uip_types.uya`：类型、常量、协议头布局
- `uip_conf.uya`：编译期配置项
- `uip_arch.uya`：字节序和架构相关能力
- `uip_checksum.uya`：校验和逻辑
- `uip_state.uya`：全局状态容器
- `uip.uya`：核心协议栈实现
- `uip_arp.uya`：ARP/Ethernet 协作逻辑
- `uiplib.uya`：辅助函数
- `driver_sim.uya`：宿主测试驱动或报文回放驱动
- `app_hello_world.uya`：最小应用示例

---

## 4. 里程碑计划

## M1：基础骨架与配置层

### 目标

建立能够表达 uIP 的最小工程骨架。

### 任务

1. 创建 `src/uip/` 目录与基础模块文件
2. 实现 `uip_conf.uya`
3. 迁移第一批编译期常量：
   - `UIP_BUFSIZE`
   - `UIP_LLH_LEN`
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
   - `UIP_UDP`
   - `UIP_STATISTICS`
   - `UIP_LOGGING`
   - `UIP_ACTIVE_OPEN`
4. 编写配置相关基础测试

### 验收标准

- 模块结构固定
- 可通过配置常量推导静态数组大小
- 配置改动能影响后续模块编译/裁剪

---

## M2：类型系统与校验和基础

### 目标

完成 `uip.h` 级别的数据表达能力。

### 任务

1. 实现 `uip_types.uya`
2. 迁移：
   - `uip_ipaddr_t`
   - `uip_conn`
   - `uip_udp_conn`
   - IPv4 header
   - TCP/IP combined header
   - UDP/IP combined header
   - ICMP/IP combined header
3. 定义：
   - TCP flags 常量
   - TCP state 常量
   - `UIP_DATA` / `UIP_TIMER` / `UIP_POLL_REQUEST` / `UIP_UDP_TIMER` 等 flag
4. 实现 `uip_arch.uya`
5. 实现 `uip_checksum.uya`
6. 完成：
   - htons / ntohs
   - add32
   - IP checksum
   - TCP/UDP pseudo header checksum

### 验收标准

- 可以声明核心连接表和报文头结构
- 报文字段读写语义稳定
- 已有 checksum 向量测试通过

---

## M3：全局状态与初始化

### 目标

建立原版 uIP 风格的单实例核心状态。

### 任务

1. 实现 `uip_state.uya`
2. 定义并初始化：
   - `uip_buf`
   - `uip_len`
   - `uip_appdata`
   - `uip_sappdata`
   - `uip_flags`
   - `uip_conn`
   - `uip_udp_conn`
   - `uip_conns[]`
   - `uip_udp_conns[]`
   - `uip_listenports[]`
   - `uip_hostaddr`
   - `uip_draddr`
   - `uip_netmask`
   - `uip_ethaddr`
   - `ipid`
   - `iss`
3. 实现 `uip_init()`
4. 增加初始化与边界测试

### 验收标准

- 所有核心状态均可初始化
- 固定容量表项初始状态正确
- 不依赖动态内存分配

---

## M4：核心入口骨架

### 目标

建立 `uip_process(flag)` 与外围入口函数。

### 任务

1. 在 `uip.uya` 中实现：
   - `uip_process(flag)`
   - `uip_input()`
   - `uip_periodic(index)`
   - `uip_udp_periodic(index)`
   - `uip_poll_conn(conn)`
   - `uip_listen(port)`
   - `uip_unlisten(port)`
   - `uip_send(data, len)`
2. 完成主流程的 flag 分发骨架
3. 实现基础 IPv4 包合法性检查
4. 建立 TCP 入站与定时器路径的初始分支

### 验收标准

- 给定不同 flag 能进入正确主流程分支
- `uip_input()` 与 `uip_periodic()` 可触发后续处理
- `uip_send()` 能设置出站数据长度与上下文

---

## M5：TCP 最小可运行闭环

### 目标

优先跑通最小 server 场景。

### 任务

1. 实现最小 TCP 状态机，优先覆盖：
   - `CLOSED`
   - `LISTEN`
   - `SYN_RCVD`
   - `ESTABLISHED`
   - `FIN_WAIT_1`
   - `FIN_WAIT_2`
   - `LAST_ACK`
   - `TIME_WAIT`
2. 支持以下事件：
   - SYN 建连
   - ACK 建立连接
   - 入站数据
   - 发送数据被 ACK
   - FIN 关闭
   - poll
   - timer/rexmit
3. 提供第一批事件状态接口语义：
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
4. 构造最小 TCP 报文回放测试

### 验收标准

- SYN → SYN+ACK
- ACK 后进入 `ESTABLISHED`
- 可接收一段数据并触发应用回调
- 可发送一段数据并生成正确 ACK/响应路径
- 可完成基本关闭流程

---

## M6：ARP 与 Ethernet 协作

### 目标

补齐原版外接式 ARP 模块。

### 任务

1. 实现 `uip_arp_types.uya`
2. 实现 `uip_arp.uya`
3. 支持：
   - `uip_arp_ipin()`
   - `uip_arp_arpin()`
   - `uip_arp_out()`
   - `uip_arp_timer()`
4. 建立固定容量 ARP 表
5. 建立 ARP request/reply 测试

### 验收标准

- 能处理 ARP request 并返回 reply
- 能根据 IP 包学习对端 MAC
- 出站 IP 包前可正确补 Ethernet 头
- ARP 表项支持老化

---

## M7：宿主测试驱动与 hello-world

### 目标

建立最小 end-to-end 演示闭环。

### 任务

1. 实现 `driver_sim.uya`
2. 提供两类测试环境：
   - 内存报文回放
   - 宿主 main loop 模拟
3. 移植 hello-world 最小版应用
4. 第一版 hello-world 先使用显式状态机，不强依赖 protosocket

### 验收标准

- 可以模拟主循环：收包 → 处理 → 发包
- hello-world 可监听端口并收发简单文本
- 具备端到端回归测试

---

## M8：协议栈补全与兼容增强

### 目标

在最小闭环稳定后扩展接近原版核心能力。

### 任务

1. 补齐 active open
2. 补齐 UDP 路径
3. 补齐 ICMP echo
4. 补齐更完整的超时与重传策略
5. 实现 `uiplib.uya`
6. 补齐统计与日志开关路径

### 验收标准

- TCP client/server 双路径可工作
- UDP 分发可工作
- ping/echo 最小路径可工作
- 基础工具函数可供后续应用复用

---

## M9：应用兼容层

### 目标

为 webserver / webclient 等原版应用铺路。

### 任务

1. 评估是否按原版移植 `psock` / `pt`
2. 若迁移，则优先支持：
   - `PSOCK_INIT`
   - `PSOCK_BEGIN`
   - `PSOCK_SEND`
   - `PSOCK_SEND_STR`
   - `PSOCK_READTO`
   - `PSOCK_CLOSE`
   - `PSOCK_END`
3. 后续再补：
   - `PSOCK_GENERATOR_SEND`
4. 将 hello-world 改写为 protosocket 风格（可选）

### 验收标准

- 原版简单应用可以按接近原风格编写
- protosocket 兼容层不改变底层 uIP 核心模型

---

## M10：上层应用迁移

### 目标

逐步迁移 `apps/` 中的代表性应用。

### 建议顺序

1. `hello-world`
2. `webserver`
3. `webclient`
4. `resolv`
5. `telnetd`
6. `dhcpc`
7. `smtp`

### 原因

- `hello-world` 最适合验证 appcall 模型
- `webserver` 最适合验证 server 应用、文件系统、动态输出
- `webclient` 依赖 active open 与 HTTP 解析
- `resolv` / `dhcpc` / `smtp` 放在核心稳定后迁移更稳妥

### 验收标准

- 至少一个 server 类示例稳定运行
- 至少一个 client 类示例稳定运行
- 应用层 API 和 appcall 协作方式收敛稳定

---

## 5. 测试策略

### 5.1 三层测试模型

#### A. 纯函数测试

覆盖：

- 字节序转换
- checksum
- 地址转换
- 配置推导
- 常量与结构布局

#### B. 报文级测试

覆盖：

- 输入原始报文
- 验证状态迁移
- 验证 `uip_len`
- 验证回包头字段
- 验证 flags、seq、ack 变化

#### C. 场景级测试

覆盖：

- TCP 建连
- hello-world 收发
- ARP request/reply
- HTTP GET 最小路径
- retransmit on timer

### 5.2 第一批优先测试用例

1. `uip_init()` 初始化状态
2. SYN 包处理
3. SYN+ACK 生成
4. ACK 建连完成
5. ESTABLISHED 数据上送
6. 应用发送数据
7. FIN 关闭路径
8. ARP request/reply
9. checksum 固定向量

---

## 6. 风险与控制策略

### 6.1 过早现代化重构

风险：偏离项目目标，导致验证困难。

策略：

- 保留单 buffer
- 保留固定表
- 保留 `uip_process(flag)`
- 不先做 socket API

### 6.2 过早移植 protosocket

风险：在核心栈未稳定前引入额外复杂度。

策略：

- hello-world 第一版先用显式状态机
- protosocket 后置到 M9

### 6.3 一次性做完整 TCP

风险：状态机与异常路径复杂度过高。

策略：

- 先做最小 server 闭环
- 后做 active open / UDP / edge case

### 6.4 缺少报文级回归基线

风险：后续改动难以定位回归。

策略：

- 尽快建立报文回放测试
- 每补一条协议路径就补一组固定测试向量

---

## 7. 建议执行顺序

若从当前仓库立即开工，建议按以下顺序推进：

1. 建立 `src/uip/` 模块骨架
2. 完成 `uip_conf.uya`
3. 完成 `uip_types.uya`
4. 完成 `uip_arch.uya` 与 `uip_checksum.uya`
5. 完成 `uip_state.uya` 与 `uip_init()`
6. 完成 `uip_process(flag)` 框架
7. 跑通 TCP listen + SYN/SYN-ACK/ACK
8. 移植 hello-world 显式状态机版
9. 实现 ARP 与主循环驱动模拟
10. 再评估 protosocket 与 webserver 迁移

---

## 8. 第一阶段完成定义

当满足以下条件时，可认为第一阶段完成：

- 有稳定的 `src/uip/` 核心模块布局
- 有可工作的 `uip_init()` 与 `uip_process(flag)`
- 有固定容量 TCP 连接表与 ARP 表
- 可在 host 测试环境下完成一次 TCP 建连、收发、关闭
- hello-world 最小应用可运行
- 关键协议路径有回归测试

在此之后，再进入 UDP、ICMP、webserver、webclient 等扩展阶段。
