# uIP Uya 移植

版本：v0.1.0

该目录提供对原始 `uIP` 仓库核心功能的 Uya 语言移植，代码严格位于 `ports/uip/` 下，未写入 `uya/` 目录。

## 当前内容

- 核心实现：`ports/uip/uiplib.uya`
- 测试目录：`ports/uip/tests/`

## 已拆分测试

为避免 TCP 与 UDP 测试相互干扰，测试已按职责拆分：

- `ports/uip/tests/uip_core_base_test.uya`：基础类型、地址、校验和、定时器等核心能力
- `ports/uip/tests/state_and_timer_test.uya`：状态初始化、监听、连接分配、UDP 连接管理
- `ports/uip/tests/uip_tcp_core_test.uya`：TCP 核心处理逻辑
- `ports/uip/tests/uip_tcp_handshake_test.uya`：TCP 握手与状态迁移
- `ports/uip/tests/udp_test.uya`：UDP 收发与路由逻辑
- `ports/uip/tests/uip_arp_test.uya` / `ports/uip/tests/arp_test.uya`：ARP 相关行为
- `ports/uip/tests/uiplib_ipaddrconv_test.uya`：`uiplib_ipaddrconv` 聚焦测试
- `ports/uip/tests/core_primitives_test.uya`：部分基础原语测试

## 运行方式

在仓库根目录执行：

```bash
./uya/bin/uya test ports/uip/tests/uip_core_base_test.uya ports/uip/uiplib.uya
./uya/bin/uya test ports/uip/tests/state_and_timer_test.uya ports/uip/uiplib.uya
./uya/bin/uya test ports/uip/tests/uip_tcp_core_test.uya ports/uip/uiplib.uya
./uya/bin/uya test ports/uip/tests/uip_tcp_handshake_test.uya ports/uip/uiplib.uya
./uya/bin/uya test ports/uip/tests/udp_test.uya ports/uip/uiplib.uya
./uya/bin/uya test ports/uip/tests/uip_arp_test.uya ports/uip/uiplib.uya
```

当前会话中已单独验证过：

- `ports/uip/tests/uip_tcp_core_test.uya`
- `ports/uip/tests/udp_test.uya`

## 移植范围

当前 `uiplib.uya` 覆盖内容包括：

- uIP 常量、类型与运行时状态定义
- IPv4 地址辅助函数
- 字节序与校验和计算
- TCP 基础状态机与部分报文构造逻辑
- UDP 连接匹配、输入输出处理
- ARP 状态与基本操作
- 定时器与连接初始化能力

## 说明

- 目前按测试文件分别编译/执行，暂不做聚合编译。
- 若后续继续统一修复，可在现有拆分基础上逐个回归测试。
