# unix uIP 示例（Uya 版）

对应原始目录：`/home/ubuntu/Documents/uip/unix`

当前已移植：
- `main.c` → `examples/unix/main.uya`
- `clock-arch.c/.h` → 内联在 `examples/unix/main.uya` 的 `clock_time_ms()` / `CLOCK_SECOND`
- `tapdev.c/.h` → 内联在 `examples/unix/main.uya` 的 `TapDev` / `tapdev_*`
- 构建入口 → `examples/unix/Makefile`

## 当前状态

这是按原目录结构逻辑移植的真实 TAP 版本：
- 打开 `/dev/net/tun`
- 通过 `TUNSETIFF` 申请 `tap0`
- 设置 nonblocking
- 轮询收包
- 驱动 `uip_input()` / `uip_periodic()` / `uip_arp_*()`
- 监听 TCP `1234` 端口
- 建连后回发 `helloworld\r\n`

## 构建与运行

```bash
cd /home/ubuntu/Documents/uip-uya
make -C examples/unix tap-up
make -C examples/unix build
make -C examples/unix run
```

连接测试：

```bash
nc 192.168.0.2 1234
```

连上后应收到：

```text
helloworld
```

## 运行前准备

需要 Linux 且启用 TUN/TAP：

```bash
sudo modprobe tun
```

当前示例默认申请接口名 `tap0`，并**不自动执行 ifconfig/ip 命令**，需要手工配置：

```bash
sudo ip tuntap add dev tap0 mode tap
sudo ip addr add 192.168.0.1/24 dev tap0
sudo ip link set tap0 up
```

uIP 端自身地址固定为：
- host: `192.168.0.2`
- router: `192.168.0.1`
- netmask: `255.255.255.0`

## 说明

与原始 `main.c` 相比，当前版本有两个实现差异：

1. 原版 `tapdev_read()` 用 `select()`；这里改成了：
   - `O_NONBLOCK`
   - 主循环 `sleep_ms(1)` 轮询

2. 原版示例调用 `httpd_init()`；当前仓库没有直接可复用的 unix webserver app，因此此部分尚未接入具体应用层服务。

## 下一步建议

要真正“可以运行并对外响应”，还需要补一项：

- 接入一个 Uya 侧最小 TCP app（等价于原始 unix 示例里的 `webserver`）

如果需要，我下一步可以继续把它补成：
- **最小 echo/http demo**
- 并给出完整启动命令
