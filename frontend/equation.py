import random

class Equation():
    # Function to Generate Equations
    @staticmethod
    def random(mode): 
        num = 2 if mode == "easy" else (3 if mode == "med" else random.choice([4, 5, 6, 7, 8]))
        result = ""
        for i in range(num):
            # Generate random number between 1 and 10
            number = random.randint(1, 10)
            num_gen = f" {number} "
            
            # Generate random operator (+, -, *)
            operator = random.randint(1, 3)
            if operator == 1:
                op_gen = " + "
            elif operator == 2:
                op_gen = " - "
            else:
                op_gen = " * "
            
            # Update the equation
            result += num_gen
            if i < num - 1:  # Avoid adding an operator after the last number
                result += op_gen
        
        return result