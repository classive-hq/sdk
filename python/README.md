# Classive Python SDK

Synchronous and native asynchronous clients for the Classive Results API, on Python 3.11+.

Install the wheel from the [GitHub release](https://github.com/classive-hq/sdk/releases/tag/v0.1.0), or run `python -m pip install ./python` from a clone of [classive-hq/sdk](https://github.com/classive-hq/sdk).

```python
from classive import Classive

with Classive() as client:  # reads CLASSIVE_API_KEY from your server environment
    print(client.voices.list())
    print(client.billing.credits())
```

Use `AsyncClassive` with `async with` and `await` for asynchronous applications. All public API operations have typed resource methods; JSON dictionaries use the API's camelCase field names, and methods/options use snake_case.

See the [full SDK guide](https://github.com/classive-hq/sdk#python), [workflow examples](https://github.com/classive-hq/sdk/blob/main/docs/workflows.md), and [API reference](https://classive.app/api).

Generation is chargeable: request a quote, check it against your spending policy, then submit its `quoteId`. Mutations never retry automatically. Polling does not implicitly cancel server work. Keep API keys on your server.
