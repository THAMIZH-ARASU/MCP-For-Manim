# Manim Control Protocol (MCP)

A FastMCP-based tool for executing Manim animations through a server interface. This project provides a convenient way to generate mathematical animations using Manim through a controlled protocol.

## Features

- Execute Manim code through a FastMCP server
- Automatic temporary directory management
- Cleanup utilities for generated files
- Environment variable configuration support

## Prerequisites

- Python 3.x
- Manim installation
- FastMCP

## Installation

1. Clone this repository:
```bash
git clone [your-repository-url]
cd MCP_for_Manim
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Manim:
   - Install Manim following the [official installation guide](https://docs.manim.community/en/stable/installation.html)
   - Optionally, set the `MANIM_EXECUTABLE` environment variable to point to your Manim installation

## Configuration

The project uses the following environment variables:

- `MANIM_EXECUTABLE`: Path to the Manim executable (defaults to "manim" if not set)

## Usage

1. Start the MCP server:
```bash
python main.py
```

2. The server provides two main tools:

   - `execute_manim_code(manim_code: str)`: Executes Manim code and generates animations
   - `cleanup_manim_temp_dir(directory: str)`: Cleans up temporary directories after execution

### Example

```python
# Example Manim code
manim_code = """
from manim import *

class SquareToCircle(Scene):
    def construct(self):
        circle = Circle()
        circle.set_fill(BLUE, opacity=0.5)
        self.play(Create(circle))
"""

# Execute the code
result = execute_manim_code(manim_code)
```

## Directory Structure

- `media/`: Base directory for generated animations
- `media/manim_tmp/`: Temporary directory for Manim execution

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Your chosen license]

## Acknowledgments

- [Manim Community](https://docs.manim.community/)
- [FastMCP](https://github.com/fastmcp/fastmcp)
