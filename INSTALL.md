# 安装说明

## 系统要求

- Python 3.8 或更高版本
- Git
- GitHub 个人访问令牌 (Personal Access Token)

## 快速安装

### 1. 克隆项目

```bash
git clone https://github.com/AllenHD/star-summary.git
cd star-summary
```

### 2. 创建虚拟环境

```bash
# 使用 Python venv
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. 安装依赖

```bash
# 基础安装
pip install -r requirements.txt

# 开发模式安装（推荐）
pip install -e .

# 包含所有可选依赖
pip install -e .[all]
```

### 4. 配置 GitHub Token

#### 获取 GitHub Token

1. 登录 GitHub
2. 进入 Settings → Developer settings → Personal access tokens → Tokens (classic)
3. 点击 "Generate new token (classic)"
4. 选择权限：
   - `public_repo` - 访问公共仓库
   - `read:user` - 读取用户信息
5. 复制生成的 token

#### 设置环境变量

```bash
# 方法1：创建 .env 文件
cp .env.example .env
# 编辑 .env 文件，添加你的 token
echo "GITHUB_TOKEN=your_token_here" >> .env

# 方法2：直接设置环境变量
export GITHUB_TOKEN=your_token_here  # macOS/Linux
set GITHUB_TOKEN=your_token_here     # Windows
```

### 5. 验证安装

```bash
# 检查安装
star-summary --help

# 验证 token
star-summary validate

# 查看系统状态
star-summary status
```

## 可选依赖安装

### AI 分类功能

如果需要使用 AI 分类功能：

```bash
pip install openai>=1.3.0

# 设置 OpenAI API Key
export OPENAI_API_KEY=your_openai_key
```

### 开发依赖

如果需要进行开发：

```bash
pip install -e .[dev]
```

包含：
- pytest - 测试框架
- black - 代码格式化
- flake8 - 代码检查
- mypy - 类型检查

### 异步支持

如果需要异步 HTTP 支持：

```bash
pip install httpx>=0.25.0
```

## Docker 安装（可选）

```bash
# 构建镜像
docker build -t star-summary .

# 运行容器
docker run -e GITHUB_TOKEN=your_token_here star-summary
```

## 配置文件

默认配置文件是 `config.yaml`，你可以：

1. 使用默认配置（推荐新手）
2. 复制并修改配置：
   ```bash
   cp config.yaml my-config.yaml
   # 编辑 my-config.yaml
   star-summary generate --config my-config.yaml
   ```

## 常见问题

### Token 权限不足

**错误**：`403 Forbidden`

**解决**：确保 token 有正确的权限：
- `public_repo` - 必需
- `read:user` - 推荐

### 依赖冲突

**错误**：包版本冲突

**解决**：
```bash
# 清理环境
pip uninstall star-summary
pip install --upgrade pip

# 重新安装
pip install -e .
```

### Python 版本过低

**错误**：`SyntaxError` 或 `ImportError`

**解决**：升级到 Python 3.8+
```bash
python --version  # 检查版本
```

### 网络问题

**错误**：连接超时

**解决**：
1. 检查网络连接
2. 配置代理（如需要）
3. 增加超时时间：
   ```yaml
   # config.yaml
   github:
     timeout: 60  # 增加到60秒
   ```

## 更新

```bash
# 拉取最新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt

# 重新安装
pip install -e .
```

## 卸载

```bash
# 卸载包
pip uninstall github-star-summary

# 删除虚拟环境
deactivate
rm -rf venv

# 删除项目目录（可选）
cd ..
rm -rf star-summary
```

## 下一步

安装完成后，请参考 [使用说明](USAGE.md) 开始使用工具。
