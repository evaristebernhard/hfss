#!/usr/bin/env bash
set -euo pipefail

# Find the virtual environment created by pyaedt_installer_from_aedt.py.
shopt -s nullglob
candidates=(
  /mnt/c/Users/*/AppData/Roaming/.pyaedt_env/*/Scripts/python.exe
  /mnt/c/Users/*/AppData/Local/.pyaedt_env/*/Scripts/python.exe
)

windows_python=""
for candidate in "${candidates[@]}"; do
  if [[ -f "$candidate" ]]; then
    windows_python="$candidate"
    break
  fi
done

if [[ -z "$windows_python" ]]; then
  echo "找不到 Windows PyAEDT 虚拟环境。" >&2
  echo "期望位置：C:\\Users\\<用户名>\\AppData\\Roaming\\.pyaedt_env\\<版本>\\Scripts\\python.exe" >&2
  exit 2
fi

if [[ "${1:-}" == "--check" ]]; then
  exec "$windows_python" -c 'import sys; import ansys.aedt.core as aedt; print("Python:", sys.executable); print("PyAEDT:", getattr(aedt, "__version__", "unknown"))'
fi

if [[ "${1:-}" == "--hfss-smoke" ]]; then
  shift
  script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
  exec "$windows_python" "$(wslpath -w "$script_dir/hfss_wsl_smoketest.py")" "$@"
fi

if [[ "${1:-}" == "--hfss-gui-demo" ]]; then
  shift
  script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
  exec "$windows_python" "$(wslpath -w "$script_dir/hfss_gui_draw_demo.py")" "$@"
fi

if [[ $# -lt 1 ]]; then
  echo "用法：" >&2
  echo "  $0 --check" >&2
  echo "  $0 --hfss-smoke" >&2
  echo "  $0 --hfss-gui-demo" >&2
  echo "  $0 path/to/your_script.py [参数...]" >&2
  exit 64
fi

script_path="$1"
shift
if [[ "$script_path" == /* ]]; then
  windows_script="$(wslpath -w "$script_path")"
else
  windows_script="$(wslpath -w "$(pwd)/$script_path")"
fi

exec "$windows_python" "$windows_script" "$@"
