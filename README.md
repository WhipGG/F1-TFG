# TFG - Prediccion de resultados de Fórmula 1

Autor: Manuel Ventura

En este resposito se aloja el código creado durante la realización del TFG de predicción de resultados de Fórmula 1. A continuación se exponen los contenidos de cada carpeta del repositorio y los requisitos para ejecurar.


## Carpeta *f1tfgapp*

Proyecto *Django* para el desarrollo de la aplicación web que permita realizar predicciones y visualizar datos correspondientes a las carreras. Las carpetas y archivos del proyecto son:

 - **f1dataapp**: aplicación web. Los archivos que contiene son:
    - **data_ready**: carpeta que aloja datasets de entrenamiento para poder reentrenar la red neuronal después de cada carrrera.
    - **f1cache**: carpeta que aloja datos de telemetría de cada carrera.
    - **f1db_csv**: carpeta que aloja la base de datos de [Ergast API](http://ergast.com/mrd/) en formato `csv`. Se puede actualizar después de cada carrera.
    - **migrations**: carpeta de Django para controlar los cambios de la base de datos.
    - **models**: carpeta que aloja los archivos que contienen la red neuronal.
    - **static**: carpeta que aloja los archivos de estilos de la web.
    - **templates**: carpeta que aloja los archivos `html` de la web.
    - **`admin.py`**, **`apps.py`**, **`tests.py`**, **`urls.py`**, **`views.py`**: archivos Django que gestionan el funcionamiento de la aplicación.
    - **`charts.py`**: script que crea las gráficas para mostrar datos.
    - **`forms.py`**: archivo que gestiona los formularios web.
    - **`models.py`**: archivo Django que gestiona la base de datos.
    - **`populateDB.py`**: archivo que carga los datos iniciales en la DB. Se cargan datos de pilotos, constructores y circuitos.
    - **`predictions.py`**: script que genera predicciones.
    - **`update_ergast.py`**: script que actualiza la copia de la base de datos de Ergast en la carpeta `f1db_csv`.
 - **f1tfgapp**: carpeta para gestionar el proyecto creada por Django, contiene los ajustes del proyecto. y se utiliza para cambiar los mismos y añadir las diferentes aplicaciones (en nuestro caso solo hay una).
 - **media**: carpeta para alojar las imágenes que se carguen en las bases de datos del proyecto, se ha configurado en `f1tfgapp/settings.py`.
 - **templates**: modificaciones de los templates de Django para la interfaz del administrador de la web.
 - **`db.sqlite3`**: base de datos utilizada durante el desarrollo del proyecto.
 - **`manage.py`**: archivo creado por Django que ejecuta el servidor web y los diferentes comandos del proyecto.


Para poder activar el proyecto, es necesario tener instalados todos los paquetes descritos en la sección de [requisitos](#requisitos-necesarios) excepto `LightGBM` y `XGBoost`. Una vex estén satisfechos los requisitos, abrimos una consola en la carpeta que contiene el archivo `manage.py` y ejecutamos el comando "`python manage.py runserver`".


## Carpeta *notebooks*

En esta carpeta se incluyen los notebooks jupyter utilizados para llevar a cabo la parte de Machine Learning del trabajo.

 - **TFG - tratamiento_datos**: transformaciones de los datos en bruto para obtener el dataset de entrenamiento.
 - **TFG - Data Analysis**: análisis de los datos e importancia de los diferentes atributos.
 - **TFG - Modelling - Classic AI**: modelado con técnicas de IA clásicas utilizando el dataset con la codificación one-hot.
 - **TFG - Modelling - Classic AI - DF Normal**: modelado con técnicas de IA clásicas utilizando el dataset con las labels sin codificar.
 - **TFG_ML_Regression**: entrenar modelo de NN de regresión.
 - **TFG_ML_Clasificación_No_Lookup**: entrenar modelo de NN de clasificación.
 - **TFG_ML_Clasificación_With_Lookup**: entrenar modelo de NN de clasificación con capa de *lookup*.
 - **TFG_Save_Embeddings**: obtener archivos con los embeddings de los modelos.
 - **TFG_Save_Embeddings_Lookup**: obtener archivos con los embeddings del modelo con lookup.
 - **TFG - NN Ranking Test**: test de la capacidad de predecir ranking de los modelos NN obtenidos.

Los archivos *TFG_ML* y *TFG_Save_Embeddings* se han ejecutado en [Google Colab](https://colab.research.google.com/) para realizar el entrenamiento de la red neuronal utilizando tarjetas gráficas.

Las carpetas que contienen los archivos para ejecutar los notebooks anteriores son:

 - **f1db_csv**: archivos para crear el dataset de entrenamiento
 - **data_ready**: datasets de entrenamiento y datos necesarios de la parrilla actual para poder realizar futuras predicciones.
 - **models**: modelos obtenidos.
 - **saved_embeddings**: los embeddings obtenidos de los diferentes modelos. Los archivos *vectors* contienen los vectores y los archivos *metadata* contienen el nombre correspondientes a cada vector. Hay embeddings obtenidos de 3 modelos:
   - Los archivos que no tienen nada añadido en su nombre corresponden al modelo de regresión.
   - Los archivos con *cat* en su nombre corresponden al modelo de clasificación con lookup.
   - Los archivos con *cat_nolookup* en su nombre corresponden al modelo de clasificación sin capa de lookup.


## Requisitos necesarios

Para poder ejecutar los archivos en este repositorio se necesitan los siguientes paquetes de Python:
 - Numpy  (`pip install numpy`)
 - Pandas  (`pip install pandas`)
 - Requests  (`pip install requests`)
 - Selenium  (`pip install selenium`)
 - MatplotLib  (`pip install matplotlib`)
 - Seaborn  (`pip install seaborn`)
 - Tensorflow  (https://www.tensorflow.org/install)
 - scikit-learn  (https://www.tensorflow.org/install)
 - LightGBM  (`pip install lightgbm`)
 - XGBoost  (`pip install xgboost`)
 - SciPy  (`pip install scipy`)
 - Joblib  (`pip install joblib`)
 - Django  (`pip install Django`)
 - FastF1  (`pip install fastf1`)

La mayoría pueden ser obtenidos con una instalación de [Anaconda](https://www.anaconda.com/) y los que no se tengan se obtienen intalandolos a traves del gestos de paquetes [PyPI](https://pypi.org/project/pip/)