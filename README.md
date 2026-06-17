# gamekee-nikke-live2d

![](./tests/sample.png)

为 GameKee 的 NIKKE 角色生成独立的 Spine live2d HTML 演示页面。

## 功能

- 从 GameKee 内容 API 获取角色的 live2d 资源元数据。
- 按 `.skel` 版本动态下载 Spine 4.0 / 4.1 运行时和角色资源（skel / atlas / png）。
- 生成一个自包含的 `index.html`，支持姿势切换、皮肤切换和点击触发动作。
- 仅使用 Python 标准库，无需第三方依赖。

## 安装

```bash
cd gamekee-nikke-live2d
pip install -e .
```

或者不安装直接运行：

```bash
python -m gamekee_nikke_live2d 164728
```

## 使用方法

### 命令行

```bash
gamekee-nikke-live2d <角色ID> [-o <输出目录>]
```

示例：

```bash
# 默认生成 demo_164728_角色名 目录，不会覆盖之前的生成结果
gamekee-nikke-live2d 164728

# 自定义输出目录
gamekee-nikke-live2d 164728 -o demo_anker
```

然后使用任意静态 HTTP 服务器运行输出目录：

```bash
cd demo_164728
python -m http.server 8766
```

浏览器打开 `http://localhost:8766` 即可查看。

### Python API

```python
from gamekee_nikke_live2d import build_demo

build_demo(char_id=164728, output_dir="demo_anker")
```

## 交互说明

- 顶部按钮：在多个皮肤/换装之间切换（若角色存在多个 `styleData`）。
- 底部按钮：在 `full`、`aim`、`cover` 三种姿势之间切换，仅显示当前皮肤实际拥有的姿势。
- 点击或触摸画布：播放当前姿势对应的动作动画，结束后自动回到 idle。
- 左上角「调试面板」按钮：打开/关闭 Spine 调试面板，可搜索并选择骨骼/插槽，实时调整位置、缩放、旋转、透明度（隐藏/显示）。

## 注意事项

- GameKee 的这些模型实际使用的是 **Spine**（常见 4.0 / 4.1），不是 Live2D Cubism；工具会根据每个 `.skel` 文件自动加载对应运行时。
- 由于浏览器对 `file://` 协议的 `fetch` 存在跨域限制，生成的 demo 必须通过 HTTP 服务器访问。
