# Proyecto Pasta Loca 2

## Equipo del Proyecto

El equipo detrás de este análisis está compuesto por:

- **Francesc Pujol Contreras**: *Data Engineer*. Responsable de la limpieza de bases de datos, creación de pipelines de datos y desarrollo de librerías utilizadas por los analistas.
  
- **Maria Alba Godoy Dominguez**: *Data Scientist*. Responsable del desarrollo y optimización de los modelos predictivos.

- **Alejandro Manzano**: *Business Analyst/Data Scientist*. Responsable de realizar el análisis funcional previo del "As Is" de lo que se busca optimizar, recopilar variables externas y análisis del contexto del negocio. Desarrollo y optimización de los modelos predictivos.

## Objetivos del Proyecto

### Modelo de clasificación

Crear un modelo que nos ayude a predecir si un nuevo *cash request* (CR) va a necesitar control manual o no.  
El objetivo es optimizar el control manual y activarlo solo para casos necesarios, mejorando así la gestión de recursos.

## **"AS IS" Manual Check**

### Diagrama de Flujo del Servicio Actual

![Diagrama de flujo](Alejandro/asis/client_requests_CR.png)

### Análisis de rendimiento de los manual checks a lo largo de las semanas

![Análisis rendimiento](Alejandro/asis/as_is_manual_check.png)

#### Aclaraciones de Métricas:
- **Unique ID CR**: Cantidad total de CR.
- **Unique ID CR with moderated_at**: Cantidad de CR sometidos a control manual.
- **Unique ID CR Need Manual Check with moderated_at**: Cantidad de CR sometidos a control manual donde era necesario el control.
- **Unique ID CR Need Manual Check**: Cantidad total de CR donde era necesario control manual.

#### **Consideración Importante:**
Para nosotros, un CR lo etiquetamos como necesario de realizar control manual basados en las siguientes condiciones:
1. El estado del CR **NO ES**: "approved", "money_sent", "pending", "direct_debit_sent", "active", "money_back".
2. El estado de los *fees* **NO ES**: "confirmed", "accepted".
3. En la columna *recovery_status* **NO HAY** ningún valor.

---

### Conclusiones del Análisis

1. **Inicialmente, las líneas naranja y azul están solapadas**, lo que indica que el 100% de los CR se controlaban manualmente. Esto cambió en la **W27 2020**, donde estas líneas comenzaron a separarse, indicando que ya no se controlaban manualmente todos los CR.
2. **Crecimiento abrupto de CR desde la W36 2020**, que no fue acompañado por la línea naranja (manual check). Esto indica que se decidió reducir los niveles de control manual.
3. La **línea roja**, que representa los CR catalogados como necesarios de revisión manual, muestra un crecimiento gradual desde la **W32 2020**, coincidiendo con la aparición del nuevo servicio instantáneo. A partir de esta semana, algunos CR que deberían haberse controlado manualmente ya no lo fueron. A pesar del crecimiento de CR, los casos susceptibles a control se mantuvieron estables semana a semana.
4. **Caída abrupta en las órdenes de CR a controlar desde la W40 2020**, con un punto de inflexión en **W41 2020** donde la cantidad de CR controlados fue igual a la cantidad de CR susceptibles a control. Este desequilibrio, junto con un rendimiento de control manual por debajo del 60%, produjo un *gap* problemático (diferencia entre las líneas roja y verde).

---

### Gráficos de Apoyo

- **Gráfico de conclusión 2**:  
  Muestra el comportamiento de los CR a controlar a lo largo del tiempo.  
  ![Total CR vs Manual Check](Alejandro\asis\as_is_manual_check_vs_total.png)

- **Gráfico de conclusión 4**:  
  Analiza la relación entre el rendimiento de los manual checks y la eficiencia a lo largo de las semanas.  
  ![Análisis Manual Check](Alejandro\asis\manual_check_analysis.png)  
  ![Eficiencia vs Porcentaje](Alejandro\asis\percentage_vs_efficency.png)

---

### Problema Identificado

El crecimiento casi exponencial de los CR que debieron haber sido controlados manualmente y no lo fueron se debe a la falta de criterios claros y herramientas eficaces para seleccionar los casos a controlar. Este problema se refleja en el bajo rendimiento de los controles manuales, que estuvo por debajo del 60% debido a una falta de optimización en la gestión de recursos.

  ![CR susceptibles a problemas no controlados](Alejandro\asis\CR_no_check_and_should.png)

### Solución Propuesta

Proponemos la creación de un modelo predictivo que identifique qué casos requerirán control manual, con el objetivo de mejorar los rendimientos de control manual, llevando la eficiencia de control de un 60% a al menos un 85%.

