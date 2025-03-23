# Bond MCP Server

A lightweight, fast-deploy server for China bond market data integration, leveraging AkShare and MCP framework.

## Features

- 📈 Integration with AkShare for financial data.
- 🛠️ Easy setup with [uv](https://github.com/astral-sh/uv) for Python environment management.
- ⚡ Simple configuration to use in MCP client.

---

## Development Setup

### Prerequisites

- macOS / Linux system (or Windows with WSL)
- Homebrew installed (for macOS users)

### Steps

1. **Install `uv` package manager**

```bash
brew install uv
```

2. **Initialize project environment**

```bash
uv init bond-mcp-server
```

3. **Add project dependencies**

```bash
uv add akshare "mcp[cli]"
```

---

## Project Usage

### 1. Clone the repository

```bash
git clone git@github.com:pangahn/bond-mcp-server.git
cd bond-mcp-server
```

### 2. Sync dependencies

```bash
uv sync
```

This will install all required dependencies defined in the project.

---

### 3. Configure MCP Client

Add the following configuration to your MCP client config file:

```json
{
  "mcpServers": {
    "china-bond": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/bond-mcp-server",
        "run",
        "server.py"
      ],
      "disabled": false,
      "alwaysAllow": []
    }
  }
}
```

> 🔔 **Note:** Replace `/path/to/bond-mcp-server` with the actual path where you cloned the project.

---

### 4. Use in MCP Client

Once configured, simply start the MCP client. The `china-bond` server will automatically launch and be available for use within the client environment.

---

## Additional Notes

- To update or add new packages:

```bash
uv add <package-name>
uv sync
```

- To remove a package:

```bash
uv remove <package-name>
uv sync
```

- Check available `uv` commands:

```bash
uv --help
```

---

## License

MIT License

---

**Would you like me to include example usage of how to query data from the server in the client as well?**