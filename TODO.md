# uIP-uya TODO List

> 目标：用 uya 忠实重写 C 版 uIP，优先完成最小可运行闭环，再逐步扩展协议与应用。

## P0：项目骨架与基线

- [ ] 建立 `src/uip/` 目录
- [ ] 创建模块文件：`uip_conf.uya`
- [ ] 创建模块文件：`uip_types.uya`
- [ ] 创建模块文件：`uip_arch.uya`
- [ ] 创建模块文件：`uip_checksum.uya`
- [ ] 创建模块文件：`uip_state.uya`
- [ ] 创建模块文件：`uip.uya`
- [ ] 创建模块文件：`uip_arp_types.uya`
- [ ] 创建模块文件：`uip_arp.uya`
- [ ] 创建模块文件：`uiplib.uya`
- [ ] 创建模块文件：`driver_sim.uya`
- [ ] 创建模块文件：`app_hello_world.uya`
- [ ] 补充 `docs/README.md`，加入 roadmap / backlog / TODO 导航
- [ ] 约定模块命名、常量命名、测试命名规则

## P1：配置层 `uip_conf`

- [ ] 定义 `UIP_BUFSIZE`
- [ ] 定义 `UIP_LLH_LEN`
- [ ] 定义 `UIP_CONNS`
- [ ] 定义 `UIP_LISTENPORTS`
- [ ] 定义 `UIP_UDP_CONNS`
- [ ] 定义 `UIP_ARPTAB_SIZE`
- [ ] 定义 `UIP_TCP_MSS`
- [ ] 定义 `UIP_RECEIVE_WINDOW`
- [ ] 定义 `UIP_RTO`
- [ ] 定义 `UIP_MAXRTX`
- [ ] 定义 `UIP_MAXSYNRTX`
- [ ] 定义 `UIP_TIME_WAIT_TIMEOUT`
- [ ] 定义 `UIP_UDP`
- [ ] 定义 `UIP_ACTIVE_OPEN`
- [ ] 定义 `UIP_STATISTICS`
- [ ] 定义 `UIP_LOGGING`
- [ ] 定义主机地址/网关/掩码相关配置入口
- [ ] 定义 MAC 地址相关配置入口
- [ ] 为配置常量补充基础测试

## P2：类型层 `uip_types`

- [ ] 定义 IPv4 地址类型 `uip_ipaddr_t`
- [ ] 预留 IPv6 类型扩展位
- [ ] 定义 `uip_conn`
- [ ] 定义 `uip_udp_conn`
- [ ] 定义以太网头结构
- [ ] 定义 IPv4 头结构
- [ ] 定义 TCP/IP 组合头结构
- [ ] 定义 UDP/IP 组合头结构
- [ ] 定义 ICMP/IP 组合头结构
- [ ] 定义 TCP flags 常量
- [ ] 定义 ICMP type 常量
- [ ] 定义 `UIP_DATA` / `UIP_TIMER` / `UIP_POLL_REQUEST` / `UIP_UDP_TIMER`
- [ ] 定义 TCP 状态常量：`CLOSED` / `LISTEN` / `SYN_RCVD` / `SYN_SENT` / `ESTABLISHED` / `FIN_WAIT_1` / `FIN_WAIT_2` / `CLOSING` / `TIME_WAIT` / `LAST_ACK`
- [ ] 定义协议头字段访问辅助函数或等价表达方式
- [ ] 补充报头布局/字段读写测试

## P3：架构层 `uip_arch` + `uip_checksum`

- [ ] 实现 `htons`
- [ ] 实现 `ntohs`
- [ ] 实现 `htonl` / `ntohl`（若需要）
- [ ] 实现 `add32`
- [ ] 实现基础校验和累加器
- [ ] 实现 IPv4 header checksum
- [ ] 实现 TCP checksum
- [ ] 实现 UDP checksum
- [ ] 实现 pseudo header checksum
- [ ] 为 checksum 补充固定向量测试
- [ ] 为大小端转换补充测试

## P4：全局状态 `uip_state`

