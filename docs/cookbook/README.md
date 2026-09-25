# Un dominio diverso

Il compilatore riceve un catalogo dal chiamante, senza importare la stdlib:

```python
from locus.compiler import compile_source
from locus.runtime import instantiate

program = compile_source("Il sensore è un dispositivo.", {"dispositivo": "lab.device"})
world = instantiate(program)
assert world.entities[0].type_id == "lab.device"
```

Questo non implementa una simulazione: dimostra il confine fra sintassi e dominio.
Il caso è coperto da test di integrazione.
