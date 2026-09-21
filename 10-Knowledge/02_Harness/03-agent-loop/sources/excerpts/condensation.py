        _messages_or_condensation = prepare_llm_messages(
            state.view, condenser=self.condenser, llm=self.llm
        )

        # Process condensation event before agent sampels another action
        if isinstance(_messages_or_condensation, Condensation):
            on_event(_messages_or_condensation)
            return
