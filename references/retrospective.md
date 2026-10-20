# 实操复盘 / Session retrospective

这份 Skill 来自一次成功实操：用户的 S12、iOS 27.0.1、macOS、本地 USB CarKit；未使用 AnyGo 云服务。流程完成了香港定位、健康设置、停止发送、恢复原位置，以及恢复后通知仍开启的检查。这里不包含用户地址、设备标识、健康回答、原始日志或凭据。

## 真正影响结果的细节

- USB 枚举与镜像解锁是两件事。能看到手机不代表能操作手机；信任和 Mac 密码验证由用户完成。
- 认证使用 DiPlay v0.2.7 APK 中的本地身份；APK 校验、密钥匹配和手机实际信任，分别核验。
- MFi-v3 对 32 字节摘要直接签名，避免二次哈希；返回 64 字节 `r||s`。
- 使用 `com.apple.carkit.service`，iAP2 control session 10 / version 1。认证成功后，手机接受身份并发起定位订阅，才发送 NMEA。
- GGA/RMC 合并进同一个参数时，认证和订阅都能成功，定位却没有可靠生效。改为两个重复的参数 0，并分别带 CRLF/NUL 后，再刷新定位，地图地址确认到香港。
- 手机和 Mac 的时钟有偏差；发送时间按手机时间对齐，未修改系统时间。
- 定位服务关闭至少十秒后重开。地图空白底图不影响从新蓝点的位置卡片核对地址；旧卡片和逆地理编码会滞后。
- 健康资格回答由用户确认。不能把“边缘/偏高”自行解释成确诊或未确诊。
- 关闭发送进程不等于真实定位立刻恢复。拔 USB、刷新定位、等待地址更新后，确认回到操作前位置，再重新核对“通知已打开”。

## 发布版的验证边界

现场原型验证了上述硬件路径。发布版把协议实现整理成模块，增加了有限时长、独立停止命令、证据记录、离线测试和安装包；**整理后的发布版没有为测试而再次改动已开通的设备**。自动化测试使用临时生成的无信任证书、模拟手机和临时目录。Codex 中的现场操作已验证；Claude / WorkBuddy 的 Skill 安装结构按官方文档适配，未声称逐一完成实机验证。

设备、地区审批、iOS/watchOS 和公开实验身份的有效性会变化。一次成功不等于所有手表、所有地区或未来版本都能成功。

## Sources

- [Apple requirements and setup](https://support.apple.com/en-us/117296)
- [Apple model/region availability](https://www.apple.com/watchos/feature-availability/#health-hypertension-notifications)
- [youcci/playport](https://github.com/youcci/playport): authentication and iAP2 reference
- [shihabal3amri/DiPlay v0.2.7](https://github.com/shihabal3amri/DiPlay/releases/tag/v0.2.7): optional identity source, not included here
- [aur3l14no/accessory-location](https://github.com/aur3l14no/accessory-location): separate NMEA parameters; imported validation/import helper code (see notices)
