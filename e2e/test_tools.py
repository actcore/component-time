async def test_component_exposes_its_tools(client):
    """hurl tools.hurl: `$.tools` count >= 1."""
    tools = await client.list_tools()
    assert len(tools) >= 1


async def test_lists_exactly_get_current_time(client):
    """hurl list_tools.hurl: exact count and name — time exposes exactly one tool."""
    tools = await client.list_tools()
    assert len(tools) == 1
    assert tools[0].name == "get_current_time"
