import pkgutil, os, importlib

for i, mod in enumerate(pkgutil.iter_modules([os.path.dirname(__file__)])):
    importlib.import_module(__name__ + '.' + mod.name)
# 这里是抄E佬的，我也不知道是什么东西，写了能加载上就行
