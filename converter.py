import json
import re
import sys
import functools
from math import gcd

#https://stackoverflow.com/a/51716959/5716012
lcm = lambda a,b : abs(a*b) // gcd(a,b)

def raise_power(base, power):
    for index, item in enumerate(base):
        if type(item) in (int, float):
            base[index] **= power
        else:
            base[index][1] *= power
def multiply_bases(base1, base2):
    #lol
    return base1 + base2
def array2eq(base):
    #get an array like this
    #[2, ["meter",2], [second,-2], [second,3]]
    #and output
    #{
    # "_":2
    # "meter":2
    # "second":1
    # }
    terms ={'_':1}

    for num_or_variable in base:
        if type(num_or_variable) in (int, float):
            terms['_'] *= num_or_variable
        else:
            terms.setdefault(num_or_variable[0],0)
            terms[num_or_variable[0]]+=num_or_variable[1]

    return terms
def get_variables(equation):
    return [variable for variable in equation if variable != '_']
class parse():

    def __init__(self, expr,eat_what='md'):
        self.expr = expr
        self.pos=-1
        self.char=''
        self.result = None
        self.next_()
        if eat_what == 'md':
            self.eat_muliply_divide(1)
        elif eat_what == 'conversion':
            self.eat_expression()

    def next_(self):
        #next character
        # next function can't go back on iterators
        self.pos+=1
        if self.pos < len(self.expr) :
            self.char = self.expr[self.pos]
        else:
            self.pos = len(self.expr)
            self.char=''

    def whitespace(self):
        #skips all whitespace
        while self.char == ' ':
            self.next_()

    def show_error(self, error_message):
        print(error_message)
        print(self.expr)
        print(''.ljust(self.pos)+'^')
        sys.exit(1)

    def eat(self, ch, necessary=0):
        #try to skip a character
        self.whitespace()
        if self.char == ch:
            self.next_()
            return True
        else:
            if necessary:
                self.show_error('Expected {}, found {}'.format(ch, self.char))
            return False

    def eat_word(self, necessary=0):
        #eat alphanumeric substring
        self.whitespace()

        start_pos = self.pos
        while self.char.isalpha():
            self.next_()

        if start_pos == self.pos:
            if necessary:
                self.show_error('Expected alphabetical character')
            return False
        self.result =  self.expr[start_pos:self.pos]
        if necessary:
            return self.result
        else:
            return True
    def eat_word_not_in(self, words, necessary=0):
            #eat alphanumeric substring if it is in words
            self.whitespace()

            start_pos = self.pos
            start_char = self.char

            while self.char.isalpha():
                self.next_()
            word = self.expr[start_pos:self.pos]

            if not word in words and len(word)>0:
                self.result = word
                if necessary:
                    return self.result
                return True
            else:
                self.pos = start_pos
                self.char = start_char
                self.result = ''
                if necessary:
                    self.show_error('Expected a word not in {}'.format(', '.join(words)))

    def eat_known_word(self, words, necessary=0):
        #eat alphanumeric substring if it is in words
        self.whitespace()

        start_pos = self.pos
        start_char = self.char

        while self.char.isalpha():
            self.next_()
        word = self.expr[start_pos:self.pos]
        if word in words:
            self.result = word
            if necessary:
                return self.result
            return True
        else:
            self.pos = start_pos
            self.char = start_char
            self.result = ''
            if necessary:
                self.show_error('Expected a word in {}'.format(', '.join(words)))
            return False

    def number(self,necessary=0):
        #this regex matches a float.
        float_parse = re.compile('[-+]?(\\d+([.]\\d*)?|[.]\\d+)([eE][-+]?\\d+)?')
        
        expr_rest = self.expr[self.pos:]
        match = float_parse.match(expr_rest)
        if match:
            start, end = match.span() 
            float_str = match.string[start:end]
            self.pos+=len(float_str) - 1
            self.next_()
            self.result = float(float_str)
            if necessary:
                return self.result
            return True
        else:
            if necessary:
                self.show_error('Expected a number, found {}'.format(self.char))
            self.result = 1
            return False

        
    def integer(self, necessary = 0):
        #try to match an integer
        float_parse = re.compile('[-+]?\\d+')
        
        expr_rest = self.expr[self.pos:]
        match = float_parse.match(expr_rest)
        if match:
            start, end = match.span() 
            float_str = match.string[start:end]
            self.pos+=len(float_str) - 1
            self.next_()
            self.result = int(float_str)
            if necessary:
                return self.result
            return True
        else:
            if necessary:
                self.show_error('Expected an integer, found {}'.format(self.char))
            self.result =1
            return False
    
    def eat_unit(self,necessary=0):
        #try to eat a unit, word, or a paranthesis
        if self.eat_word_not_in(['as','to']):
            self.result = [[self.result,1]]
        elif self.number():
            self.result = [self.result]
        elif self.eat('('):
            self.eat_muliply_divide(1)
            self.eat(')',1)
        else:
            if necessary:
                self.show_error('Expected a unit')
            return False

        if necessary:
            return self.result
        return True

    def eat_power(self,necessary=0):
        #eat power allows integer powers only
        if self.eat_unit(0):
            base = self.result
            
            power = 1
            if self.eat('^'):
                power = self.integer(1)
            
            raise_power(base, power)
            self.result = base

            if necessary:
                return self.result
            else:
                return True
        else:
            if necessary:
                self.show_error('Expected a unit')
            else:
                return False

    def eat_postfix(self, necessary=0):
        if self.eat_power():
            base = self.result
            total_exponent =1
            while True:
                ate = self.eat_known_word(['square','squared','cube','cubed'])
                if not ate:
                    break
                word = self.result
                total_exponent*= 2 if word in ['square','squared'] else 3
            raise_power(base, total_exponent)
            self.result = base
            if necessary:
                return self.result
            else:
                return True
        else:
            if necessary:
                self.show_error('Expected a unit')
            else:
                return False
    
    def eat_muliply_divide(self, necessary=0):
        if self.eat_postfix():
            left = self.result
            while True:
                if self.eat_known_word(['per','over']) or self.eat('/'):
                    right = self.eat_postfix(1)
                    raise_power(right,-1)
                    left = multiply_bases(left, right)
                elif self.eat_known_word(['times']) or self.eat('*'):
                    right = self.eat_postfix(1)
                    left = multiply_bases(left, right)
                else:
                    #concatenation
                    if self.eat_postfix():
                        right = self.result
                    else:
                        break
                    left = multiply_bases(left, right)
            self.result = left
            if necessary:
                return self.result
            return True
        else:
            if necessary:
                return False
    def eat_expression(self):
        self.whitespace()
        leftpos = self.pos
        left = self.eat_muliply_divide(1)
        left_expr = self.expr[leftpos:self.pos].rstrip()
        self.eat_known_word(['as','to'], 1)
        self.whitespace()
        leftpos = self.pos
        right = self.eat_muliply_divide(1)
        right_expr = self.expr[leftpos:self.pos].rstrip()
        self.result = (left, right, left_expr, right_expr)

