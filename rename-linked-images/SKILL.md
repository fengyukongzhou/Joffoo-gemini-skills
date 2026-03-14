---
name: rename-linked-images
description: Rename linked images in Markdown files and update their references. Also supports converting between WikiLinks and standard Markdown image links. Use when the user asks to rename images, organize attachments, or convert link formats (Wiki to MD, MD to Wiki) in an Obsidian note.
---

# Rename Linked Images & Format Converter

此 Skill 用于批量重命名 Markdown 文档中引用的图片文件，并同步更新文档内的链接，同时支持 WikiLinks 和标准 Markdown 链接之间的转换。

## 核心功能
1. **自动提取**：识别文档中的 WikiLinks (`![[...] ]`) 和标准 Markdown 图片引用。
2. **规则重命名**：支持自定义前缀、基于文件创建日期的日期字符串（MMDD/DDMM/YYMMDD）以及自动递增的序号。
3. **同步更新**：重命名物理文件后，自动更新 Markdown 文档中的所有引用。
4. **格式转换**：支持 WikiLinks 格式 (`![[image.png|alt]]`) 与标准 Markdown 格式 (`![alt](image.png)`) 的相互转换。

## 使用方法

使用 `run_shell_command` 调用配套的 Python 脚本。

### 1. 图片重命名
**命令：**
```bash
python .gemini/skills/rename-linked-images/scripts/rename_images.py "<markdown_file_path>" --prefix <prefix> --date-format <MMDD|DDMM|YYMMDD> --pad-length <length>
```
- 详见：`rename_images.py` 参数说明。

### 2. 链接格式转换
**命令：**
```bash
python .gemini/skills/rename-linked-images/scripts/convert_links.py "<markdown_file_path>" --to <markdown|wiki>
```
**参数说明：**
- `markdown_file_path`: 必填，Markdown 文件的绝对或相对路径。
- `--to`: 必填，目标格式，可选 `markdown` 或 `wiki`。
- `--dry-run`: 可选，预览转换结果。

## 注意事项
- 重命名操作会自动保留原始的链接格式。
- 格式转换操作仅修改 Markdown 文本，不会触动物理文件。
- 建议在执行大规模操作之前先使用 `--dry-run` 进行预览。
