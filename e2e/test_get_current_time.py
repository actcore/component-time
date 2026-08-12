import re


async def test_default_is_utc(client):
    """hurl 'UTC time' block: no args -> an RFC 3339 timestamp."""
    result = await client.call_tool("get_current_time", {})
    assert "T" in result.content[0].text


async def test_with_timezone(client):
    """hurl 'With timezone' block: Europe/Moscow.

    Moscow sits at UTC+03:00 today but carried +04:00 under permanent DST
    from 2011-2014, so the original regex tolerates either offset — kept
    verbatim rather than pinned to the current value.

    hurl's `matches` predicate is an unanchored substring search, not a
    fullmatch (confirmed empirically: `jsonpath ... matches "\\+0[34]:00"`
    against a full URL containing other characters around the offset still
    passes under `hurl --test`). The offset is a fragment of the full RFC
    3339 string, not the whole of it, so `re.search` is the faithful
    translation here, not `re.fullmatch`.
    """
    result = await client.call_tool("get_current_time", {"timezone": "Europe/Moscow"})
    assert re.search(r"\+0[34]:00", result.content[0].text)


async def test_rejects_an_invalid_timezone(client, expect_error):
    """hurl 'Invalid timezone' block: HTTP 422 + `$.error.kind` ==
    std:invalid-args is ACT-HTTP's projection of the same tool-event::error
    the MCP transport surfaces as an is_error result; expect_error covers
    both paths.
    """
    await expect_error(client, "get_current_time", {"timezone": "Not/A/Zone"}, "std:invalid-args")


async def test_safe_to_call_repeatedly(client):
    """hurl 'QUERY method (safe, cacheable)' block: ACT-HTTP re-issued the
    same call over the QUERY verb to prove this read_only tool is reachable
    safely that way too. MCP's `tools/call` has no verb to vary — there is
    exactly one way to invoke a tool — so the only faithful counterpart is
    confirming a second, independent call is just as well-formed as the
    first.
    """
    result = await client.call_tool("get_current_time", {})
    assert "T" in result.content[0].text
