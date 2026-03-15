export LANG=C.UTF-8
export LC_ALL=C.UTF-8
export PYTHONIOENCODING=utf-8

# 生成 locale
if command -v locale-gen &> /dev/null; then
    locale-gen C.UTF-8 2>/dev/null || true
fi
