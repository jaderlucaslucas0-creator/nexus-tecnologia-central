import os
import platform
import shutil

def get_system_status():
    disk = shutil.disk_usage(os.getcwd())
    return {'os': platform.system(), 'version': platform.version(), 'architecture': platform.machine(), 'python': platform.python_version(), 'cpu_count': os.cpu_count() or 0, 'disk_free_gb': round(disk.free / (1024**3), 2)}