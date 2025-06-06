import asyncio
import json
from fastmcp import Client


async def check_status():
    url = "http://127.0.0.1:8888/mcp/"  # Default URL
    tool_name = "mcp_diagnostics"

    print(
        f"Attempting to connect to MCP server at {url} to call tool '"
        f"{tool_name}'..."
    )

    try:
        async with Client(url) as client:
            print(f"Successfully connected. Calling tool: {tool_name}...")
            result = await client.call_tool(tool_name)

            if result and isinstance(result, list) and len(result) > 0:
                # Assuming the actual content is in the 'text' attribute of the first element
                # which is typical for FastMCP when result is simple text/json
                if hasattr(result[0], 'text'):
                    diagnostics_output_str = result[0].text
                    try:
                        # Attempt to parse as JSON for pretty printing
                        diagnostics_output_json = json.loads(
                            diagnostics_output_str
                        )
                        print("Diagnostics Result (JSON):")
                        print(
                            json.dumps(
                                diagnostics_output_json,
                                indent=2,
                                ensure_ascii=False
                            )
                        )
                    except json.JSONDecodeError:
                        # If not JSON, print as raw text
                        print("Diagnostics Result (Raw Text):")
                        print(diagnostics_output_str)
                else:
                    # Fallback if structure is different
                    print("Diagnostics Result (Raw Object):")
                    print(result)
            else:
                print("No result or empty result received from the tool.")

    except ConnectionRefusedError:
        print(
            f"Error: Connection to {url} was refused. Is the server running?"
        )
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(check_status()) 