import os
import inspect
import numpy as np
import pandas as pd
import seaborn as sns
#import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
import yfinance as yf

# cash_request = pd.read_csv('./data/extract - cash request - data analyst.csv')
# fees = pd.read_csv('../data/extract - fees - data analyst - .csv')

def help():
    print("""Ajuda:
    import payments_manager as bp
    av.Init()
    av.Init("./data/extract - cash request - data analyst.csv","./data/extract - fees - data analyst - .csv")
    av.info()
    av.df("cr") # Cash Request
    av.df("fe") # Fees
    df_sorted = av.sort("cr_date_status", ["Date","region"], asc=[False, True])
    display(av.df("cr_cp"))
    av.add(df,"df_name")
    """)
    
def init(csv_cr = "./data/extract - cash request - data analyst.csv", 
         csv_fe = "./data/extract - fees - data analyst - .csv",
         csv_ex = "./data/divisa_exogenas.csv", debug=True):
    Manager(csv_cr, csv_fe, csv_ex, debug)

def df(name):
    return Manager.get_df(name)

def add(df, df_name):
    Manager.add_df(df, df_name)

def sort(dataframe, columns, asc = True):
    return Manager.sort_df(name= dataframe, columns= columns, ascending= asc)

def info():
    Manager.mostrar_info()

def reset():
    Manager.dataframes = {}
    if os.path.exists("./data/divisa_exogenas.csv"):
        os.remove("./data/divisa_exogenas.csv")

#def get_season():
#    return Manager.get_season

def get_map_list(expression, my_list):
    #numbers = [1, 2, 3, 4, 5]
    #cuadrados = list(map(lambda x: x**2, numbers))
    #print(cuadrados)  # [1, 4, 9, 16, 25]
    return list(map(expression, my_list))

def format_to_dates(df, time_format ='d'): # 'min','s'
    return Manager.format_to_dates(df, time_format)

