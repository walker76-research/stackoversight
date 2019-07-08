from pipeline.processing_step import ProcessingStep
from sanitizecode import SanitizeCode


class Sanitizer(ProcessingStep):
    """
    Input for Pipeline - An array of arrays of code snippet strings
    Output for Pipeline - An array of arrays of code snippet strings
    """
    def operation(self, item):
        """
        Returns a code snippet that is cleaned from comments/plaintext/bad indentation
        """
        sc = SanitizeCode(item)
        sc.remove_plaintext()
        sc.remove_comments()
        sc.remove_false_indents()
        return filter(None, sc.code)
