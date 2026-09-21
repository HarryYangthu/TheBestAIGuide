    if message.tool_calls:
        return LLMResponseType.TOOL_CALLS

    if any(isinstance(c, TextContent) and c.text.strip() for c in message.content):
        return LLMResponseType.CONTENT

    if (
        message.responses_reasoning_item is not None
        or message.reasoning_content is not None
        or message.thinking_blocks
    ):
        return LLMResponseType.REASONING_ONLY

    return LLMResponseType.EMPTY