---

### Diagrama de Flujo del Nuevo Servicio

Este modelo ayudará a identificar los casos que realmente requieren control manual, optimizando así los recursos y mejorando la eficiencia de los procesos.  
![Nuevo Diagrama de Flujo](Alejandro\asis\new_client_requests_CR.png)

---

## Conclusión

El presente proyecto tiene como objetivo optimizar el proceso de control manual de solicitudes de préstamos, abordando una problemática inicial en la que solo el 60% de las solicitudes controladas manualmente eran realmente necesarias. Esto generaba una sobrecarga operativa y un uso ineficiente de recursos. Utilizando técnicas de Data Science y Machine Learning, buscamos desarrollar un modelo predictivo basado en transacciones históricas que permita identificar de manera precisa cuáles solicitudes requieren un control manual.

Este modelo no solo reducirá la carga operativa al eliminar controles innecesarios, sino que también mejorará la eficiencia global del proceso, contribuyendo al uso óptimo de recursos humanos y tecnológicos. Como resultado, esperamos generar un impacto significativo en la toma de decisiones y en la calidad del servicio al cliente.

---

# **Modelos utilizando modelos del tipo arbol de desicion: RandomForest**

Lo primero que hacemos antes de comenzar a modelar es ver como estan divididas las lineas entre:
1) Primeras operaciones de un id_user (new_users)
2) Segundas y posteriores operaciones de un id_user (rep_users)

![Segmentacion de Dataframes](Alejandro\exploring_data\dataset_rep_vs_new.png)

Se analiza el balanceo de las clases de nuestra etiqueta para cada segmentacion:

![Balance de Clases](Alejandro\exploring_data\class_check.png)

Primero realizamos modelos trabajando con todo el dataset, no segmentando por repetitivos y/o nuevos.

## **Modelos utilizando todo el dataset sin realizar segmentaciones entre tipo de clientes**

Por mas que las clases estaban bastante balanceadas 52,31 %, se realiza el balanceo de clases para no tener sesgo a ninguna de las 2 clases.

Inicialmente hacemos un primer modelo con estas 17 caracteristicas que consideramos que pueden influir en la prediccion de nuestra etiqueta "needs_m_check". Utilizamos los hiperparametros standard del modelo RandomForest.

![Modelo Inicial](Alejandro\no_segmentation_model\all_variables_results.png)

Obtenemos los siguientes pesos de las caracteristicas, una accuracy del 97,58 % y la siguiente matriz de confusión.

![Modelo Inicial Results](Alejandro\no_segmentation_model\features_all_variables.png)


![Confusion Inicial](Alejandro\no_segmentation_model\confusion_initial.png)

Vemos que si bien el accuracy es alto y la matriz de confusión muy buena, al analizar los errores de entrenamiento y prueba obtenemos lo siguiente:

![Error de Modelo Inicial](Alejandro\no_segmentation_model\all_variables_overfitting.png)

A partir de estos resultados y para mejorar el overfitting que hemos obtenido y viendo la distribucion de pesos nos quedaremos con las top 4 variables. Estas representan el 70% del modelo inical y son:

1) n_inc_fees: Número de incidencias por fees totales del user_id
2) n_cr_fe_w: Número de operaciones (CR o fees) por semana del user_id
3) n_backs: Número de operaciones de CR totales del user_id
4) n_recovery: Número de incidencias por recovery (departamento de moras) del user_id

![Modelo Top 4 Variables](Alejandro\no_segmentation_model\features_top_4.png)

Se obtiene un error del 94,45 %, baja el accuracy, pero no demasiado simplicando el modelo de 17 caracteristicas a solo 4.

![Modelo Top 4 Result](Alejandro\no_segmentation_model\top_4_model_results.png)

Y las siguientes curvas de error, se ve que hemos reducido bastante el overfitting:

![Modelo Top 4 Error](Alejandro\no_segmentation_model\top_4_error.png)

A continuación para refinar nuestro modelo hacemos una busqueda de los hiperparametros optimos:

-    'n_estimators': Número de árboles
-    'min_samples_split': Mínimas muestras para dividir un nodo
-    'min_samples_leaf': Mínimas muestras en una hoja
-    'max_features': Número máximo de características para cada división
-    'class_weight': Peso para manejar desbalanceo
-    'criterion': Criterio para medir la calidad de las divisiones   


utilizando la funcion utilizando una validacion cruzada de 10 pliegues utilizando la funcion "GridSearchCV" de la libreria sklearn.

Consideramos como los mejores modelos los que tengan mayor accuracy mas alto y diferencia entre errores de entrenamiento y prueba mas chico (overfitting gap) para asi evitar el sobreajuste.

