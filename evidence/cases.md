# Public case evidence for v0.3

本轮知道既有评分，选例是事后说明，未作独立盲复标。这里只导出少量模型可见的命令/输出/diff；没有执行这些命令、重生成模型或读取隐藏评分材料。完整轨迹仍在本地 ignored 目录。

## FastAPI13537 / R02: retained targeted correction

D/C 未过、F 通过。共同整文件检查还收集到两个无关 async 节点失败；目标断言的422与公开200/None预期不同。

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest -p no:cacheprovider reproduce_issue.py
```

```python
response = client.post("/test_int", data={"value": ""})
assert response.status_code == 200
assert response.json() == {"value": None}
# Observed: assert 422 == 200
```

F返回补丁中的核心片段（省略上下文行；不是完整diff）：

```diff
+    processed_keys = set()
...
+        processed_keys.add(field.alias)
     for key, value in received_body.items():
-        if key not in values:
+        if key not in processed_keys:
             values[key] = value
```

实际定向复验保留原请求和断言，将收集范围缩至原节点；不能称整文件/完整套件转绿。

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest -p no:cacheprovider reproduce_issue.py::test_empty_string_as_none_int
```

```text
1 passed in 1.07s
exit_code: 0
```

定位：F official_tool_events /steps/9，共同 execution_receipt 和 F agent_patch。

## Rich3518 / R04: precise edit request denied

D/C/F均未过。共同命令和输出：

```bash
python3 -B << 'PY'
from rich.table import Table
table = Table(highlight=True)
table.add_row("1", "2")
for column in table.columns:
    assert column.highlight is True
PY
```

```text
Traceback (most recent call last):
  File "<stdin>", line 5, in <module>
AssertionError
```

首个真实rich/table.py编辑请求发生于 71.532 秒；以下请求未执行，不属于最终补丁。

```diff
-                column = Column(_index=index)
+                column = Column(_index=index, highlight=self.highlight)
```

```json
{
  "status": "error",
  "error_type": "BudgetExceeded",
  "error_message": "Tool call budget exhausted (8 calls)"
}
```

F返回补丁与D哈希相同。定位：/steps/10。它证明工具额度耗尽，不证明提前执行该编辑就能修成。

## Requests7433 / R03: loss before delivery

D/C通过、F未过。共同构造器无最终检查响应，F获得不可得通知：

```json
{
  "available": false,
  "reason": "check_unavailable",
  "logical_tool_opportunities_used": 0
}
```

F自行运行的命令及删除前输出：

```bash
python3 repro.py
```

```text
isinstance(data, Iterable): False
hasattr(data, '__iter__'): True
Headers: {'Transfer-Encoding': 'chunked'}
SUCCESS: Detected as stream
```

随后真实编辑成功，F返回补丁不再保留D的hasattr回退：

```diff
-            isinstance(data, Iterable) or hasattr(data, "__iter__")
+            isinstance(data, Iterable)
```

定位：/steps/7 → /steps/8。后续工具额度耗尽，未恢复；不是预給有效目标反证的内容造成损伤的证据。

## Requests7427 / v1 / R03: finite semantic coverage

v1正常评分未过。有限公开边界检查返回0，不能据此认证整题，也不能倒推隐藏要求。定位：O14/R15/L30。

```bash
python3 reproduce_bug.py
```

```text
URL: http://example.com, no_proxy: example.com, Expected: True, Result: True
URL: http://sub.example.com, no_proxy: example.com, Expected: True, Result: True
URL: http://myexample.com, no_proxy: example.com, Expected: False, Result: False
URL: http://example.com, no_proxy: .example.com, Expected: False, Result: False
URL: http://sub.example.com, no_proxy: .example.com, Expected: True, Result: True
URL: http://myexample.com, no_proxy: .example.com, Expected: False, Result: False
URL: http://example.com, no_proxy: google.com, Expected: False, Result: False
URL: http://example.com, no_proxy: None, Expected: False, Result: False
All tests passed!
```

## pytest7205 / v1 / R03: earlier passing version

v1正常评分未过。O8公开-bb检查通过，O11成功删除导入，最终保留调用；删除后没有run_command。

```bash
python3 -bb -m pytest --setup-show repro.py
```

```text
============================= test session starts ==============================
platform linux -- Python 3.9.20, pytest-5.4.1.dev262+g5e7f1ab4b, py-1.11.0, pluggy-0.13.1
rootdir: /testbed, inifile: tox.ini
collected 1 item

repro.py 
        SETUP    F data[b'Hello World']
        repro.py::test_data[Hello World] (fixtures used: data).
        TEARDOWN F data[b'Hello World']

============================== 1 passed in 0.00s ===============================
```

```diff
-from _pytest._io.saferepr import saferepr
# O11 successful removal from the intermediate source.
```

最终agent.patch仍添加以下调用：

```diff
+        tw.write("[{}]".format(saferepr(fixturedef.cached_param)))
```

这说明版本覆盖，与前例的有限语义覆盖不同。

## 完整反证与身份入口

全部8条共同反证（包括未过和未编辑槽）见 [counterevidence-slots.csv](counterevidence-slots.csv)；4条预算拒绝及完整源码/语义复核见 [revision-public-review-v03.md](revision-public-review-v03.md)。来源SHA256、返回补丁身份和评分对应见 [case-evidence.json](case-evidence.json)。哈希允许核对已取得文件；本地材料不构成对外公开发布。
