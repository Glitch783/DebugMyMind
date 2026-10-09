import io
import sys
import time
import threading
import traceback
from RestrictedPython import compile_restricted
from RestrictedPython.Guards import (
    guarded_iter_unpack_sequence,
    safe_builtins,
    guarded_iter
)
from RestrictedPython.Eval import (
    default_guarded_getattr,
    default_guarded_getitem
)

class TimeoutException(BaseException):
    """Custom exception raised when the student code execution exceeds the timeout limit."""
    pass

def safe_write(obj):
    """Allow attribute writing for standard objects in RestrictedPython."""
    return obj

def execute_code(code_str: str, timeout: float = 5.0) -> dict:
    """
    Safely executes the provided Python code string in a sandboxed environment.
    Applies a execution timeout limit using sys.settrace.
    
    Returns a dictionary containing:
        - error_type: Name of the raised exception (if any)
        - error_message: Text of the raised exception (if any)
        - line_number: The line number where the exception occurred (if any)
        - stdout: Collected standard output
        - stderr: Collected standard error
        - traceback: Cleaned traceback string (if any)
    """
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()

    # Compile the code restrictedly
    try:
        compiled_code = compile_restricted(code_str, filename='<student_code>', mode='exec')
    except Exception as e:
        tb = traceback.format_exc()
        return {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "line_number": getattr(e, 'lineno', None),
            "stdout": "",
            "stderr": "",
            "traceback": tb
        }

    # Setup the execution globals
    custom_builtins = safe_builtins.copy()
    
    # Custom print function that writes to stdout_buffer
    def safe_print(*args, **kwargs):
        # We redirect sys.stdout inside the thread, so print will write to it.
        # But just to be robust, we write to sys.stdout explicitly.
        print(*args, **kwargs)

    custom_builtins['print'] = safe_print
    # Include range and len (they are typically in safe_builtins, but let's be safe)
    if 'range' not in custom_builtins:
        custom_builtins['range'] = range
    if 'len' not in custom_builtins:
        custom_builtins['len'] = len

    local_globals = {
        '__builtins__': custom_builtins,
        '_getattr_': default_guarded_getattr,
        '_getitem_': default_guarded_getitem,
        '_getiter_': guarded_iter,
        '_iter_unpack_sequence_': guarded_iter_unpack_sequence,
        '_write_': safe_write,
    }

    exec_error = None
    exec_tb = None

    def target_run():
        nonlocal exec_error, exec_tb
        
        # Redirect stdout and stderr inside the executing thread
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = stdout_buffer
        sys.stderr = stderr_buffer
        
        # Set trace function to detect timeout on every line executed
        deadline = time.time() + timeout
        def tracer(frame, event, arg):
            if time.time() > deadline:
                raise TimeoutException(f"Execution timed out ({timeout} seconds limit exceeded)")
            return tracer

        sys.settrace(tracer)
        try:
            exec(compiled_code, local_globals)
        except TimeoutException as te:
            exec_error = te
            exec_tb = "TimeoutException: Execution timed out."
        except Exception as e:
            exec_error = e
            exec_tb = traceback.format_exc()
        finally:
            sys.settrace(None)
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    t = threading.Thread(target=target_run)
    t.start()
    t.join(timeout + 0.5)

    stdout_val = stdout_buffer.getvalue()
    stderr_val = stderr_buffer.getvalue()

    if t.is_alive():
        # Fallback if thread is stuck outside tracer control
        exec_error = TimeoutException(f"Execution timed out ({timeout} seconds limit exceeded)")
        exec_tb = "TimeoutException: Execution timed out."

    if exec_error:
        error_type = type(exec_error).__name__
        error_msg = str(exec_error)
        line_no = None

        # Parse line number from traceback frames
        if hasattr(exec_error, '__traceback__') and exec_error.__traceback__:
            tb_list = traceback.extract_tb(exec_error.__traceback__)
            for frame in reversed(tb_list):
                if frame.filename == '<student_code>':
                    line_no = frame.lineno
                    break

        return {
            "error_type": error_type,
            "error_message": error_msg,
            "line_number": line_no,
            "stdout": stdout_val,
            "stderr": stderr_val,
            "traceback": exec_tb
        }

    return {
        "error_type": None,
        "error_message": None,
        "line_number": None,
        "stdout": stdout_val,
        "stderr": stderr_val,
        "traceback": None
    }
