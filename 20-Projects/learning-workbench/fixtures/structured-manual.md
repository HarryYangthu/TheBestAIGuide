# DEMO-FAN manual

All equipment names and measurements in this file are constructed teaching data.

## Version 1 inspection

Only after power is disconnected, inspect the cooling fan. The temperature limit is 70 C.

| Device | Limit | Unit |
| --- | --- | --- |
| DEMO-A | 70 | C |
| DEMO-B | 65 | C |

```python
# A fenced block must not be split into unrelated retrieval chunks.
if power_disconnected:
    inspect_fan()
```

The table is not permission to touch a running fan; the preceding safety condition applies.

## Version 2 inspection

Version 2 changes the DEMO-A limit to 68 C; do not mix version 1 and version 2 limits.
