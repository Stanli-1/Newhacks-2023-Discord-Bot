#this file processes messages
import pandas as pd

#predefine the ranking array
input = []
#number of preferences
#1. calories 2. protein
number_of_preferences = 1

#min preference: 0, max 10
min_preference = 0
max_preference = 10

"""
calculating average needs of a person: 
using breakfast entrees of 100g per portion, we will calculate the target number of a nutrient through these metrics:
Average weight of food eaten per day: 1814g
Average calories required per day: 2250
Average calories required per 100g: 2250*100/1814 = 80.6
Average protein required per day: 50g
Average protein required per 100g: 50*100/1814 = 2.22
Average saturated fat required per day: 17.6g
Average saturated fat required per 100g: 17.6*100/1814 = 0.96
"""
calorie_target = 80.6
protein_target = 2.22
saturated_fat_target = 0.96
carbohydrate_target = 68.22
sugar_target = 1.68


#nutrient scaling factor!
#this is so arbitrary!
calorie_scale = 5
protein_scale = -4
saturated_fat_scale = 3
carbohydrate_scale = 2
sugar_scale = 1



#titles of menu directories:
chestnut_breakfast_menu = r"Chestnut_Breakfast_Menu.xlsx"
chestnut_dinner_menu = r"Chestnut_Dinner_Menu.xlsx"

#reads the excel file of all food options and returns a dataframe with relevant columns and rows (because we are lazy)
def read_excelfile():
    data=pd.read_excel(chestnut_breakfast_menu)
    df=pd.DataFrame(data,columns=["Menu Item", "Serving Size", "Calories", "Saturated Fat (g)", "Carbohydrate (g)", "Sugars (g)","Protein (g)"])
    df=df.dropna()
    df = df[df['Serving Size'] != 'Bowl']
    df = df[df['Serving Size'] != 'Each']
    df=df.reset_index(drop=True)
    df=df.drop('Serving Size', axis=1)

    #adding the empty score table
    #df['score'] = 0.0
    
    return df


#return an array of preference variables from the user
#redundant
def get_preference_array(message):
    #creates preferences array and sets them all to 0
    preferences = [-1 for i in range(number_of_preferences)]
    #break down message into an array of words and remove the first word (remove the prompt word)
    string_input = message.split()[1:]
    #check if string input has the correct amount of varialbes entered
    if len(string_input) != number_of_preferences:
        return preferences
    #for every list entry,
    #1. check if it can be converted to a number
    #2. convert the entry into a number and put it into preferences
    for i in range(number_of_preferences):
        #1. convert
        preferences[i] = string_to_int(string_input[i])
        #2. check if the number is on the right scale
        if preferences[i] < min_preference or preferences[i] > max_preference:
            preferences[i] = -1 #hard code error
            return preferences #early return
    
    return preferences
    #returns an array in [1, 2... n]

#convert string to int, and also check
def string_to_int(input):
    try:
        int_output = int(input)
    except ValueError:
        return -1
    return int_output

#attempt at making a new type of function
def add_scores_df(data):
    for i in range(len(data.axes[0])):
        mealName = data.iat[i,0]
        #hard coded names, in the order: Calories, Saturated Fat, Carbs, Sugars, Protein 
        calorie = data.iat[i,1]
        saturated_fat = data.iat[i,2]
        carbohydrate = data.iat[i,3]
        sugar = data.iat[i,4]
        protein = data.iat[i,5]

        data.iloc[i,7] = weight_score_formula(calorie, protein, saturated_fat, carbohydrate, sugar)
    #for every entry in the list, if the entry is negative, map to 0-5. if the entry is positive, map to 5-10. This should map the random range that we initially created to a range from 0-10.
    fixed_data = data
    for i in range(len(data.axes[0])):
        if(data.iloc[i,7]<=0):
            #map to 0-5
            #df['AAL'].max()
            fixed_data.iloc[i,7] = newMap(data['score'].min(), 0, 0, 5, data.iloc[i,7])
        else: #map to 5-10
            fixed_data.iloc[i,7] = newMap(0, data['score'].max(), 5, 10, data.iloc[i,7])
    
    return data



#add s scores to a new column in a dataframe
def add_scores(data):

    #method 1: create an array and make it all work together
    #create an array that will store all the S values (will be used later when creating new column)
    scoreArray = [0 for i in range(len(data.axes[0]))]

    #for every row (food choice), calculate 
    for i in range(len(data.axes[0])):
        mealName = data.iat[i,0]
        #hard coded names, in the order: Calories, Saturated Fat, Carbs, Sugars, Protein 
        calorie = data.iat[i,1]
        saturated_fat = data.iat[i,2]
        carbohydrate = data.iat[i,3]
        sugar = data.iat[i,4]
        protein = data.iat[i,5]
        
        scoreArray[i] = weight_score_formula(calorie, protein, saturated_fat, carbohydrate, sugar)
         
    #for every entry in the list, if the entry is negative, map to 0-5. if the entry is positive, map to 5-10. This should map the random range that we initially created to a range from 0-10.
    fixedScoreArray = [0.0 for i in range(len(data.axes[0]))]
    for i in range(len(scoreArray)):
        if(scoreArray[i]<=0):
            #map to 0-5
            fixedScoreArray[i] = newMap(min(scoreArray), 0, 0, 5, scoreArray[i])
        else: #map to 5-10
            fixedScoreArray[i] = newMap(0, max(scoreArray), 5, 10, scoreArray[i])
    
    #add fixedScore array later
    data.insert(len(data.axes[1]), "score", fixedScoreArray, True)

    return data

