
# HSpicePy

Bilgisayarınıza PATH değişkenlerine eklediğiniz HSPICE programını python ile çalıştırmanızı sağlayan basit bir araç.


A simple tool that allows you to run the HSPICE program that you add to the PATH variables on your computer with python.
# Usage/Examples

## HSPICE Simulating
```python
from hspicpy import HSpicePy

meAbsPath = os.path.dirname(os.path.realpath(__file__))
h = HSpicePy(file_name="amp",design_file_name="designparam",path=meAbsPath)
h.run()
```

## Asynchronous HSPICE Simulating

Simülasyonların arkaplanda çalışmasını istiyorsanız bu yöntemi kullanmalısınız.

You should use this method if you want the simulations to run in the background.
```python
from hspicpy import HSpicePy
import asyncio

meAbsPath = os.path.dirname(os.path.realpath(__file__))
h = HSpicePy(file_name="your_sp_file",design_file_name="your_cir_file",path=meAbsPath)
asyncio.run(h.run_async())
```

Simulasyon çalıştırıldıktan sonra projenizin bulunduğu dizinde "out" klasörü oluşacaktır.
Simulasyon sonuçları bu klasöre kaydedilecektir.

Sadece bir adet .sp ve .cir dosyası girişte parametre olarak vermelisiniz.

After the simulation is run, an "out" folder will be created in the directory where your project is located.
The simulation results will be saved in this folder.

You must provide only one .sp and .cir file as parameters at the entrance.

## Results
```python
from hspicpy import HSpicePy
import asyncio

meAbsPath = os.path.dirname(os.path.realpath(__file__))
h = HSpicePy(file_name="your_sp_file",design_file_name="your_cir_file",path=meAbsPath)
asyncio.run(h.run_async())

print(h.result)
print(h.operation_point_result)

```

Simulasyon sonuçlarını .json olarak out klasöründe bulabilirsiniz.

You can find operation point result and measure result which are saved json file format in "out" folder 

## Change Parameters on .cir File


```
//old
//my_parameters.cir

.PARAM
+ R1 = 8000
+ LM2 = 4.272405486964919e-06
+ LM3 = 5.066472271942056e-06
```


```python
from hspicpy import HSpicePy
import asyncio

meAbsPath = os.path.dirname(os.path.realpath(__file__))
h = HSpicePy(file_name="amp",design_file_name="designparam",path=meAbsPath,timeout="")
h.change_parameters_to_cir(R1 = 12000, LM2 = 6.272405486964919e-06, LM3 = 7.272405486964919e-06)

asyncio.run(h.run_async())

print(h.result)
print(h.operation_point_result)

```

```
//new
//my_parameters.cir

.PARAM
+ R1 = 12000
+ LM2 = 6.272405486964919e-06
+ LM3 = 7.272405486964919e-06
```


## Authors

- [@ubeydtalha](https://github.com/ubeydtalha)