class Manager:            
    debug = None
    dataframes = {}

    get_season = lambda date: '1.Primavera' if 3 <= date.month <= 5 else ('2.Verano' if 6 <= date.month <= 8 else ('3.Otoño' if 9 <= date.month <= 11 else '4.Invierno'))

    prop_classification_colors = {'City':'green' ,'Region':'yellow' ,'GreaterRegion':'orange', 'State':'red'}

    @property
    def classification_colors(self):
        return self.prop_classification_colors
    
    @property
    def region_classification(self):
        return self.prop_region_classification

    @classmethod
    def __init__(self, cr_path='./data/extract - cash request - data analyst.csv',
                  fe_path='./data/extract - fees - data analyst - .csv',
                  ex_path ='./data/divisa_exogenas.csv', debug=False):
        """
        Inicializa la clase DatasetLoader.
        
        :param debug: Booleano que indica si se debe mostrar información de depuración.
        :param csv_path: Ruta opcional a un archivo CSV para cargar inmediatamente.
        """
        self.debug = debug
        # Si se proporciona un archivo CSV, se intenta cargarlo
        if cr_path is not None:
            if self.dataframes is not None and len(self.dataframes) >0:
                if debug:
                    print("Debug: Res a fer, les dades ja estan carrgades als datafames.")
            else:    
                self.load_data(cr_path, fe_path, ex_path)
                self.format_data()
                self.exogen_data()

    @classmethod
    def get_df(cls, name='df'):
        """
        Retorna el DataFrame almacenado bajo un nombre específico.
        
        :param name: Nombre del DataFrame a obtener.
        :return: DataFrame correspondiente o None si no existe.
        """
        if cls.dataframes is not None and len(cls.dataframes) >0:
            return cls.dataframes.get(name, None).copy()
        else: 
            cls.__init__()
            return cls.dataframes.get(name, None).copy()

    @classmethod
    def add_df(cls, dataframe, name):
        cls.dataframes[name] = dataframe.copy()

    @classmethod
    def sort_df(cls, name, columns, ascending):
        #cls.dataframes[name] = dataframe
        return cls.dataframes.get(name, None).sort_values(columns, ascending= ascending)

    @classmethod
    def load_data(cls, cr_path, fe_path, ex_path):
        """
        Carga un dataset desde archivos CSV.
        
        :return: None
        """

        if not os.path.exists(cr_path):
            print(f"Error: El archivo '{cr_path}' no existe.")
            return
        if not os.path.exists(fe_path):
            print(f"Error: El archivo '{fe_path}' no existe.")
            return
        if not os.path.exists(ex_path):            
            cls.download_exogens()
            if not os.path.exists(ex_path):
                print(f"Error: El archivo '{ex_path}' no existe y no se ha podido crear de nuevo.")
                return            
        try:
            cr = pd.read_csv(cr_path)
            cls.add_df(cr,"cr")
            
            fe = pd.read_csv(fe_path)
            cls.add_df(fe,"fe")
            
            ex = pd.read_csv(ex_path)
            cls.add_df(ex,"ex")

            if cls.debug:
                print(f"Dataset {cr_path} cargado correctamente.")
                print(f"Dimensiones del dataset cr: {cr.shape}")
                print(f"Columnas: {cr.columns.tolist()}")

                print(f"Dataset {fe_path} cargado correctamente.")
                print(f"Dimensiones del dataset fe: {fe.shape}")
                print(f"Columnas: {fe.columns.tolist()}")
        except Exception as e:
            print(f"Error al cargar el archivo: {e} {e.__traceback__}")
            print(f"line: {e.__traceback__.tb_lineno} tb_frame: {e.__traceback__.tb_frame} ")

    @classmethod
    def format_to_dates(cls, df, time_format = 'd'): # 'min','s'
        #df_jo = df_jo.copy()
        df['created_at'] = df['created_at'].dt.to_period(time_format).dt.to_timestamp()
        df['created_at_fe'] = df['created_at_fe'].dt.to_period(time_format).dt.to_timestamp()
        df['updated_at'] = df['updated_at'].dt.to_period(time_format).dt.to_timestamp()
        df['updated_at_fe'] = df['updated_at_fe'].dt.to_period(time_format).dt.to_timestamp()

        df['to_receive_ini'] = pd.to_timedelta(df['to_receive_ini']).round(time_format)
        #df['to_receive_ini'] = df['to_receive_ini'].timedelta(seconds=math.ceil(df['to_receive_ini'].total_seconds()))

        df['to_receive_bank'] = pd.to_timedelta(df['to_receive_bank']).round(time_format)
        df['to_reimbur'] = pd.to_timedelta(df['to_reimbur']).round(time_format)
        df['to_reimbur_cash'] = pd.to_timedelta(df['to_reimbur_cash']).round(time_format)
        df['to_end'] = pd.to_timedelta(df['to_end']).round(time_format)
        df['to_send'] = pd.to_timedelta(df['to_send']).round(time_format)

        df['money_back_date'] = df['money_back_date'].dt.to_period(time_format).dt.to_timestamp()
        df['reimbursement_date'] = df['reimbursement_date'].dt.to_period(time_format).dt.to_timestamp()
        df['send_at'] = df['send_at'].dt.to_period(time_format).dt.to_timestamp()
        df['paid_at'] = df['paid_at'].dt.to_period(time_format).dt.to_timestamp()
        df['moderated_at'] = df['moderated_at'].dt.to_period(time_format).dt.to_timestamp()
        df['from_date'] = df['from_date'].dt.to_period(time_format).dt.to_timestamp()
        df['to_date'] = df['to_date'].dt.to_period(time_format).dt.to_timestamp()

        df['reco_creation'] = df['reco_creation'].dt.to_period(time_format).dt.to_timestamp()
        df['reco_last_update'] = df['reco_last_update'].dt.to_period(time_format).dt.to_timestamp()
        #display(df_jo.head(5))

    #@classmethod
    def fill_empty_data(df):
        #### Calcular la medias:
        #* 2,94 dias de demora promedio en las transferencias bancarias
        #* 31.6: Promedio del tiempo que tarda la empresa en cobrar los fee

        # pd.options.display.max_columns = None
        # df = pm.df('df_jo')
        # # Calcular la medias:

        # # 2,94 dias de demora promedio en las transferencias bancarias
        # print(df['to_receive_bank'].dt.days.mean())
        # #x = df['to_b2b_delay'] = (df.cr_received_date-df.send_at).dt.days
        # #display(x.notna().mean())
        # #display(df['to_b2b_delay'])# .mean()

        # # 31.6: Promedio del tiempo que tarda la empresa en cobrar los fee
        # df['to_fee_paid_delay'] = (df.paid_at -df.created_at).dt.days
        # x =  df[(df['to_fee_paid_delay'].notna()) & (df['stat_cr'] == 'money_back')]
        # display(x.to_fee_paid_delay.mean())


        # pd.options.display.max_columns = None
        # df = pm.df('df_jo')

        # # send_at mirar si tiene registros faltantes.
        # # money_back_date

        # #0 registros
        # #display(df[ (df['reimbursement_date'].isna()) & (df['stat_cr'] == 'money_back') ])


        # #191 registros
        # #display(df[ ((df['reimbursement_date'].isna()) | (df['money_back_date'].isna())) & (df['stat_cr'] == 'money_back') ])

        # #191 Normalizamos:
        # display(df[ (df['money_back_date'].isna()) & (df['stat_cr'] == 'money_back') ])
        # df['money_back_date'] = df.apply(
        #             lambda row: row['reimbursement_date']             
        #             if ( pd.isna(row['money_back_date']) & (row['stat_cr'] == 'money_back') ) 
        #             else row['money_back_date'], axis=1)
        # display(df[ (df['money_back_date'].isna()) & (df['stat_cr'] == 'money_back') ])

        # # 838  registros
        # #display(df[ (df['reimbursement_date'].notna()) & (df['money_back_date'].notna() & (df['stat_cr'] != 'money_back') )])#.head(5).reset_index()


        # Rellenamos datos faltantes
        df['money_back_date'] = df.apply(
                    lambda row: row['reimbursement_date'] 
                    if ( pd.isna(row['money_back_date']) & (row['status'] == 'money_back') ) 
                    else row['money_back_date'], axis=1
                )
        # Rellenamos datos faltantes
        df['cash_request_received_date'] = df.apply(
            lambda row: row['send_at']+ pd.DateOffset(days=3) 
            if ( pd.isna(row['cash_request_received_date']) & (row['status'] == 'money_back') ) 
            else row['cash_request_received_date'], axis=1
        )
        return df

    @classmethod
    def download_exogens(cls, save_path="./data/divisa_exogenas.csv",
                        date_start='2019-10-01', date_end='2020-11-30'):
        
        def fetch_and_prepare_data(ticker, column_name):
            """Descarga datos históricos de un ticker y los prepara con columnas específicas."""
            data = yf.download(ticker, start=date_start, end=date_end)[['Close']].reset_index()
            data.columns = ['Date', column_name]
            data['Date'] = pd.to_datetime(data['Date']).dt.date
            return data

        # Descargar y preparar datos
        exchange_rate = fetch_and_prepare_data('GBPEUR=X', 'GBP to EUR')
        btc_gbp_data = fetch_and_prepare_data('BTC-GBP', 'BTC to GBP')

        # Crear un DataFrame con todas las fechas del rango
        daily = pd.DataFrame({'Date': pd.date_range(start=date_start, end=date_end, freq='D').date})
        
        # Unir datos y llenar valores faltantes con 0
        divisa_exogenas = daily.merge(exchange_rate, on='Date', how='left').fillna(0)
        divisa_exogenas = divisa_exogenas.merge(btc_gbp_data, on='Date', how='left').fillna(0)

        # Guardar a CSV
        divisa_exogenas.to_csv(save_path, index=False)

    @classmethod
    def download_exogens_old(cls, save_path = "./data/divisa_exogenas.csv", 
                     date_start ='2019-10-01', date_end ='2020-11-30'):

        # Define el símbolo del ticker para el par de divisas (GBP/EUR)
        ticker = 'GBPEUR=X'

        # Obtener datos históricos
        data = yf.download(ticker, start=date_start, end=date_end)

        # Mantener solo la columna 'Close' (Cierre)
        exchange_rate = data[['Close']]

        # Restablecer el índice para que 'Date' (Fecha) sea una columna
        exchange_rate = exchange_rate.reset_index()

        # Renombrar las columnas a 'Date' (Fecha) y 'GBP to EUR' (GBP a EUR)
        exchange_rate.columns = ['Date', 'GBP to EUR']

        # Define el símbolo del ticker para BTC/GBP
        ticker = 'BTC-GBP'

        # Obtener datos históricos
        data4 = yf.download(ticker, start= date_start, end=date_end)

        # Mantener solo la columna 'Close' (Cierre)
        btc_gbp_data = data4[['Close']]

        # Restablecer el índice para que 'Date' (Fecha) sea una columna
        btc_gbp_data = btc_gbp_data.reset_index()

        # Renombrar las columnas a 'Date' (Fecha) y 'BTC to GBP' (BTC a GBP)
        btc_gbp_data.columns = ['Date', 'BTC to GBP']

        divisa_exogenas = pd.merge(exchange_rate, btc_gbp_data, on='Date', how='inner')
        divisa_exogenas.reset_index(drop=True).to_csv(save_path, index=False)

    @classmethod
    def exogen_data(cls):
        ex_cp = cls.get_df("ex")
        df_jo = cls.get_df('df_jo')

        ex_cp['Date'] = pd.to_datetime(ex_cp['Date'],format='ISO8601')
        ex_cp['Date'] = ex_cp['Date'].dt.date
        df_jo['created_at_d'] = pd.to_datetime(df_jo['created_at'])
        df_jo['created_at_d'] = df_jo['created_at_d'].dt.date
        df_jo = pd.merge(df_jo, ex_cp, left_on='created_at_d', right_on='Date', how ="left") #inner
        df_jo = df_jo.drop(columns=['Date'])
        df_jo = df_jo.rename(columns={'GBP to EUR': 'GBP_EUR', 'BTC to GBP': 'BTC_GBP'})

        #Fuente: https://www.statista.com/statistics/306648/inflation-rate-consumer-price-index-cpi-united-kingdom-uk/
        data = {
            'Date': ['11-2019', '12-2019', '01-2020', '02-2020', '03-2020', '04-2020', '05-2020', 
                     '06-2020', '07-2020', '08-2020', '09-2020', '10-2020', '11-2020'],
            'inflation': [1.3, 1.3, 1.8, 1.7, 1.5, 0.8, 0.5, 0.6, 1.0, 0.2, 0.5, 0.7, 0.7] 
            }

        # DataFrame original con datos diarios
        #data_daily = pd.DataFrame({'Date': pd.date_range(start='2019-12-01', end='2020-10-31', freq='D')})
        data_inflation = pd.DataFrame(data)

        # Convertir la columna 'Date' a tipo datetime con formato mensual
        data_inflation['Date'] = pd.to_datetime(data_inflation['Date'], format='%m-%Y')

        # Crear un rango de fechas que abarque el mes correspondiente para cada fila
        data_inflation = data_inflation.set_index('Date').resample('D').ffill().reset_index()

        # Renombrar columna a 'Inflation (%)'
        data_inflation.rename(columns={'index': 'Date'}, inplace=True)
        data_inflation['Date'] = data_inflation['Date'].dt.date

        # Unir ambos DataFrames por la columna de fecha
        df_jo = pd.merge(df_jo, data_inflation, left_on='created_at_d', right_on='Date', how='left')

        #Fuente csv: https://www.ons.gov.uk/employmentandlabourmarket/peoplenotinwork/unemployment/timeseries/mgsx/lms
        # Fuente: https://www.oecd.org/en/data/indicators/unemployment-rate.html?oecdcontrol-59006032fa-var1=GBR&oecdcontrol-4c072e451c-var3=2020-10
        data = {
            'Date': ['11-2019', '12-2019', '01-2020', '02-2020', '03-2020', '04-2020', '05-2020', 
                     '06-2020', '07-2020', '08-2020', '09-2020', '10-2020', '11-2020'],
            'unemploy_rate': [3.9, 4.0, 4.1, 4.1, 4.2, 4.2, 4.2, 4.4, 4.7, 5.0, 5.2, 5.2, 5.3]
            }
        data_inflation = pd.DataFrame(data)

        # Convertir la columna 'Date' a tipo datetime con formato mensual
        data_inflation['Date'] = pd.to_datetime(data_inflation['Date'], format='%m-%Y')

        # Crear un rango de fechas que abarque el mes correspondiente para cada fila
        data_inflation = data_inflation.set_index('Date').resample('D').ffill().reset_index()

        # Renombrar columna a 'Inflation (%)'
        data_inflation.rename(columns={'index': 'Date'}, inplace=True)
        data_inflation['Date'] = data_inflation['Date'].dt.date

        # Unir ambos DataFrames por la columna de fecha
        df_jo = pd.merge(df_jo, data_inflation, left_on='created_at_d', right_on='Date', how='left')
        
        df_jo = df_jo.drop(columns=['Date_x'])
        df_jo = df_jo.drop(columns=['Date_y'])
        cls.add_df(df_jo,"df_jo")

        # df_hyper = df_jo[[#'id_cr', #'id_fe','fe_cr_id'
        #     'user_id', #'active',
        #     'created_at', # 'updated_at',
        #     'created_at_slot', 'created_at_dow',
        #     #'created_at_d', 'created_at_w', 'created_at_m',
        #     #'Mes_created_at',
        #     #'cash_request_received_date',
        #     'amount', # 'fee',
        #     'needs_m_check_recov', 'n_fees', 'n_backs', 'n_recovery', 'n_incidents', 
        #     #'stat_cr', 'stat_fe',
        #     #'type',
        #     'transfer_type', 'charge_moment',
        #     #'recovery_status', 
        #     'reco_creation',  #'reco_last_update',
        #     'to_receive_ini', 'to_receive_bank', 'to_reimbur',
        #     'to_reimbur_cash', 'to_end', 'to_send',
        #     'send_at', 'paid_at',
        #     'moderated_at', 'category',
        #     #'reason',
        #     #'from_date', 'to_date',            
        #     #'updated_at_fe',             
        #     #'n_cr_fe_w', 'n_cr_fe_m', 
        #     'GBP_EUR', 'BTC_GBP', 'inflation', 'unemploy_rate'
        #     ]].copy()
        # cls.add_df(df_hyper,"df_hyper")


        df_hyper = df_jo[[
            'user_id',
            #'created_at', 
            'created_at_slot', 'created_at_dow',
            'amount',
            'needs_m_check_recov', 'n_fees', 'n_backs', 'n_recovery', 'n_incidents', 
            'transfer_type', 'charge_moment',
            #'reco_creation', 
            #'to_receive_ini', 'to_receive_bank', 'to_reimbur',
            #'to_reimbur_cash', 'to_end', 'to_send',
            #'send_at', 'paid_at',
            #'moderated_at', 
            'n_cr_fe_w', #'n_cr_fe_m', 
            'category',
            'inflation' , 'GBP_EUR', 'BTC_GBP', 'unemploy_rate',
            ]].copy()
        cls.add_df(df_hyper,"df_hyper")


    @classmethod
    def format_data(cls):
        """
        Formatea el dataset basado en ...
        
        :param conditions: None
        :return: Un DataFrame con los datos filtrados.
        """
        if cls.get_df("cr") is None:
            print("format_data: El dataset Cash Request no se ha cargado. Usa el método 'load_data' primero.")
            return None
        if cls.get_df("fe") is None:
            print("format_data: El dataset Fees no se ha cargado. Usa el método 'load_data' primero.")
            return None
        
        
        # Dataframe normalitzat
        cr_cp = cls.get_df("cr").copy()
        fe_cp = cls.get_df("fe").copy()

        # Eliminem registres que no es corresponen amb CR al buscar id null - (Cash Request)
        # Instant Payment Cash Request 11164
        # Instant Payment Cash Request 11444
        # Instant Payment Cash Request 11788
        # Instant Payment Cash Request 12212
        fe_cp = fe_cp.dropna(subset=['cash_request_id'])

        
        #if 'cash_request_id' not in fe_cp.columns:
        #    fe_cp['cash_request_id'] = 0  # O un altre valor predeterminat

        # Convertir a INT i treure els nulls, deixant el valor a 0. 
        #fe_cp['cash_request_id'] = fe_cp['cash_request_id'].fillna(0).astype(int)
        fe_cp['cash_request_id'] = fe_cp['cash_request_id'].round().astype('Int64')


        cr_cp['created_at'] = pd.to_datetime(cr_cp['created_at']) #Normalizar fechas
        cr_cp['created_at'] = cr_cp['created_at'].dt.tz_localize(None)
        cr_cp['Mes_created_at'] = cr_cp['created_at'].dt.to_period('M')
        
        # Normalitzar i deslocalitzar dates
        date_cols = ['updated_at','moderated_at','reimbursement_date','cash_request_received_date',
                    'money_back_date','send_at','reco_creation','reco_last_update']
        for col in date_cols:
            if col in cr_cp.columns:  # Comprova si la columna existeix
                # cr_cp[col] = pd.to_datetime(cr_cp[col], errors='coerce')  # Normalitza les dates ## !! aixo descarta dates !!
                cr_cp[col] = pd.to_datetime(cr_cp[col],format='ISO8601')
                cr_cp[col] = cr_cp[col].dt.tz_localize(None)  # Elimina la informació de zona horària
        
         # Convertir a INT i treure els nulls, deixant el valor a 0. 
        cr_cp['user_id'] = cr_cp['user_id'].fillna(0).astype(int)
        
        # TODO OK: això sembla que no cal ? Si que cal per la join !!
        cr_cp['recovery_status'] = cr_cp['recovery_status'].fillna('nice')
        fe_cp['category'] = fe_cp['category'].fillna('nice')

        # errors = cr_cp[(cr_cp['created_at']> cr_cp['money_back_date']) | 
        #       (cr_cp['created_at'] > cr_cp['reimbursement_date'])]

        # Eliminar les files que no tenen sentit respecte a dates:
        cr_cp.drop(cr_cp[cr_cp['created_at'] > cr_cp['money_back_date']].index, inplace=True)
        cr_cp.drop(cr_cp[cr_cp['created_at'] > cr_cp['reimbursement_date']].index, inplace=True)

        cls.fill_empty_data(cr_cp)

        #cr_cp.info()
        #display(cr_cp)

        #if 'cash_request_id' not in fe_cp.columns:
        #    fe_cp['cash_request_id'] = 0  # O un altre valor predeterminat
        fe_cp['cash_request_id'] = fe_cp['cash_request_id'].fillna(0).astype(int)
        #fe_cp['cash_request_id'] = fe_cp['cash_request_id'].astype(int)

        # Normalitzar i deslocalitzar dates
        date_cols = ['created_at','updated_at','paid_at','from_date','to_date']
        for col in date_cols:
            if col in fe_cp.columns:  # Comprova si la columna existeix
                #fe_cp[col] = pd.to_datetime(fe_cp[col], errors='coerce')  # Normalitza les dates
                fe_cp[col] = pd.to_datetime(fe_cp[col],format='ISO8601')
                fe_cp[col] = fe_cp[col].dt.tz_localize(None)  # Elimina la informació de zona horària
        #fe_cp.info()

        # Calculos de fechas en CR_CP
        # Tiempo que tarda en recibir el dinero el usuario desde la primera accion.
        # cr_received_date  (cash_request_received_date) = ??
        cr_cp['to_receive_ini'] = cr_cp.cash_request_received_date-cr_cp.created_at

        # Tiempo que tarda en recibir el dinero el usuario desde que se envia (demora entre bancos).
        cr_cp['to_receive_bank'] = cr_cp.cash_request_received_date-cr_cp.send_at

        # Tiempo que la empresa recupera el dinero desde la primera accion.
        cr_cp['to_reimbur'] = cr_cp.reimbursement_date-cr_cp.created_at

        # Tiempo en el que la emprera realmente ha prestado el dinero
        cr_cp['to_reimbur_cash'] = cr_cp.reimbursement_date-cr_cp.send_at

        # Tiempo que la empresa presta el dinero.
        cr_cp['to_end'] = cr_cp.reimbursement_date-cr_cp.money_back_date
        # En funcion del tipo instant o regular:
        # TransfType: instant send_at - created_at =? 0 dias
        # TransfType: regular send_at - created_at =? 7 dias
        cr_cp['to_send'] = cr_cp.send_at-cr_cp.created_at


        # Verifica duplicats a fe_cp
        #duplicats_fe_cp = fe_cp[fe_cp.duplicated(subset=['id', 'cash_request_id'], keep=False)]
        #print(duplicats_fe_cp)

        # Verifica duplicats a cr_cp
        #duplicats_cr_cp = cr_cp[cr_cp.duplicated(subset=['id'], keep=False)]
        #print(duplicats_cr_cp)

        #display(fe_cp[['id','cash_request_id']])
        #df_jo = pd.merge(cr_cp, fe_cp,  on=['id','cash_request_id'], how ="left")
        df_jo = pd.merge(cr_cp, fe_cp, left_on='id', right_on='cash_request_id', how ="left") #inner       
        
        #ex_cp = fe_cp = cls.get_df("ex").copy()
        #df_jo = pd.merge(df_jo, ex_cp, left_on='created_at', right_on='Date', how ="left") #inner       
        #df_jo.info()

        # TODO OK: això sembla que no cal ? Si que cal per la join !!
        # Podriamos modificamos el valor 'nice' a 'cr_no_fee' para ser mas claros, pero luego usarlos sera mas dificil. 
        # LO PODEMOS COMENTAR EN EQUIPO.
        df_jo['type'] = df_jo['type'].fillna(0)  # quitamos el 'nice', nos da problemas al estandarizar
        # Rellenar NaN de fee por 0
        df_jo['total_amount'] = df_jo['total_amount'].fillna(0)

        # Añadir la columna 'active': 1 si deleted_account_id es NaN, de lo contrario 0
        df_jo['active'] = df_jo['deleted_account_id'].apply(lambda x: 1 if pd.isna(x) else 0)

        # Migrar user_id:
        # - Para las filas donde deleted_account_id existe, usar "99" + deleted_account_id
        # - De lo contrario, mantener el user_id original
        df_jo['user_id'] = df_jo.apply(
            lambda row: int(f"{99000000+int(row['deleted_account_id'])}") if not pd.isna(row['deleted_account_id']) else row['user_id'],
            axis=1
        )
        # Eliminar la columna 'deleted_account_id'
        df_jo = df_jo.drop(columns=['deleted_account_id'])

        df_jo.insert(df_jo.columns.get_loc("user_id")+1,"active",df_jo.pop("active"))

        # fields_actions = ['id_x as id_cr','amount','status_x as stat_cr','created_at_x','user_id','moderated_at: 0=manual 1=auto',
        #           'reimbursement_date','cash_request_received_date', 'money_back_date','transfer_type','send_at',
        #           'recovery_status: 0= null, 1=no, 2=si, etc.','','type','status_y as stat_fe','category','total_amount','paid_at',
        #           'from_date','to_date','charge_moment 0=after, 1=before']

        # Renombrar
        df_jo = df_jo.rename(columns={'id_x': 'id_cr'})
        df_jo = df_jo.rename(columns={'id_y': 'id_fe'})
        df_jo = df_jo.rename(columns={'cash_request_id': 'fe_cr_id'})
        df_jo = df_jo.rename(columns={'status_x': 'stat_cr'})
        df_jo = df_jo.rename(columns={'status_y': 'stat_fe'})

        df_jo = df_jo.rename(columns={'created_at_x': 'created_at'})
        df_jo = df_jo.rename(columns={'created_at_y': 'created_at_fe'})        
        
        df_jo = df_jo.rename(columns={'updated_at_x': 'updated_at'})
        df_jo = df_jo.rename(columns={'updated_at_y': 'updated_at_fe'})

        df_jo['id_fe'] = df_jo['id_fe'].fillna(0).astype(int)

        # Copiar para mantener compatibilidad
        #df_jall = df_jall.rename(columns={'cash_request_received_date': 'cr_received_date'})
        df_jo['cr_received_date'] = df_jo['cash_request_received_date']






        #df_jo['fee'] = df_jo['total_amount']
        df_jo = df_jo.rename(columns={'total_amount': 'fee'})
        
        df_jo['Mes_created_at'] = df_jo['created_at'].dt.to_period('M')
        
        # Tiempo que tarda en recibir el dinero el usuario desde la primera accion.
        # cr_received_date  (cash_request_received_date) = ??
        df_jo['to_receive_ini'] = df_jo.cash_request_received_date-df_jo.created_at

        # Tiempo que tarda en recibir el dinero el usuario desde que se envia (demora entre bancos).
        df_jo['to_receive_bank'] = df_jo.cash_request_received_date-df_jo.send_at
        # Tiempo en el que el banco tarda a entregar el dinero a la cuenta del cliente(al otro banco),  emprera realmente ha prestado el dinero
        #df_jo['to_b2b_delay_D'] = (df_jo.cash_request_received_date-df_jo.send_at).dt.days

        # Tiempo que la empresa recupera el dinero desde la primera accion.
        df_jo['to_reimbur'] = df_jo.reimbursement_date-df_jo.created_at

        # Tiempo en el que la emprera realmente ha prestado el dinero
        df_jo['to_reimbur_cash'] = df_jo.reimbursement_date-df_jo.send_at
        #df_jo['to_reimbur_cash_de'] = (df_jo.reimbursement_date-df_jo.send_at).dt.days()
        df_jo['to_reimbur_cash_de'] = (df_jo['reimbursement_date'] - df_jo['send_at']).dt.days

        # Tiempo que la empresa presta el dinero.
        # Dedicion de money_back_date: - Date where the CR was "considered" as money back. 
        #   It's either the paid_by_card date or 
        #   the date were we considered that's the direc debit "have low odds to be rejected" (based on business rules) 
        df_jo['to_end'] = df_jo.reimbursement_date-df_jo.money_back_date


        #### Calcular la medias:
        #* 2,94 dias de demora promedio en las transferencias bancarias
        #* 31.6: Promedio del tiempo que tarda la empresa en cobrar los fee

        # pd.options.display.max_columns = None
        # df = pm.df('df_jo')
        # # Calcular la medias:

        # # 2,94 dias de demora promedio en las transferencias bancarias
        # print(df['to_receive_bank'].dt.days.mean())
        # #x = df['to_b2b_delay'] = (df.cr_received_date-df.send_at).dt.days
        # #display(x.notna().mean())
        # #display(df['to_b2b_delay'])# .mean()

        # # 31.6: Promedio del tiempo que tarda la empresa en cobrar los fee
        # df['to_fee_paid_delay'] = (df.paid_at -df.created_at).dt.days
        # x =  df[(df['to_fee_paid_delay'].notna()) & (df['stat_cr'] == 'money_back')]
        # display(x.to_fee_paid_delay.mean())



        #* Demora:
        #df['to_delay'] = df_jo.money_back_date-df_jo.reimbursement_date

        # En funcion del tipo instant o regular:
        # TransfType: instant send_at - created_at =? 0 dias
        # TransfType: regular send_at - created_at =? 7 dias
        df_jo['to_send'] = df_jo.send_at-df_jo.created_at


        # Rellenamos datos faltantes
        df_jo['money_back_date'] = df_jo.apply(
                    lambda row: row['reimbursement_date'] 
                    if ( pd.isna(row['money_back_date']) & (row['stat_cr'] == 'money_back') ) 
                    else row['money_back_date'], axis=1
                )
        # Rellenamos datos faltantes
        df_jo['cr_received_date'] = df_jo.apply(
            lambda row: row['send_at']+ pd.DateOffset(days=3) 
            if ( pd.isna(row['cr_received_date']) & (row['stat_cr'] == 'money_back') ) 
            else row['cr_received_date'], axis=1
        )

        order = ['id_cr','id_fe', 'fe_cr_id','user_id','active', 'created_at','created_at_fe','amount','fee','stat_cr','stat_fe','transfer_type','type',
                'to_receive_ini', 'to_receive_bank','to_reimbur','to_reimbur_cash','to_end','to_send',
                'send_at', 'cr_received_date', 'money_back_date', 'reimbursement_date', 'paid_at','charge_moment','moderated_at','reason',
                'category','from_date','to_date', 'recovery_status','updated_at','reco_creation','reco_last_update','updated_at_fe',
                'Mes_created_at','cash_request_received_date'] 
        df_jo= df_jo[order]

        df_jo = cls.calc_columns(df_jo)

        df_jall = df_jo.copy()
            
        # Eliminar
        #df_jo = df_jo.drop(columns=['updated_at'])
        #df_jo = df_jo.drop(columns=['recovery_status'])
        #df_jo = df_jo.drop(columns=['reco_creation'])
        #df_jo = df_jo.drop(columns=['reco_last_update'])
        #df_jo = df_jo.drop(columns=['id_y'])
        #df_jo = df_jo.drop(columns=['cash_request_id'])
        #df_jo = df_jo.drop(columns=['reason'])
        #df_jo = df_jo.drop(columns=['created_at_y'])
        #df_jo = df_jo.drop(columns=['updated_at_y'])

        cls.add_df(cr_cp ,"cr_cp")
        cls.add_df(fe_cp ,"fe_cp")        
        cls.add_df(df_jo,"df_jo")
        cls.add_df(df_jall,"df_jall")
        #print(df_jo.info())        

    #@classmethod
    def calc_columns(df):
        '''
        '''

        # # Aplicar las franjas horarias a CR created_at en nueva columna llamada 'created_at_slot' (created_at_slot_h para ver exactamente la hora)
        # # de 7 a 14 mañana, 
        # # de 14 a 21 tarde,
        # # de 21 a 6 noche
        clasificar_hora = lambda hora: "7" if 7 <= hora.hour < 14 else ("14" if 14 <= hora.hour < 21 else "21")
        # clasificar_hora_h = lambda hora: f"{hora.hour}-Mañana" if 7 <= hora.hour < 14 else (f"{hora.hour}-Tarde" if 14 <= hora.hour < 21 else f"{hora.hour}-Noche")
        # df['created_at_slot'] = df['created_at'].apply(clasificar_hora)
        # df['created_at_slot_h'] = df['created_at'].apply(clasificar_hora_h)
        df['created_at_slot'] = df['created_at'].dt.hour
        #df['created_at_slot_h'] = df['created_at'].apply(clasificar_hora)

        # Determinar el dia de la semana de CR created_at (The day of the week with Monday=0, Sunday=6)
        df['created_at_dow'] = df['created_at'].dt.dayofweek

        # Rellenar NaN de stat_fe por cr regulares
        df['stat_fe'] = df['stat_fe'].fillna('cr_regular')

        # Clasificacion basica de los usuarios: segun los status de CR y FEEDS
        good_cr = ['approved', 'money_sent', 'pending', 'direct_debit_sent', 'active', 'money_back']
        good_fe = ['confirmed', 'accepted', 'cr_regular']
        # df['needs_m_check'] = (~(
        #     (df['stat_cr'].isin(good_cr)) & 
        #     (df['stat_fe'].isin(good_fe))
        #     )).astype(int)
        
        no_incident_cr_reco = ['nice']
        df['needs_m_check_recov'] = (~(
            (df['stat_cr'].isin(good_cr)) & 
            (df['stat_fe'].isin(good_fe)) & 
            (df['recovery_status'].isin(no_incident_cr_reco))
            )).astype(int)




        # # Para stat_cr == "money_back" & stat_fe == "accepted" acumulamos el numero de operaciones con feeds
        #df = df.drop(columns=['n_fees'])
        df = df.sort_values(['created_at','created_at_fe'])
        df['n_fees'] = (df['stat_cr'] == "money_back") & (df['stat_fe'] == "accepted") & (df['fee'] > 0)
        df['n_fees'] = df.groupby('user_id')['n_fees'].cumsum()

        # # Para stat_cr == "money_back" & stat_fe == "accepted" acumulamos el numero de operaciones de tipo money_back        
        df = df.sort_values(['created_at','created_at_fe'])
        unique_cr = (df['stat_cr'] == "money_back") & (df['amount'] > 0) & ~df.duplicated(subset=['id_cr'], keep='first')
        df['n_backs'] = unique_cr.groupby(df['user_id']).cumsum() # -1 # 2024-12-11 Cesc no podemos hacer el -1 esto nos deja casos en negativo que son claramente erroneos
        
        #df = df.drop(columns=['n_backs'])
        #df['n_backs'] = (df['stat_cr'] == "money_back")  & (df['amount'] > 0)
        #df['n_backs'] = df.groupby('user_id')['n_backs'].cumsum()

        # #df['n_backs'] = 0
        # #df.loc[unique_cr, 'n_backs'] = unique_cr.groupby(df['user_id']).cumsum()

        #df['n_backs'] = df['n_backs'].where(df['stat_cr'] == "money_back", -1)
        #df['n_backs'] = df.drop_duplicates(subset=['user_id', 'id_cr']).groupby('user_id').cumcount() + 1
        #df['n_backs'] = df.groupby('user_id')['id_cr'].transform('nunique')
        #df['n_backs'] = df.groupby('user_id')['n_backs'].fillna(method='ffill')



        # # Para CR recovery_status != "nice" acumulamos el numero de recovery_status que han tenido incidentes.        
        df = df.sort_values(['created_at','created_at_fe'])
        df['n_recovery'] = (df['recovery_status'] != "nice") & (df['amount'] > 0)
        df['n_recovery'] = df.groupby('user_id')['n_recovery'].cumsum()

        # # Para stat_cr != good_cr | stat_fe != good_fe acumulamos el numero de operaciones de tipo money_back
        good_cr = ['approved', 'money_sent', 'pending', 'direct_debit_sent', 'active', 'money_back']
        good_fe = ['confirmed', 'accepted', 'cr_regular']        
        df = df.sort_values(['created_at','created_at_fe'])
        df['n_incidents'] = ( (~df['stat_cr'].isin(good_cr)) | (~df['stat_fe'].isin(good_fe)) | (df['recovery_status'] != "nice")  ) & (df['amount'] > 0)
        df['n_incidents'] = df.groupby('user_id')['n_incidents'].cumsum()

        #df['n_user_cr_fe'] = df.groupby('user_id').size().reset_index(name='n_user_cr_fe')

    
        df['created_at_w'] = df['created_at'].dt.isocalendar().week
        df_mb = df[df['stat_cr'].isin(good_cr)] # == 'money_back']
        df_mb = df_mb[df_mb['stat_fe'].isin(good_fe)] # == 'accepted']
        frecuencia_w = df_mb.groupby(['user_id', 'created_at_w']).size().reset_index(name='n_cr_fe_w')
        df = pd.merge(df, frecuencia_w, on=['user_id', 'created_at_w'], how='left')

        df['created_at_m'] = df['created_at'].dt.month
        df_mb = df[df['stat_cr'].isin(good_cr)] # == 'money_back']
        df_mb = df_mb[df_mb['stat_fe'].isin(good_fe)] # == 'accepted']
        frecuencia_m = df_mb.groupby(['user_id', 'created_at_m']).size().reset_index(name='n_cr_fe_m')        
        df = pd.merge(df, frecuencia_m, on=['user_id', 'created_at_m'], how='left')


        #cls.add_df(df_jo,"df_jo")
        return df

    @classmethod
    def filter_data(cls, df_name, **conditions):
        """
        Filtra el dataset basado en condiciones especificadas.
        
        :param conditions: Condiciones de filtro en formato clave=valor. 
                           Ejemplo: columna="valor"
        :return: Un DataFrame con los datos filtrados.
        """
        df = cls.get_df(df_name)
        if df is None:
            print("filter_data: El dataset no se ha encontrado.")
            return None
        
        filtered_data = df
        for column, value in conditions.items():
            if column in filtered_data.columns:
                filtered_data = filtered_data[filtered_data[column] == value]
                if cls.debug:
                    print(f"Filtrando por {column}={value}. Dimensiones actuales: {filtered_data.shape}")
            else:
                print(f"Advertencia: La columna '{column}' no existe en el dataset.")
        
        return filtered_data

    @classmethod
    def obtener_regions(cls, filtro):
        return [clave for clave, valor in cls.prop_region_classification.items() if valor == filtro]

    @classmethod
    def mostrar_info(cls):
        """
        Muestra información general del dataset cargado.
        
        :return: None
        """
        
        cr = cls.get_df("cr")
        fe = cls.get_df("fe")
        if cr is None or fe is None:
            print("mostrar_info: Los datasets no se han cargado. Usa el método 'load_data' primero.")
            return

        print(f"Lista de dataframes: {list(cls.dataframes.keys())}")
        if cls.debug:
            print("Información general del dataset:")
            print(cr.info())

            print("Información estadística del dataset:")
            print(cr.describe())

            # years = cls.get_df("years")
            # print(f"\nAños: {years}")

            # regions = cls.get_df("regions")
            # print(f"\nRegiones comerciales: {regions}")

            #print("\nPrimeras 5 filas del dataset df_cp:")
            #df_cp = cls.get_df("df_cp")
            #print(df_cp.head())

#region_classification = Manager.prop_region_classification
classification_colors = Manager.prop_classification_colors

color_orga ='green'; color_conv ='grey'; color_total ='blue'