# DJI DSP 工具

## 简介

本工具提供了一些处理 DSP 文件的常用工具，包括

- 编解码工具 dsp-codec
- *and more*

## 安装

### 使用 PyPI 安装

运行命令
```bash
pip install dspy_tool
```

若您网络条件不佳，建议使用清华源安装
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple dspy_tool
```

### 使用源码安装

需要您提前安装 Python, Git 以及 [flit](https://pypi.org/project/flit/) 包

1. 克隆本项目或下载 zip 文件  
   克隆命令  
   Using SSH
   ```bash
   git clone git@github.com:RMYC-Lab/dspy-tool.git
   ```
   or using HTTPS
   ```bash
   git clone https://github.com/RMYC-Lab/dspy-tool.git
   ```
2. 进入项目文件夹
   ```bash
   cd dji-dsp-tools
   ```
3. 安装
   ```bash
   flit install
   ```

## DSP 编解码工具 dsp-codec

命令
`python -m dspy_tool.cli.dsp_codec` 或者
```
dsp-codec input [--output OUTPUT] [--file-name FILE_NAME]
          [--std-out] [--raw] [--delete-comments]
          [--title TITLE] [--creator CREATOR]
          [-h] [--version]
```

### 参数

- input: 输入文件路径 (`.dsp` 或 `.py` 格式文件)
- `-o OUTPUT, --output OUTPUT`: 输出文件夹路径
- `-f FILE_NAME, --file-name FILE_NAME`: 输出文件名  
  若为空，则会根据输入文件名及当前时间生成输出文件名
- `-s, --std-out`: 输出到标准输出 (打印到屏幕上)  
  *Update in verison 0.1.1: 现在会直接 `return` 解码后的字符以方便其他程序使用*
- `-r, --raw`: 输出为原始数据 (DSP 解码后 xml 文件)
- `--dc, --delete-comments`: 删除图形化块注释 (以 `#block` 开头)
- `--pc, --process-chinese`: 处理中文字符  
  将会将 `.dsp` 文件的 _xx_xx_xx_ 格式的字符转换为中文字符 (实际为 utf-8 编码)
- `-t TITLE, --title TITLE`: 设置文件标题
- `-c CREATOR, --creator CREATOR`: 设置文件创建者
- `--debug`: 输出调试信息
- `-h, --help`: 显示帮助信息
- `-v, --version`: 显示版本信息

## DSP 文件管理器 dsp-fm

命令
`python -m dspy_tool.cli.file_manager` 或者
```
dsp-fm [--dsp-dirs] [--add ADD] [--remove REMOVE] [--list] [--tui] [--version] [-h] 
```

### 参数

- `--dsp-dirs, -d`: 显示 DSP 文件夹列表
- `--add ADD, -a ADD`: 添加 DSP 文件夹
- `--remove REMOVE, -r REMOVE`: 移除 DSP 文件夹
- `--list, -l`: 列出 DSP 文件夹列表
- `--tui, -t`: 使用 TUI 显示 DSP 文件夹列表  
  进入后程序将自动扫描 DSP 文件夹列表中的文件并显示  
  并在右方显示 Python 代码  
  快捷键:  
  - `C`: 复制选中的 Python 代码到剪贴板
  - `D`: 解密选中的文件 且在 Windows 资源管理器中打开
  - `S`: 切换界面风格
  - `O`: 在 Windows 资源管理器中打开选中的文件夹
  - `Q`: 退出 TUI
- `--version, -v`: 显示版本信息
- `-h, --help`: 显示帮助信息

## 常见问题 Q&A

1. Q: 为什么我安装不了？  
   A: 请检查你的 Python 版本，本工具需要 Python 3.8 或以上版本

2. Q: 提示找不到文件？  
   A: 请检查你的环境变量是否配置正确，或者使用 `python -m dspy_tool.cli.TOOL_NAME` 命令
