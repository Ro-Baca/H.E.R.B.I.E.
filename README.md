# **H.E.R.B.I.E.** <br> <span style="font-size:60%;">**H**orticultural **E**lectronic **R**obot **B**udy **I**nteractive **E**ntity</span>


> ![Logo de H.E.R.B.I.E. o la foto del robot]


[![License](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE) 


H.E.R.B.I.E. es un prototipo de robot social de código abierto, diseñado para ser una plataforma de investigación accesible en el campo de la Interacción Humano-Robot (HRI). Fue desarrollado siguiendo una metodología de Ingeniería de Sistemas para estudiar cómo la filosofía de 'Robot Débil' puede fomentar la cooperación y el acoplamiento social con los usuarios.

## Modelo
[![Modelo](https://img.shields.io/badge/Modelo-Navegación-red)](./Model/Navegador_del_modelo.pdf)

### Conceptual
Define los **actores y requerimientos de usuario** (el "Qué" y "Por qué" del sistema). 

[![Modelo]( https://img.shields.io/badge/Modelo-Conceptual-yellow)](./Model/1.%20Concept%20Level/) 


### Lógico
Describe la **estructura funcional** y las interacciones del sistema, agnósticas a la tecnología.

[![Modelo]( https://img.shields.io/badge/Modelo-Lógico-blue)](./Model/1.%20Concept%20Level/) 

### Tecnológico
Define la **arquitectura concreta**, componentes de hardware y plataformas de software específicas.

[![Modelo]( https://img.shields.io/badge/Modelo-Tecnológico-green)](Modelo) 

## Hardware
Esta sección contiene los planos de los componentes y su interconexión, esenciales para la replicabilidad.
### Circuitos
Aquí se encuentran los diagramas eléctricos y pinouts para la interconexión de sensores y actuadores.


### CAD
Archivos STL para los encapsulamientos modulares, diseñados para impresión FDM en PLA.

## Software
El software se divide en una arquitectura dual:

### Cerebro (Raspberry Pi Zero)
-   **Función:** Procesamiento de alto nivel, servidor web y base de datos.
-   **Tecnologías:** Python, Flask, SQLite.

### Controlador (Raspberry Pi Pico)
-   **Función:** Gestión de entradas/salidas (lectura de sensores y control de actuadores) en tiempo real.
-   **Tecnologías:** MicroPython.




