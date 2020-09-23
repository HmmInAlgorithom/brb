import numpy as np
import pandas as pd
import os

filename = 'BeliefRuleBase_v4.csv'
raw_filepath = os.path.join(os.curdir, filename)

raw_rulebase = pd.read_csv(raw_filepath, sep=';')
counter = 1
antecedents = ['rule_id', 'rule_weight']
deltas = []
test = raw_rulebase.isnull()


# appending the antecedent names to the antecedents list and the antecedent weights to the deltas list
while raw_rulebase.iloc[2, counter] != 'Rule ID':
    if pd.notnull(raw_rulebase.iloc[2, counter]):
        antecedents.append('A_' + raw_rulebase.iloc[2, counter])
        deltas.append('del_' + str(raw_rulebase.iloc[2, counter+1]))
        counter += 2
    else:
        counter += 1

# column id where the consequents start
idx_ruleid = counter

# creating a list with all consequent names
counter += 1
consequents = []
while counter < raw_rulebase.shape[1]:
    if pd.isnull(raw_rulebase.iloc[2, counter]):
        break
    consequents.append('D_' + raw_rulebase.iloc[2, counter])
    counter += 1

#extract belief table from the xlsx file
beliefs = raw_rulebase.iloc[3:, (idx_ruleid + 1):(idx_ruleid + 1 + len(consequents))].dropna(how='all')

num_rules = beliefs.shape[0]

#replace , with . in belief table for python float readability
for col in range(beliefs.shape[1]):
    for idx in range(beliefs.shape[0]):
        value = beliefs.iloc[idx, col]
        if pd.isna(value):
            continue
        elif ',' in value:
            beliefs.iloc[idx, col] = value.replace(',', '.')


# creating the rules dataframe which will be the final .csv
rules = pd.DataFrame(index=range(num_rules), columns=(antecedents + consequents + deltas))

# filling the ruleid column
for num in range(num_rules):
    rules.iloc[num, 0] = num + 1

# iterating through the antecedents to enter referential value in correct row (rule) in rules dataframe
for idx, ant in enumerate(antecedents[2:]):
    col = 0
    while col < idx_ruleid:
        #anti = raw_rulebase.iloc[2, col]
        if raw_rulebase.iloc[2, col] == ant.split('_')[1]:
            x = 1
            while pd.notnull(raw_rulebase.iloc[2+x, col]):
                ref_val = raw_rulebase.iloc[2+x, col]
                print(raw_rulebase.iloc[2+x, col+1], type(raw_rulebase.iloc[2+x, col+1]))
                if pd.isnull(raw_rulebase.iloc[2+x, col+1]):
                    x += 1
                elif isinstance(raw_rulebase.iloc[2+x, col+1], float):
                    ruleid = raw_rulebase.iloc[2+x, col+1]
                    #rules[ant].iloc[int(ruleid) - 1] = ref_val
                    rules.iloc[int(ruleid) - 1, idx + 2] = ref_val
                    break
                elif isinstance(raw_rulebase.iloc[2 + x, col + 1], str):
                    rule_list = raw_rulebase.iloc[2 + x, col + 1].split(',')
                    rule_list = [int(elem) for elem in rule_list]

                    for ruleid in rule_list:
                        rules.iloc[ruleid - 1, idx + 2] = ref_val
                    x += 1

                else:
                    rule_list = raw_rulebase.iloc[2+x, col+1].split(',')
                    rule_list = [int(elem) for elem in rule_list]

                    for ruleid in rule_list:
                        rules.iloc[ruleid - 1, idx + 2] = ref_val
                    '''
                    data = []
                    for idx in range(beliefs.shape[0]):
                        if idx in rule_list:
                            data.append(raw_rulebase.iloc[2 + x, col])
                        else:
                            data.append('')
                        #ii = rules[ant]
                        #iii = ruleid
                        #rules[ant].iloc[int(ruleid)-1] = raw_rulebase.iloc[2 + x, col]
                    rules[ant] = data
                    '''
                    x += 1
        col += 1

for idx in range(beliefs.shape[0]):
    for col in range(beliefs.shape[1]):
        rules.iloc[idx, len(antecedents)+col] = beliefs.iloc[idx, col]

rules.to_csv('rulebase_v4.csv')
print('done.')
print('really done')