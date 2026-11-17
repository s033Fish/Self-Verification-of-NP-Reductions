"""Broken: forgets that an odd total can never be split evenly.
 
total // 2 rounds down, so [1, 2] (total 3) asks for a sub-list summing to 1,
which exists, although [1, 2] has no equal split. Expect wrong_answer_no_to_yes.
"""
 
 
def reduce(instance):
    numbers = instance["numbers"]
    return {"numbers": numbers, "target": sum(numbers) // 2}
 