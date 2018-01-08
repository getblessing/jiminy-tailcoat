import pyblish.api
import datetime


class CollectCurrentTime(pyblish.api.ContextPlugin):
    """Inject the real world profile into context

    ```
    context.data {
            time:       data time
    }
    ```

    """
    label = "Get Time"
    order = pyblish.api.CollectorOrder - 0.499

    def process(self, context):
        context.data.update(
            {
                "time": datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ"),
            }
        )
