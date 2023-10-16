# DJI DSP 工具

## 简介

本工具提供了一些处理 DSP 文件的常用工具，包括

- 编解码工具 dsp-codec
- *and more*

## 安装

### 使用 PyPI 安装

目前只上传到 TestPyPI 网站
运行命令
```bash
pip install -i https://test.pypi.org/simple/ dspy_tool
```

### 使用源码安装

1. 克隆本项目或下载 zip 文件
   克隆命令
   ```bash
   git clone https://github.com/RMYC-Lab/dji-dsp-tools.git
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
```
dsp-codec input [--output OUTPUT] [--file-name FILE_NAME]
          [--std-out] [--raw] [--delete-comments]
          [--title TITLE] [--creator CREATOR]
          [-h] [--version]
```

### 参数
- input: 输入文件路径 (`.dsp` 或 `.py` 格式文件)
- `-o OUTPUT; --output OUTPUT`: 输出文件夹路径
- `-f FILE_NAME; --file-name FILE_NAME`: 输出文件名
- `-s; --std-out`: 输出到标准输出 (打印到屏幕上)
- `-r; --raw`: 输出为原始数据 (DSP xml 解码后文件)
- `-d; --delete-comments`: 删除图形化块注释 (以 `#block` 开头)
- `-t TITLE; --title TITLE`: 设置文件标题
- `-c CREATOR; --creator CREATOR`: 设置文件创建者
- `-h; --help`: 显示帮助信息
- `--version`: 显示版本信息
