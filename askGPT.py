import pandas as pd
from openai import OpenAI
from os import listdir
from os.path import join 

def parse_xlsx(path):
    col_names = []
    dfs = []
    file_names = listdir(path)
    for file in file_names:
        df = pd.read_excel(join(path,file)) 
        df.columns = df.columns.str.strip()
        col_names.append(str(list(df.columns)))
        dfs.append(df)
    return ';\n'.join(col_names), dfs, file_names
    
#я заплатил 500 шекелей, так что не транжирьте понапрасну
def askGPT(cols): 
    client = OpenAI(
        api_key="sk-cQz7FzglTZcbFxaIDZRAWb9M9XBY2HkS",  
        base_url="https://api.proxyapi.ru/openai/v1",
    )
    message = f'''Проанализируй все названия колонок, найди те колонки, которые обозначают одно и то же и унифицируй их.
В ответном сообщении должен быть только python словарь для трансляции старых названий в новые единые для всех таблиц.
Для каждого имени из всех таблиц должен быть свой ключ, а его значение - унифицированное новое имя. 
Названия: 
{cols}'''
    messages = [ 
        {"role": "system", "content": "You are a intelligent assistant."},
        {"role": "user", "content": message}
    ] 
    chat = client.chat.completions.create( 
        model="gpt-4o", messages=messages 
    ) 
    reply = chat.choices[0].message.content 
    #messages.append({"role": "assistant", "content": reply})
    col_dict = eval(reply[reply.index('{'):reply.rindex('}')+1]) # eval делать нельзя, но если очень хочется, то можно
    return col_dict
    
def change_cols(dfs, cols_dict):
    for df in dfs:
        df.columns = [cols_dict[col.strip()] for col in df.columns]

def save_files(dfs, path, file_names):
    #Так как мы парсили таблички пандусом, то все стили, шрифты и прочее удалились, сохраняем в csv
    for df, file_name in zip(dfs, file_names):
        df.to_csv(join(path, file_name.replace('xlsx', 'csv')), index = False)

path = 'data'
cols, dfs, file_names = parse_xlsx(path)
cols_dict = askGPT(cols)
change_cols(dfs, cols_dict)
save_files(dfs, path, file_names)
print(set(dfs[0].columns) == set(dfs[1].columns))
