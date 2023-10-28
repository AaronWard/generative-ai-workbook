'''
Utility functions

'''


def is_termination_message( x):
    return x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE")