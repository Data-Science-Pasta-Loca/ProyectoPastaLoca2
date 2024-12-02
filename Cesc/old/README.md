# ProyectoPastaLoca
Proyecto Pasta Loca

# OBJETIVO DEL PROYECTO
- Analisis avanzado de insights y cohortes
- Segmentacion de datos exhaustiva
- Analizar cohortes de usuarios relevantes (definidads segun el periodo en que realizaron su primer adelanto de efectivo)>Primera "created_at" de cada user_id

# ALCANCE DEL PROYECTO
- Generar modelos de regresión y clasificación para proporcionar a BP tener valiosas perspectivas sobre el comportamiento de los usuarios y el rendimiento de sus servicios financieros.

# DIAGRAMA DE FLUJO DEL SERVICIO

(link al diagrama de flujo definitivo)


# METRICAS PARA ANALIZAR RENTABILIDAD FINANCIERA DE BP

- Margen de ingreso por fees = (ingresos por fees de adelanto + ingresos por fees de prorrogas) / total adelantos * 100

- Porcentaje de adelantos con fee = adelantos con fee / total adelantos * 100

# METRICAS PARA ANALIZAR COMPORTAMIENTO DE CLIENTES DE BP

- Porcentaje de clientes repetitivos: Clientes repetitivos / Total de Clientes * 100

- Porcentaje de nuevos clientes que pagan fees=  Clientes nuevos que pagan fees / Total de clientes nuevos * 100
  
- Porcentaje de clientes repetitivos que pagan fees=  Clientes repetitivos que pagan fees / Total de clientes repetitivos * 100

- Tasa de incumplimiento nuevos clientes: (Clientes nuevos que no cumplen el plazo / Total de clientes nuevos) * 100

- Tasa de incumplimiento clientes repetitivos: (Clientes repetitivos que no cumplen el plazo / Total de clientes repetitivos) * 100

---

## Estructura de los datos

### Cash_Request

#### CR campo: status (23970 regs)

-**money_back** :           (16397) The CR was successfully reimbursed.

-**rejected** :             (6568 regs) The CR needed a **manual review** and was rejected.<br/>

-**direct_debit_rejected** :(831 regs) Our last attempt of SEPA direct debit to charge the customer was rejected  <br/>

-**active** :               (59) Funds were received on the customer account.<br/>

-**transaction_declined** : (48 regs) We failed to send the funds to the customer<br/>

-**canceled** :             (33 regs) The user didn't confirm the cash request in-app, we automatically canceled it <br/>

-**direct_debit_sent** :    (34 regs) We sent/scheduled a SEPA direct debit to charge the customer account. 
                            The result of this debit is not yet confirmed<br/>

-**(no constan en los datos proporcionados):**

-**(approved)** :           CR is a 'regular' one **(= without fees)** and was approved either automatically or manually. 
                            Funds will be **sent aprox. 7 days after** the creation<br/>

-**(money_sent)** :         We transferred the fund to the customer account. 
                            Will change to **active** once we detect that the user received the funds (using user's bank history)<br/>

-**(pending)** :            The CR is **pending a manual review** from an analyst. <br/>

-**(waiting_user_confirmation)** : The user needs to confirm in-app that he want the CR (for legal reasons) <br/>

-**(waiting_reimbursement)** : We were not able to estimate a date of reimbursement, the user needs to choose one in the app.<br/>

---

#### CR campo: transfer_type

-**instant** =              user choose not received the advance instantly . <br>
-**regular** =              user choose to not pay and wait for the transfer

--

#### CR campo: recovery_status

-**null** :                 if the cash request never had a payment incident.<br>

-**completed** :            the payment incident was resolved (=the cash request was reimbursed.<br>

-**pending** :              the payment incident still open.<br>

-**pending_direct_debit** : the payment incident still open but a SEPA direct debit is launched<br>

-**cancelled**:             ???


### Fees

#### Fees: type

- **instant_payment** : fees for instant cash request (send directly after user's request, through SEPA Instant Payment)<br>

- **split_payment** :   futures fees for split payment (in case of an incident, we'll soon offer the possibility to our 
                        users to reimburse in multiples installements)<br>

- **incident** :        fees for failed reimbursement. Created after a failed direct debit <br>

- **postpone** :        fees created when a user want to postpone the reimbursment of a CR



#### Fees: status (= does the fees was successfully charged): 

- **confirmed** :   the user made an action who created a fee. It will normally get charged at the moment of the CR's reimbursement. 
                    In some rare cases, postpones are confirmed without being charges due to a commercial offer.<br>

- **rejected** :    the last attempt to charge the fee failed.<br>

- **cancelled** :   fee was created and cancelled for some reasons. 
                    It's used to fix issues with fees but it mainly concern postpone fees who failed. 
                    We are charging the fees at the moment of the postpone request. 
                    If it failed, the postpone is not accepted and the reimbursement date still the same.<br>

- **accepted** :    fees were successfully charged


#### Fees: category (Describe the reason of the incident fee.)  

- **rejected_direct_debit** :   fees created when user's bank rejects the first direct debit<br>

- **month_delay_on_payment** :  fees created every month until the incident is closed


#### Fees: charge_moment (When the fee will be charge.)  

- **before** : the fee should be charged at the moment of its creation <br>

- **after** : the fee should be charged at the moment of the CR's reimbursement





---

## Preparar data Frames: Crear libreria

### Crear columnas:

* FullUserId = user_id | ("99" +"deleted_account_id")
* Demora: money_back_date - reimbursement_date
* cash_request_received_date = ??

* TransfType: instant send_at - created_at =? 0
* TransfType: regular send_at - created_at =? 7 dies
* ...

### Crear join de los data frames

* Cesc ....

---

## Observaciones:

* Los fees solo se pagan si el dinero es instantaneo o al prorrogar la fecha de devolucion.

### Casos:

*  UsedID 3161, en cash request. 
 
 
* CR 18730
user_id clarificar las dos primeras peticiones, la parece correcta, genera un feed.
18730
18730
18730
reimbursement_date = 2020-10-24 10:59:56.652+00 coincide con la fecha del feed.
Vemos clara la peticion ordinaria con 7 dias.


* Hipotesis: hay 1 dia de gracia donde no genera feed. Caso CR: 20108

* CR 23354 caso perfecto de "regular" con devolucion correcta y en plazo.


