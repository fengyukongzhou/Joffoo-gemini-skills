---
name: rename-linked-images
description: Rename linked images in Markdown files and update their references across the entire Obsidian vault. Also supports converting between WikiLinks and standard Markdown image links. Use when the user asks to rename images, organize attachments, or convert link formats (Wiki to MD, MD to Wiki) in an Obsidian note.
---

# Rename Linked Images & Format Converter

此 Skill 用于批量重命名 Markdown 文档中引用的图片文件，并**同步更新整个 Vault 中所有相关文档的链接**，同时支持 WikiLinks 和标准 Markdown 链接之间的转换。

## 核心功能
1. **自动提取**：识别文档中的 WikiLinks (`![[...]]`) 和标准 Markdown 图片引用。
2. **规则重命名**：支持自定义前缀、基于文件创建日期的日期字符串（MMDD/DDMM/YYMMDD）以及自动递增的序号。
3. **全库同步更新**：重命名物理文件后，自动遍历整个 Vault，更新**所有**引用这些图片的 Markdown 文档中的链接。
4. **格式转换**：支持 WikiLinks 格式 (`![[image.png|alt]]`) 与标准 Markdown 格式 (`![alt](image.png)`) 的相互转换。

## 使用方法

使用 `run_shell_command` 调用配套的 Python 脚本。

### 1. 图片重命名
**命令：**
```bash
python .gemini/skills/rename-linked-images/scripts/rename_images.py "<markdown_file_path>" --prefix <prefix> --date-format <MMDD|DDMM|YYMMDD> --pad-length <length>
```

**参数说明：**
- `markdown_file_path`: 必填，Markdown 文件的绝对或相对路径。
- `--prefix`: 可选，新文件名的前缀，默认为 `img`。
- `--date-format`: 可选，日期格式，可选 `MMDD`（默认）、`DDMM`、`YYMMDD`。
- `--start-index`: 可选，序号起始值，默认为 `1`。
- `--pad-length`: 可选，序号位数，默认为 `3`（如 001, 002）。
- `--vault-root`: 可选，Vault 根目录路径。如不指定，会自动向上查找 `.obsidian` 文件夹来确定。
- `--dry-run`: 可选，预览模式，只显示将要执行的操作，不实际修改任何文件。

**示例：**
```bash
# 基本使用（自动检测 Vault 根目录）
python .gemini/skills/rename-linked-images/scripts/rename_images.py "_inbox/note.md"

# 自定义前缀和格式
python .gemini/skills/rename-linked-images/scripts/rename_images.py "_inbox/note.md" --prefix vol --date-format MMDD --pad-length 3

# 先预览再执行
python .gemini/skills/rename-linked-images/scripts/rename_images.py "_inbox/note.md" --prefix vol --dry-run
```

### 2. 链接格式转换
**命令：**
```bash
python .gemini/skills/rename-linked-images/scripts/convert_links.py "<markdown_file_path>" --to <markdown|wiki>
```

**参数说明：**
- `markdown_file_path`: 必填，Markdown 文件的绝对或相对路径。
- `--to`: 必填，目标格式，可选 `markdown` 或 `wiki`。
- `--dry-run`: 可选，预览转换结果。

## 工作原理

### 图片重命名流程
```
1. 读取指定的 Markdown 文件
   ↓
2. 提取文件中所有的图片链接 (![[...]] 或 ![](...))
   ↓
3. 在 Vault 中查找这些图片文件的实际位置
   ↓
4. 生成新的文件名（前缀 + 日期 + 序号）
   ↓
5. 重命名物理文件
   ↓
6. 【关键】遍历整个 Vault 的所有 Markdown 文件
   ↓
7. 更新所有引用这些图片的链接
```

### 图片搜索路径
脚本会按以下顺序查找图片文件：
1. 当前 Markdown 文件所在目录
2. 同级目录的 `_attachments`、`assets`、`attachments`、`Attachments` 文件夹
3. 整个 Vault 范围内的其他位置

## 注意事项
- **全库更新**：重命名操作会更新整个 Vault 中所有引用该图片的文档，而不仅是当前文档。
- **链接格式保留**：重命名操作会自动保留原始的链接格式（WikiLinks 或 Markdown）。
- **格式转换操作**：仅修改 Markdown 文本，不会触动物理文件。
- **安全建议**：建议在执行大规模操作之前先使用 `--dry-run` 进行预览。
- **Vault 根目录**：脚本会自动向上查找 `.obsidian` 文件夹来确定 Vault 根目录，也可以通过 `--vault-root` 手动指定。
