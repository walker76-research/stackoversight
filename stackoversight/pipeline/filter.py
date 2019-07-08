from astformer import ASTFStatus, ASTFormer
from pipeline.processing_step import ProcessingStep


class Filter(ProcessingStep):
    """
    Input for Pipeline - An array of arrays of code snippet strings
    Output for Pipeline - An array of arrays of code snippet strings
    """
    def operation(self, item):
        """
        Returns a code snippet that can actually be compiled. Sanitizes more as needed. None if not
        """
        filtered = ASTFormer(item)
        if filtered.status == ASTFStatus.SUCCESS:
            return filtered.code
        else:
            return None
