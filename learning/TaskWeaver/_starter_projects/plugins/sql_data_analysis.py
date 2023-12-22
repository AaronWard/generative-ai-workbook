import pandas as pd
from taskweaver.plugin import Plugin, register_plugin, test_plugin

# Plugin definition
@register_plugin
class SQLDataAnalysis(Plugin):
    def __call__(self):
        """
        Performs a simple SQL Pull and return stats on the data.
        """
        df = pd.DataFrame({
            "A": [1, 2, 3],
            "B": ["A", "B", "C"]
        })

        row_count = len(df)
        column_count = len(df.columns)
        description = f"The data has {row_count} rows and {column_count} columns."
        return description