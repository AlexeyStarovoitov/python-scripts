import pandas as pd
import numpy as np
import collections
#from copy import deepcopy

url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"

dataframe = pd.read_csv(url)

print(f'Dataframe head:\n{dataframe.head(10)}\n')
print(f'Datafrmae tail:\n {dataframe.tail(10)}\n')
print(f'Dataframe resolution:\n{dataframe.shape}\n')

print(f'Dataframe description:\n{dataframe.describe()}\n')

print('Dataframe.iloc[0]:\n')
print(f'{dataframe.iloc[0]}\n')

print('Dataframe.iloc[0:2]:\n')
print(f'{dataframe.iloc[0:2]}\n')

print('Dataframe.iloc[0:4]:\n')
print(f'{dataframe.iloc[0:4]}\n')

print('Setting indexes:\n')
dataframe_with_name_indexes = dataframe.set_index(dataframe['Name'])
print(f'Dataframe with name indexes:\n{dataframe_with_name_indexes.head(5)}\n')

print('dataframe.iloc[\'Braund, Mr. Owen Harris\']:\n')
print(f'{dataframe_with_name_indexes.loc["Braund, Mr. Owen Harris"]}\n')

print('Conditional selecting rows based:\n')
print('dataframe[(dataframe["Sex"] == "male") & (dataframe["Pclass"]==3) & (dataframe["Survived"] == 1):\n')
print(f'{dataframe[(dataframe["Sex"] == "male") & (dataframe["Pclass"]==3) & (dataframe["Survived"] == 1) ]}\n')

survived_male_3rd_class = (dataframe[(dataframe["Sex"] == "male") & (dataframe["Pclass"]==3) & (dataframe["Survived"] == 1) ].shape[0] / \
                           dataframe[(dataframe["Sex"] == "male") & (dataframe["Pclass"]==3)].shape[0])*100 
print("Percent of survived male passegers of third class: {:.2f}%".format(survived_male_3rd_class))

print("Replacing values in rows:\n")
replaced_dataframe = dataframe.copy(deep=True)
replaced_dataframe["Sex"].replace({"female":"woman", "male":"man"}, inplace=True)
print(f'Dataframe with replaced sex column:\n{replaced_dataframe.head(5)}\n')

replaced_dataframe.replace({3:"Third"}, inplace=True)
print(f'Dataframe with replaced class:\n{replaced_dataframe.head(5)}\n')

replaced_dataframe.replace({r"Cum":"Cam"}, regex=True, inplace=True)
print(f'Dataframe with replaced Name:\n{replaced_dataframe.head(5)}\n')

columns_names = collections.defaultdict(str)
for name in dataframe.columns:
    columns_names[name]

print(f'column names dictionary:{columns_names}\n')
renamed_dataframe = dataframe.copy(deep=True)
#renamed_dataframe.rename(columns=columns_names)
print(f'Dataframe with named columns:\n{renamed_dataframe.rename(columns=columns_names).head(5)}\n')
print(f'Dataframe with named indexes:\n{renamed_dataframe.rename(index={0:"Zero", 1:"One", 2:"Two", 3:"Three", 4:"Four"}).head(5)}\n')
exit()

dataframe2 = pd.DataFrame()
dataframe2['name'] = ['Alex Oldvoight', 'Robert Lious Stevenson']
dataframe2['age'] = [27, 123]
dataframe2['driver'] = [True, False]
print(dataframe2)

#new_person = pd.DataFrame(data = np.array([["Mollie Wisley", 40, True]]), columns = ['name', 'age', 'driver'])
new_person = pd.Series(data = ["Mollie Wisley", 40, True], index = dataframe2.columns)
print(new_person)
dataframe2 = pd.concat([dataframe2, new_person.to_frame().T], ignore_index = True)
print(dataframe2) 