- [ ] 定义全局 `uip_buf`
- [ ] 定义全局 `uip_len`
- [ ] 定义全局 `uip_appdata`
- [ ] 定义全局 `uip_sappdata`
- [ ] 定义全局 `uip_flags`
- [ ] 定义当前 TCP 连接 `uip_conn`
- [ ] 定义当前 UDP 连接 `uip_udp_conn`
- [ ] 定义 `uip_conns[UIP_CONNS]`
- [ ] 定义 `uip_udp_conns[UIP_UDP_CONNS]`
- [ ] 定义 `uip_listenports[UIP_LISTENPORTS]`
- [ ] 定义 `uip_hostaddr`
- [ ] 定义 `uip_draddr`
- [ ] 定义 `uip_netmask`
- [ ] 定义 `uip_ethaddr`
- [ ] 定义 `ipid`
- [ ] 定义 `iss`
- [ ] 实现 `uip_init()`
- [ ] 初始化所有 TCP 连接状态
- [ ] 初始化所有 UDP 连接状态
- [ ] 初始化 listen port 表
- [ ] 补充初始化状态测试

## P5：核心入口 `uip`

- [ ] 实现 `uip_process(flag)` 骨架
- [ ] 实现 `uip_input()`
- [ ] 实现 `uip_periodic(index)`
- [ ] 实现 `uip_udp_periodic(index)`
- [ ] 实现 `uip_poll_conn(conn)`
- [ ] 实现 `uip_listen(port)`
- [ ] 实现 `uip_unlisten(port)`
- [ ] 实现 `uip_send(data, len)`
- [ ] 建立 `flag -> 处理路径` 分发逻辑
- [ ] 建立 IPv4 包最小合法性检查
- [ ] 建立 TCP 路径分支
- [ ] 建立 UDP 路径分支占位
- [ ] 建立 ICMP 路径分支占位
- [ ] 建立 timer 路径分支
- [ ] 建立 poll 路径分支
- [ ] 补充核心入口分支测试

## P6：TCP 最小闭环

- [ ] 解析入站 TCP 头
- [ ] 匹配监听端口
- [ ] 匹配已建立连接
- [ ] 实现 `LISTEN -> SYN_RCVD`
- [ ] 实现 `SYN_RCVD -> ESTABLISHED`
- [ ] 实现 `ESTABLISHED` 数据接收路径
- [ ] 实现 `ESTABLISHED` ACK 路径
- [ ] 实现 `ESTABLISHED` 发送路径
- [ ] 实现 `FIN_WAIT_1`
- [ ] 实现 `FIN_WAIT_2`
- [ ] 实现 `LAST_ACK`
- [ ] 实现 `TIME_WAIT`
- [ ] 实现基本 RST 处理
- [ ] 实现超时重传最小逻辑
- [ ] 实现 `uip_connected()`
- [ ] 实现 `uip_newdata()`
- [ ] 实现 `uip_acked()`
- [ ] 实现 `uip_rexmit()`
- [ ] 实现 `uip_poll()`
- [ ] 实现 `uip_closed()`
- [ ] 实现 `uip_aborted()`
- [ ] 实现 `uip_timedout()`
- [ ] 实现 `uip_datalen()`
- [ ] 实现 `uip_mss()`
- [ ] 构造 SYN/SYN-ACK/ACK 报文测试
- [ ] 构造 data/ack/fin 报文测试
- [ ] 构造超时/重传测试

## P7：ARP 与 Ethernet

- [ ] 定义 ARP 头结构
- [ ] 定义 ARP 表项结构
- [ ] 定义 `arp_table[UIP_ARPTAB_SIZE]`
- [ ] 实现 `uip_arp_ipin()`
- [ ] 实现 `uip_arp_arpin()`
- [ ] 实现 `uip_arp_out()`
- [ ] 实现 `uip_arp_timer()`
- [ ] 实现 ARP 表学习逻辑
- [ ] 实现 ARP reply 构造
- [ ] 实现出站 IP 包的 Ethernet 头封装
- [ ] 实现 ARP 老化逻辑
- [ ] 构造 ARP request/reply 测试

## P8：驱动与回放环境

