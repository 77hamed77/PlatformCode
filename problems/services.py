# problems/services.py

from RestrictedPython import compile_restricted
from RestrictedPython.Guards import safe_builtins, full_write_guard, guarded_iter_unpack_sequence
import io
import sys
from .models import Submission

class JudgingService:
    """
    Encapsulates all code execution logic.
    Uses RestrictedPython to safely execute user-submitted code in a sandbox.
    """
    
    @staticmethod
    def _safe_execute(user_code, test_input):
        """Executes user code in a sandboxed environment."""
        restricted_globals = {'__builtins__': safe_builtins}
        restricted_locals = {
            '_write_': full_write_guard,
            '_getiter_': guarded_iter_unpack_sequence,
            '_unpack_sequence_': guarded_iter_unpack_sequence,
        }
        
        old_stdout, sys.stdout = sys.stdout, io.StringIO()
        old_stdin, sys.stdin = sys.stdin, io.StringIO(str(test_input))
        
        output, status, error_message = "", "Error", ""

        try:
            byte_code = compile_restricted(user_code, '<string>', 'exec')
            exec(byte_code, restricted_globals, restricted_locals)
            status = "Success"
        except Exception as e:
            error_message = f"Runtime Error: {type(e).__name__} ({e})"
        finally:
            output = sys.stdout.getvalue().strip()
            sys.stdout = old_stdout
            sys.stdin = old_stdin

        return output, status, error_message

    @classmethod
    def judge_submission(cls, problem, student, code):
        """
        Judges a user's code against all test cases for a problem.
        
        1. FIX (Efficiency): This method now expects `problem.test_cases` to be pre-fetched
           by the caller (the view), avoiding an extra database query here.
        """
        final_status = Submission.Status.CORRECT

        # This will use the pre-fetched test cases, not hit the DB again.
        for test_case in problem.test_cases.all():
            actual_output, exec_status, _ = cls._safe_execute(code, test_case.input_data)
            
            if exec_status != "Success" or actual_output != test_case.expected_output.strip():
                final_status = Submission.Status.ERROR if exec_status != 'Success' else Submission.Status.WRONG
                break

        submission = Submission.objects.create(
            problem=problem,
            student=student,
            submitted_code=code,
            status=final_status
        )
        return submission