# problems/services.py

# 1. CRITICAL FIX: Import tools for sandboxing
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
        """
        Executes user code in a sandboxed environment.
        This prevents access to the filesystem, database, and other sensitive operations.
        """
        # Define allowed built-in functions. `print`, `int`, `str`, etc., are safe.
        restricted_globals = {'__builtins__': safe_builtins}
        
        # Define security guards
        restricted_locals = {
            '_write_': full_write_guard,  # Prevents writing to unauthorized attributes
            '_getiter_': guarded_iter_unpack_sequence, # Safely handles iteration
            '_unpack_sequence_': guarded_iter_unpack_sequence,
        }
        
        # Redirect stdout and stdin
        old_stdout, sys.stdout = sys.stdout, io.StringIO()
        old_stdin, sys.stdin = sys.stdin, io.StringIO(str(test_input)) # Ensure input is a string
        
        output, status, error_message = "", "Error", ""

        try:
            # 2. CRITICAL FIX: Compile the code in restricted mode first.
            # This fails early if the code contains forbidden syntax (like `import os`).
            byte_code = compile_restricted(user_code, '<string>', 'exec')
            
            # Execute the compiled bytecode with restricted globals and locals.
            exec(byte_code, restricted_globals, restricted_locals)
            
            status = "Success"
        except SyntaxError as e:
            error_message = f"Syntax Error: {e}"
        except Exception as e:
            # Catch any other runtime errors that might occur
            error_message = f"Runtime Error: {type(e).__name__} - {e}"
        finally:
            output = sys.stdout.getvalue().strip()
            # Always restore stdout and stdin
            sys.stdout = old_stdout
            sys.stdin = old_stdin

        return output, status, error_message

    @classmethod
    def judge_submission(cls, problem, student, code):
        """
        Judges a user's code against all test cases for a problem.
        Creates a Submission object with the final result.
        Returns the created Submission object.
        """
        final_status = Submission.Status.CORRECT

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