#takes in the food dataframe with the scores, and selects the best choices based off of preferences and sorts based off of target score
#we'll give a margin of error of +- 1 for the time being, really random
def select_choices(data, preference):
    temp_data = data 
    margin_of_error = 0.5 #start with small margin of error

    #infinite loop until we get enough items in the list
    while(True):
        #delete all rows that aren't within the margin of error
        #keeping rows that are below highest margin of error
        temp_data =  data[data.score < preference+margin_of_error]
        #allow rows taht are above lowest margin of error
        temp_data = temp_data[temp_data.score > preference-margin_of_error]
        #re-indexing 
        temp_data=temp_data.reset_index(drop=True)
        #redefine score by distance to target scores, loop per row
        for i in range(len(temp_data.axes[0])):
            #hard coding in column 'score' with a '6' because i dont think we can mix str and number to access cells
            temp_data.iloc[i,6] = abs(float(preference) - temp_data.iloc[i,6])
        
        #sort rows by distance to target score
        temp_data = temp_data.sort_values(by=['score'], ascending=True) 
        #if the processed data has at least 3 options, we done
        if len(temp_data.axes[0]) >= 3:
            break
        else: #increase margin of error and try again
            margin_of_error += 0.5 
            
    return temp_data

#creates a selected list string from the ordered dataframe for the bot to speak out
#input: dataframe with ordered scores ascending (meaning best options 1st) 
#output: string that gives an ordered list


# take final dataframe that is sorted by score values, create output text that will be displayed in discord
def output_list(data):  
  output=''
  output = 'Here are your Top Food Choices:'

  for i in range(len(data.axes[0])): 
    output += "\n#" + str(i+1) + ": " + str(data.iloc[i,0]) + " - " + str(data.iloc[i,1]) + " calories"
  return output

#returns the score of given food options for balancing weight
def weight_score_formula(calorie, protein, saturated_fat, carbohydrate, sugar):
    score = 0
    score += calorie_scale*percentage_change_formula(calorie,calorie_target)
    score += protein_scale*percentage_change_formula(protein,protein_target)
    score += saturated_fat_scale*percentage_change_formula(saturated_fat,saturated_fat_target)
    score += carbohydrate_scale*percentage_change_formula(carbohydrate,carbohydrate_target)
    score += sugar_scale*percentage_change_formula(sugar,sugar_target)
    return score

#literally in the name
def percentage_change_formula(actual, initial):
    return (actual-initial)/initial

#gets the array and maps the array on a scale of max to min (5 parameters!)
#takes the value and maps it onto a new scale
def newMap(oldMin, oldMax, newMin, newMax, value):
    newValue = ((value-oldMin)/(oldMax-oldMin) * (newMax-newMin)) + newMin
    return newValue

#incredible way of making a global variable of the whole spreadsheet!
meal_spreadsheet = read_excelfile()
meal_spreadsheet = add_scores(meal_spreadsheet)

#returns the message the bot should send
def handle_response(message: str) -> str:
    #makes the message all into lowercase
    p_message = message.lower()
    #get the first word of the command, gets the prompt
    prompt_message = p_message.split()[0]
    #correct format for this command: "!food a b c" which starts with '!food' and is 11 chars long
    #this prompt is for getting preferences

    #reset global weight variables
    calorie_scale = 5
    protein_scale = -4
    saturated_fat_scale = 3
    carbohydrate_scale = 2
    sugar_scale = 1

    # command that provides user basic info about bot
    if prompt_message == '!hello':
        return "Hello! Welcome to MunchMate, your food buddy! \nJust type \"!food\" followed by a number from 0 to 10 to indicate your weight goal. 10 means gaining the most weight, 0 means losing the most weight, and 5 means maintaining weight. I'll suggest tasty options accordingly."

    #get manual input of all the weight variables
    #!custom <calorie> <protein> <saturated> <carb> <sugar>
    if prompt_message == '!custom':
        preferences = get_preference_array(p_message)
        for i in range(len(preferences)):
            if (preferences < min_preference or preferences > max_preference):
                return 'Input Error'
                
        selection_spreadsheet = meal_spreadsheet

        #redefine preferences, these variables are global so it should just update to the score function
        calorie_scale = preferences[0]
        protein_scale = preferences[1]
        saturated_fat_scale = preferences[2]
        carbohydrate_scale = preferences[3]
        sugar_scale = preferences[4]

        #start loading scores and stuff
        selection_spreadsheet = select_choices(selection_spreadsheet, preferences)

        print(selection_spreadsheet)

    # food command 
    if prompt_message == '!food':
        
        #preferences gets one number
        string_input = p_message.split()[1:]
        #future message: catch empty array (i.e someone enters "!food ")!
        preferences = string_to_int(string_input[0])
        if (preferences < min_preference or preferences > max_preference):
            #failed input L
            return 'Input Error' #or some kind of actually helpful message to the user
        #get spreadsheet from global variable
        selection_spreadsheet = meal_spreadsheet
        #calculate scores in the spreadsheet
        #selection_spreadsheet = add_scores(meal_spreadsheet)

        #sort spreadsheet based on preference
        selection_spreadsheet = select_choices(selection_spreadsheet, preferences)
        
        print(selection_spreadsheet)

        selection_speadsheet = output_list(selection_spreadsheet)

        #develop message or embed or whatever
        #actual thingy:

        #this should be what the bot should say at the end,
   
        #successful return of a table of best options
        return output_list(selection_spreadsheet)

        #failed return
        #exit if statement and no return

    return 'That is not a valid command'
