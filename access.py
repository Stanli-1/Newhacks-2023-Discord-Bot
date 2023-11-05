import pandas as pd
data=pd.read_excel(r"C:\Users\krish\OneDrive\Desktop\NewHacks\Chestnut_Breakfast_Menu.xlsx")
df=pd.DataFrame(data,columns=["Menu Item", "Serving Size", "Calories", "Saturated Fat (g)", "Carbohydrate (g)", "Sugars (g)","Protein (g)"])
df=df.dropna()
df = df[df['Serving Size'] != 'Bowl']
df = df[df['Serving Size'] != 'Each']
df=df.reset_index(drop=True)
df=df.drop('Serving Size', axis=1)
print(df)
