# photobooth

## Comment démarrer ?

```bash
poetry install
poetry run photobooth --window
```


## Hacking

Résolution possible pour la camera

* '160.0x120.0'
* '176.0x144.0'
* '320.0x180.0'
* '480.0x270.0'
* '320.0x240.0'
* '424.0x240.0'
* '340.0x340.0'
* '352.0x288.0'
* '640.0x360.0'
* '800.0x448.0'
* '440.0x440.0'
* '640.0x480.0'
* '848.0x480.0'
* '800.0x600.0'
* '960.0x540.0'
* '1024.0x576.0'
* '1280.0x720.0'
* '1600.0x896.0'
* '1920.0x1080.0'
* '2560.0x1440.0'
* '3840.0x2160.0'
* '4096.0x2160.0'

Pour connaitre les resolution possible:

```bash
python testres.py
```

Prochaine feature (creation d'un acces point)
    * portage sur rapsberry pi
    * https://github.com/Goblenus/pyaccesspoint