Los resultos obtenidos fueron:

-    'n_estimators': 50
-    'min_samples_split': 5
-    'min_samples_leaf': 2
-    'max_features': sqrt
-    'class_weight': balanced
-    'criterion': entropy  

Dejamos la profundidad maxima y la seleccion del optimo para evaluar con un grafico de boxplots para comparar profundidades graficamente.

Evaluamos nuevamente el modelo con la seleccion de los hiperparametros optimos encontrados. Se encuentran los siguientes resultados:

![Modelo Top 4 Hyperparameters Variables](Alejandro\no_segmentation_model\top_4_features_hyper_final.png)

![Modelo Top 4 Hyperparameters Results](Alejandro\\no_segmentation_model\top_4_results_hyper.png)

![Modelo Top 4 Hyperparameters Error](Alejandro\no_segmentation_model\top_4_hyper_error.png)


Realizamos el analisis de la profundidad maxima del modelo en funcion a un grafico de boxplots y se obtiene lo siguiente:

![Modelo Top 4 Hyperparameters Max Depth](Alejandro\no_segmentation_model\top_4_hyper_boxplots.png)

Se puede observar que el optimo de la profundiad es 10.

Modificamos este hiperparametro y calculamos otra vez el modelo con los siguientes hiperparametros:

-    'n_estimators': 50
-    'min_samples_split': 5
-    'min_samples_leaf': 2
-    'max_features': sqrt
-    'class_weight': balanced
-    'criterion': entropy
-    'max_depth: 10

Se obtienen los siguientes resultados:

![Modelo Top 4 Hyperparameters Final Variables](Alejandro\no_segmentation_model\top_4_features_hyper_final.png)

![Modelo Top 4 Hyperparameters Final Results](Alejandro\no_segmentation_model\top_4_results_hyper_final.png)

![Modelo Top 4 Hyperparameters Final Error](Alejandro\no_segmentation_model\top_4_hyper_final_error.png)


## **Modelos segmentando los clientes repetitivos**

Al segmentar el dataframe para los clientes repetitivos se sigue el mismo proceso, y se hace un primer modelo utilizando todas las variables y los hiperparametros standard del modelo de RF:


![Modelo ALL variables Repeat Variables](Alejandro\repeat_model\repet_all_features.png)


![Modelo ALL variables Repeat Results](Alejandro\repeat_model\repeat_all_variables_results.png)


![Modelo ALL variables Repeat Results Error](Alejandro\repeat_model\repet_all_features_error.png)

Vemos que el modelo esta sobreajustado

Como hicimos con el otro dataset nos quedamos con el top 4 columnas que representan el 70% del peso:

Obtenemos los siguientes resultados

![Modelo Top 4 Repeat Variables](Alejandro\repeat_model\repet_top_4.png)

![Modelo Top 4 Repeat Results](Alejandro\repeat_model\repeat_top_4_results.png)

![Modelo Top 4 Repeat Confusion](Alejandro\repeat_model\repet_top_4_confusion.png)

![Modelo Top 4 Repeat Results Error](Alejandro\repeat_model\repeat_top_4_error.png)


Procedemos a realizando la busqueda de los hiperparametros optimos para nuestro modelo utilizando validación cruzada, dejando para posterior analisis grafico la profundidad. Los hiperparametros optimos hallados para este modelo fueron:

-    'n_estimators': 50
-    'min_samples_split': 5
-    'min_samples_leaf': 4
-    'max_features': log2
-    'class_weight': None
-    'criterion': gini
-    'max_depth: ¿?

Realizamos el grafico de boxplots para analizar diferentes profunidades y analizar graficamente cual es el optimo:

![Modelo Top 4 Repeat Results Boxplots](Alejandro\repeat_model\repeat_top_4_hyper_boxplots.png)


Elegimos como la optima la profundidad de 10. Modificamos este parámetro y vemos los resultados finales de nuestro modelo.

![Modelo Top 4 Repeat Variables](Alejandro\repeat_model\repet_top_4_final.png)

![Modelo Top 4 Repeat Results](Alejandro\repeat_model\repeat_top_4_results_final.png)

![Modelo Top 4 Repeat Confusion](Alejandro\repeat_model\repet_top_4_confusion_final.png)

![Modelo Top 4 Repeat Results Error](Alejandro\repeat_model\repeat_top_4_error_final.png)


Como se puede observar el rendimiento del modelo baja un poco considerando solo la informacion de clientes repetitivos, las primeras transacciones de nuevos clientes nos proporciona informacion valiosa para nuestros modelos, ademas de contar con un dataframe mas grande y robusto para que estos modelos se optimizen mejor.