#unit group stores dictionaries
#if two names are in the same unit group, they are linear
#to each other.
#i.e meters, centimeters, inches, feet belong to the same unit group
#their ratios can be determined from the ratio of their values
unit_groups=[]

def close_enough(num1, num2):

    #abs(num1) +1 to prevent division by 0
    if abs( (num1-num2)/(abs(num1) +1) ) < 0.01:
        return True
    return False

def groups_with(names):
    return (group for group in unit_groups if any(name in group for name in names))

def group_id():
    #get a new id for object
    _id_ = 0
    while any(group['_id_'] ==_id_ for group in unit_groups):
        _id_+=1
    return _id_

def get_group_by_id(_id_):
    return next(iter(group for group in unit_groups if group['_id_'] == _id_),None)

def add_group(names):
    #if one of the names is in a unit group, all of them are
    
    already_known = next(iter(groups_with(names)), None)
    if already_known:
        names_in_group = [name for name in names if name in already_known]
        for name in names:
            if not name in already_known:
                already_known[name] = already_known[names_in_group[0]]
        return already_known
    else:
        unit_group = {}.fromkeys(names,1)
        unit_group['_id_'] = group_id()
        unit_groups.append(unit_group)
        return unit_group
            
def add_variable_power(eq, ug, value):
    eq.setdefault(ug,0)
    eq[ug]+=value
    if eq[ug] == 0:
        del eq[ug]
equations = []

def raise_group(group, power):
    new_group ={}
    for key in group:
        if key == '_':
            new_group[key] = group[key]**power
        else:
            new_group[key] = group[key]*power
    return new_group

def combine_equations(group1, group2):
    for key in group2:
        if key == '_':
            group1.setdefault('_',1)
            group1['_']*= group2['_']
        else:
            group1.setdefault(key,0)
            group1[key]+=group2[key]
    return group1

def clean_equation(eq):
    cleaned_equation = {}
    for key in eq:
        if  key == '_':
            cleaned_equation[key] = eq[key]
        else:
            val = round(eq[key])
            if not val == 0:
                cleaned_equation[key] = val
    #mutate
    eq.clear()
    eq.update(cleaned_equation)
def eq2group(equation):
    variables = get_variables(equation)
    for variable in variables:
        #put the variable in a group returning the group containing the variable
        var_group = add_group([variable])

        #get the power of the variable in the equation
        power = equation.pop(variable,0)
        #replace variable with unit group containing variable
        add_variable_power(equation,var_group['_id_'],power)
        #multiply the scalar in the equation by the ratio of the variable to it's group
        equation['_']*= var_group[variable]**power
    return equation

