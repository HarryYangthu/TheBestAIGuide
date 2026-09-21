# 通信与交接实验

| 场景 | 实际决定 | 通过 |
|---|---|---|
| failure_reported | accepted_failure | True |
| incomplete_after_failure | False | True |
| retry_result | accepted_result | True |
| duplicate_result | duplicate | True |
| same_id_changed | conflicting_message | True |
| late_attempt | stale_attempt | True |
| late_started | late_progress | True |
| wrong_correlation | wrong_correlation | True |
| old_input | stale_input | True |
| new_id_same_result | duplicate_outcome | True |
| new_id_conflicting_result | conflicting_outcome | True |
| duplicate_request_reply | duplicate | True |
| worker_execution_count | 2 | True |
| merged_shortage | 1 | True |
| offer_keeps_owner | coordinator | True |
| handoff_owner | fulfillment-specialist | True |
| handoff_epoch | 2 | True |
| old_owner_rejected | rejected_stale_owner | True |
| new_owner_acts | draft_created | True |