- [ ] 设计 `driver_sim` 接口
- [ ] 支持内存报文回放
- [ ] 支持报文送入 `uip_buf`
- [ ] 支持读取 `uip_len` 与出站缓冲区
- [ ] 支持模拟主循环：收包 -> `uip_input()` -> 发包
- [ ] 支持模拟 periodic timer 调用
- [ ] 准备第一组固定测试报文样本
- [ ] 准备第一组 TCP 建连场景回放
- [ ] 准备第一组 ARP 场景回放

## P9：最小应用 `hello-world`

- [ ] 设计 `appcall` 协作接口
- [ ] 定义 hello-world 连接状态结构
- [ ] 实现 `hello_world_init()`
- [ ] 实现 `hello_world_appcall()`
- [ ] 第一版先用显式状态机发送 greeting
- [ ] 第一版接收一行输入
- [ ] 第一版返回 `Hello <name>`
- [ ] 关闭连接
- [ ] 编写 hello-world 端到端测试

## P10：协议栈增强

- [ ] 实现 active open
- [ ] 实现 `uip_connect()`
- [ ] 实现 UDP 最小路径
- [ ] 实现 `uip_udp_new()`
- [ ] 实现 UDP periodic
- [ ] 实现 ICMP echo reply
- [ ] 补齐更完整的 TCP 重传策略
- [ ] 补齐更完整的状态迁移边界处理
- [ ] 实现统计结构与统计更新
- [ ] 实现日志钩子

## P11：辅助库 `uiplib`

- [ ] 实现 IPv4 地址字符串转换
- [ ] 实现文本到 IPv4 地址解析
- [ ] 实现端口/字节辅助函数（按需要）
- [ ] 为 `uiplib` 增加基础测试

## P12：应用兼容层

- [ ] 评估是否移植 protothread
- [ ] 评估是否移植 protosocket
- [ ] 若迁移，先实现 `PSOCK_INIT`
- [ ] 若迁移，先实现 `PSOCK_BEGIN`
- [ ] 若迁移，先实现 `PSOCK_SEND`
- [ ] 若迁移，先实现 `PSOCK_SEND_STR`
- [ ] 若迁移，先实现 `PSOCK_READTO`
- [ ] 若迁移，先实现 `PSOCK_CLOSE`
- [ ] 若迁移，先实现 `PSOCK_END`
- [ ] 后续实现 `PSOCK_GENERATOR_SEND`

## P13：上层应用迁移

- [ ] 迁移 `hello-world` 原版风格实现
- [ ] 迁移 `webserver`
- [ ] 迁移 `httpd-fs`
- [ ] 迁移 `httpd-cgi`
- [ ] 迁移 `webclient`
- [ ] 迁移 `resolv`
- [ ] 迁移 `telnetd`
- [ ] 迁移 `dhcpc`
- [ ] 迁移 `smtp`

## P14：测试与质量

- [ ] 建立测试目录结构
- [ ] 建立纯函数测试约定
- [ ] 建立报文级测试约定
- [ ] 建立场景级测试约定
- [ ] 为每个阶段补最小回归测试
- [ ] 为关键 TCP 状态迁移补回归用例
- [ ] 为 ARP 表行为补回归用例
- [ ] 为 hello-world 端到端补回归用例
- [ ] 为后续 webserver/webclient 预留测试模板

## P15：文档与里程碑管理

- [ ] 在 `docs/README.md` 中加入 `uip-roadmap.md` 链接
- [ ] 在 `docs/README.md` 中加入本 TODO 链接
- [ ] 为 M1-M10 建立完成状态跟踪
- [ ] 约定每阶段完成定义
- [ ] 约定提交信息风格与里程碑对应关系
- [ ] 阶段完成后同步更新 roadmap / backlog / TODO

## 第一阶段完成定义

- [ ] 已有稳定 `src/uip/` 模块骨架
- [ ] 已实现 `uip_init()`
- [ ] 已实现 `uip_process(flag)` 基础流程
- [ ] 已实现固定容量 TCP 连接表
- [ ] 已实现固定容量 ARP 表
- [ ] 已能在 host 回放环境下完成一次 TCP 建连、收发、关闭
- [ ] 已有 hello-world 最小应用可运行
- [ ] 已有关键路径回归测试