with open('conversion_table.txt', 'r') as file:
    for line in file:
        clean_line = line.lstrip().rstrip()
        if not clean_line== '':
            if not clean_line.startswith("#"):
                #get name and value
                name_str, value_str = clean_line.split('=')

                #turn names to array, and the values to an equation
                names = [name.lstrip().rstrip() for name in name_str.split(',')]
                equation = array2eq(parse(value_str).result)

                group = add_group(names)
                
                variables = get_variables(equation)

                for variable in variables:
                    #put the variable in a group returning the group containing the variable
                    var_group = add_group([variable])

                    #get the power of the variable in the equation
                    power = equation.pop(variable,0)
                    #replace variable with unit group containing variable
                    add_variable_power(equation,var_group['_id_'],power)
                    #multiply the scalar in the equation by the ratio of the variable to it's group
                    equation['_']*= var_group[variable]**power
                add_variable_power(equation, group['_id_'], -1)
                equations.append(equation)

def merge_groups(group_1,group_2,ratio,eqs=equations):
    for key, value in group_2.items():
        if key == '_id_':
            continue
        if key in group_1.keys():
            if not close_enough(group_1[key]/value, ratio):
                print(group_1,group_2,key, value, ratio)
                print('contradiction')
        else:
            group_1[key] = value*ratio
    #replace references equations
    for equation in eqs:
        if group_2['_id_'] in equation:
            add_variable_power(equation, group_1['_id_'], equation[group_2['_id_']])
            equation['_']*=  ratio**equation[group_2['_id_']]
            equation.pop(group_2['_id_'])
    unit_groups.remove(group_2)

def reduce_groups():
    #combine groups which have a common member, because linearity is transitive
    for i, group in list(enumerate(unit_groups)):
        groups_with_common_key = [group_other for group_other in unit_groups[i+1:] if any(name in group_other for name in group if not name == '_id_')  ]
        for group_other in groups_with_common_key:
            common_key = [key for key in group if not key == '_id_' and key in group_other]
            
            merge_groups(group, group_other, group[common_key[0]] / group_other[common_key[0]] )
#a**n b**-n s = 1
#(a/b)**n = 1/s
#(a/b) = (1/s)^(1/n) = 1/s^(1/n)
def merge_if_linear(eq):
    variables = get_variables(eq)
    if len(variables) == 2:
        if eq[variables[0]] == -eq[variables[1]]:
            if eq[variables[0]] % 2 == 1:
                ratio =  eq['_']**(1/eq[variables[0]])
                merge_groups(get_group_by_id(variables[0]), get_group_by_id(variables[1]),  ratio)
            else:
                pass

def linear_handle():
    #TODO
    equations[:] = None
    for eq in equations:
        variables = get_variables(eq)
        if len(variables) == 2:
            if eq[variable[0]] == 1 and eq[variable[1]] == -1:
                pass

def remove_redundant_equations():
    
    indices = []
    for index, eq in enumerate(equations):
        if eq['_'] == 0:
            indices.append(index)
            print('found contradiction in table')
            sys.exit(0)
        elif len(get_variables(eq)) == 0:
            indices.append(index)

    #keep track of offset
    #this works because indices_removed is ordered
    indices_removed = 0
    for index_to_remove in indices:
        equations.pop(index_to_remove - indices_removed)
        indices_removed+=1

def equation_handle(equations,src, target, left_expr, right_expr):
    variables  = set()
    src['$'] = -1
    target['$$'] = -1
    eq = equations[:]
    eq.append(src)
    eq.append(target)
    for equation in eq:
        variables.update(get_variables(equation))

    #remove all variables from the equation
    for variable in variables:
        if variable not in ['$','$$']:
            #variable ought to be removed from the equations
            eqs_with_variable = (equ for equ in eq if variable in equ)
            first_eq = next(eqs_with_variable,None)
            if first_eq:
                for equ in eqs_with_variable:
                    if equ[variable] == 0 or first_eq[variable] == 0:
                        print('expected no redundancy')
                    else:
                        power_lcm = lcm(equ[variable], first_eq[variable])
                        equ_power = power_lcm/equ[variable]
                        first_power = - power_lcm/first_eq[variable]
                        new_equ = raise_group(equ, equ_power)
                        new_first = raise_group(first_eq, first_power)
                        
                        new_equation = combine_equations(new_equ, new_first)
                        clean_equation(new_equation)
                        eq[eq.index(equ)] = new_equation
                eq.remove(first_eq)

    if len(eq) > 0:
        for equ in eq:
            clean_equation(equ)
            if equ['$'] == -equ['$$'] and not equ['$'] == 0 and len(get_variables(equ)) == 2:
                conversion_factor = equ['_']**(1/equ['$$'])
                
                conversion_factor = round(conversion_factor*10e5) /10e5
                print('{} = {} {}'.format(left_expr, conversion_factor, right_expr))
                return
    print('Failed to convert: no path found or units are different')

for equation in equations:
    merge_if_linear(equation)
remove_redundant_equations()
reduce_groups()
print('Enter your conversion:')
while True:
    left, right, left_expr, right_expr = parse(input('> '),'conversion').result
    left = eq2group(array2eq(left))
    right = eq2group(array2eq(right))
    equation_handle(equations, left, right,left_expr, right_expr)